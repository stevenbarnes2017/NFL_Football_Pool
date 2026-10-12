# Football_Project/services/recap.py
"""
Weekly recaps.

A recap summarizes one finished week for one group: weekly scores and ranks,
season standings movement, awards, the upset of the week and the crowd record.

The compute_* functions are pure (plain dicts in, plain dicts out) so they can be
unit tested without a database. The load/generate functions read stored picks and
results, then upsert one WeeklyRecap row per group/season/week. Generation is
deterministic, so re-running it for the same week leaves the row unchanged.
"""

from collections import Counter, defaultdict
from datetime import datetime

from ..extensions import db
from ..models import Game, GroupMember, Pick, PoolGroup, User, WeeklyRecap
from .teams import team_abbr, team_nickname


FINAL_STATUSES = {"STATUS_FINAL", "FINAL", "STATUS_GAME_OVER"}
CONTRARIAN_MAX_SHARE = 0.20
RECAP_VERSION = 1


# ----------------------------- pure helpers ----------------------------------

def is_final_status(status: str | None) -> bool:
    return (status or "").strip().upper() in FINAL_STATUSES


def ats_winner(game: dict) -> str | None:
    """
    Team that earns confidence points for this game, mirroring
    utils.calculate_user_scores: against the spread when a spread and favorite
    are stored (a push goes to the underdog), otherwise straight up.
    Returns None when nobody earns points (straight-up tie or missing score).
    """
    home, away = game.get("home_score"), game.get("away_score")
    if home is None or away is None:
        return None

    fav = game.get("favorite_team")
    spread = game.get("spread")
    if spread is None or not fav:
        if home == away:
            return None
        return game["home_team"] if home > away else game["away_team"]

    margin = (home - away) if game["home_team"] == fav else (away - home)
    if margin > abs(spread):
        return fav
    return game["away_team"] if fav == game["home_team"] else game["home_team"]


def underdog(game: dict) -> str | None:
    fav = game.get("favorite_team")
    if game.get("spread") is None or fav not in (game["home_team"], game["away_team"]):
        return None
    return game["away_team"] if fav == game["home_team"] else game["home_team"]


def opponent(game: dict, team: str) -> str:
    return game["away_team"] if team == game["home_team"] else game["home_team"]


def assign_ranks(rows: list[dict], key, field: str = "rank") -> list[dict]:
    """
    Sort rows by key (then username) and assign standard competition ranks
    (1, 1, 3): rows with an equal key share a rank.
    """
    rows.sort(key=lambda r: (key(r), str(r.get("username", "")).lower()))
    prev_key, prev_rank = object(), 0
    for i, r in enumerate(rows, start=1):
        k = key(r)
        if k != prev_key:
            prev_rank, prev_key = i, k
        r[field] = prev_rank
    return rows


def points_left_on_table(week_picks: list[dict]) -> int:
    """
    Best possible score with the same correct picks but confidence ordered
    perfectly (largest values on the correct picks), minus the actual score.
    Uses every confidence value the player had in play that week, including
    values consumed by auto-filled missed picks.
    """
    confidences = sorted(
        (int(p["confidence"]) for p in week_picks if p.get("confidence")),
        reverse=True,
    )
    correct = sum(1 for p in week_picks if (p.get("points_earned") or 0) > 0)
    actual = sum(int(p.get("points_earned") or 0) for p in week_picks)
    return max(0, sum(confidences[:correct]) - actual)


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _fmt_points(n: int) -> str:
    return f"{n} pt" if n == 1 else f"{n} pts"


# ----------------------------- pure compute ----------------------------------

def _weekly_totals(member_ids, picks_by_week, week):
    totals = {uid: {"points": 0, "correct": 0} for uid in member_ids}
    for p in picks_by_week.get(week, []):
        t = totals[p["user_id"]]
        pts = int(p.get("points_earned") or 0)
        t["points"] += pts
        if pts > 0:
            t["correct"] += 1
    return totals


def _season_ranks(members, picks_by_week, through_week, tiebreaker):
    """{user_id: (rank, points, correct)} using the season leaderboard order."""
    totals = {m["user_id"]: {"points": 0, "correct": 0} for m in members}
    member_ids = list(totals)
    for w in picks_by_week:
        if w > through_week:
            continue
        for uid, t in _weekly_totals(member_ids, picks_by_week, w).items():
            totals[uid]["points"] += t["points"]
            totals[uid]["correct"] += t["correct"]

    use_tb = bool(tiebreaker) and tiebreaker.get("week") is not None and tiebreaker["week"] <= through_week
    diffs = (tiebreaker or {}).get("diffs", {})

    rows = [
        {"user_id": m["user_id"], "username": m["username"], **totals[m["user_id"]]}
        for m in members
    ]

    def key(r):
        tb = diffs.get(r["user_id"], float("inf")) if use_tb else 0
        return (-r["points"], -r["correct"], tb)

    assign_ranks(rows, key)
    return {r["user_id"]: (r["rank"], r["points"], r["correct"]) for r in rows}


def _weekly_winner_ids(members, picks_by_week, week):
    totals = _weekly_totals([m["user_id"] for m in members], picks_by_week, week)
    best = max(((t["points"], t["correct"]) for t in totals.values()), default=(0, 0))
    if best[0] <= 0:
        return set()
    return {uid for uid, t in totals.items() if (t["points"], t["correct"]) == best}


def _pick_award(pick, game, username, team_pickers, game_pickers):
    team = pick["team_picked"]
    opp = opponent(game, team)
    share = team_pickers / game_pickers if game_pickers else 0.0
    return {
        "user_id": pick["user_id"],
        "username": username,
        "game_id": game["id"],
        "team": team,
        "team_abbr": team_abbr(team),
        "team_nickname": team_nickname(team),
        "opponent": opp,
        "opponent_abbr": team_abbr(opp),
        "opponent_nickname": team_nickname(opp),
        "confidence": int(pick["confidence"] or 0),
        "points": int(pick.get("points_earned") or 0),
        "team_pickers": team_pickers,
        "game_pickers": game_pickers,
        "share_pct": round(share * 100, 1),
    }


def compute_awards(week_games, week_picks, usernames, rank_changes, week):
    games_by_id = {g["id"]: g for g in week_games}

    team_counts = defaultdict(Counter)
    for p in week_picks:
        if p.get("team_picked"):
            team_counts[p["game_id"]][p["team_picked"]] += 1

    correct, wrong = [], []
    for p in week_picks:
        game = games_by_id.get(p["game_id"])
        if not game or not p.get("team_picked") or not p.get("confidence"):
            continue
        counts = team_counts[p["game_id"]]
        award = _pick_award(
            p, game, usernames[p["user_id"]],
            counts[p["team_picked"]], sum(counts.values()),
        )
        (correct if award["points"] > 0 else wrong).append(award)

    best_call = min(
        correct,
        key=lambda a: (-a["confidence"], a["share_pct"], a["username"].lower(), a["game_id"]),
        default=None,
    )
    worst_miss = min(
        wrong,
        key=lambda a: (-a["confidence"], a["username"].lower(), a["game_id"]),
        default=None,
    )
    contrarian = min(
        (a for a in correct if a["game_pickers"] and a["team_pickers"] / a["game_pickers"] < CONTRARIAN_MAX_SHARE),
        key=lambda a: (-a["confidence"], a["share_pct"], a["username"].lower(), a["game_id"]),
        default=None,
    )

    biggest_mover = None
    if week > 1:
        movers = [r for r in rank_changes if (r.get("rank_change") or 0) > 0]
        top = min(
            movers,
            key=lambda r: (-r["rank_change"], r["season_rank"], r["username"].lower()),
            default=None,
        )
        if top:
            biggest_mover = {
                "user_id": top["user_id"],
                "username": top["username"],
                "from_rank": top["prev_season_rank"],
                "to_rank": top["season_rank"],
                "change": top["rank_change"],
                "from_rank_label": ordinal(top["prev_season_rank"]),
                "to_rank_label": ordinal(top["season_rank"]),
            }

    return {
        "biggest_mover": biggest_mover,
        "best_call": best_call,
        "worst_miss": worst_miss,
        "contrarian": contrarian,
    }


def compute_upset(week_games, week_picks, usernames):
    """Biggest-spread underdog that covered outright (pushes excluded)."""
    candidates = []
    for g in week_games:
        dog = underdog(g)
        if not dog or g.get("home_score") is None or g.get("away_score") is None:
            continue
        fav = g["favorite_team"]
        fav_score = g["home_score"] if fav == g["home_team"] else g["away_score"]
        dog_score = g["away_score"] if fav == g["home_team"] else g["home_score"]
        line = abs(float(g["spread"]))
        fav_margin = fav_score - dog_score
        if fav_margin >= line:
            continue
        candidates.append((-line, -(line - fav_margin), g["id"], g, dog, fav, dog_score, fav_score, line))

    if not candidates:
        return None

    _, _, _, g, dog, fav, dog_score, fav_score, line = min(candidates, key=lambda c: c[:3])
    game_picks = [p for p in week_picks if p["game_id"] == g["id"] and p.get("team_picked")]
    pickers = sorted(
        (usernames[p["user_id"]] for p in game_picks if p["team_picked"] == dog),
        key=str.lower,
    )
    return {
        "game_id": g["id"],
        "underdog": dog,
        "underdog_abbr": team_abbr(dog),
        "underdog_nickname": team_nickname(dog),
        "favorite": fav,
        "favorite_abbr": team_abbr(fav),
        "spread": line,
        "underdog_score": dog_score,
        "favorite_score": fav_score,
        "won_outright": dog_score > fav_score,
        "pickers": pickers,
        "picked_count": len(pickers),
        "game_pickers": len(game_picks),
    }


def compute_crowd(week_games, week_picks):
    """How the pool's majority pick fared in each game, against the spread."""
    counts = defaultdict(Counter)
    for p in week_picks:
        if p.get("team_picked"):
            counts[p["game_id"]][p["team_picked"]] += 1

    games, record = [], {"won": 0, "lost": 0, "push": 0, "split": 0}
    for g in week_games:
        c = counts.get(g["id"])
        if not c:
            continue
        total = sum(c.values())
        ranked = c.most_common()
        team, n = ranked[0]
        if len(ranked) > 1 and ranked[1][1] == n:
            result = "split"
        else:
            winner = ats_winner(g)
            result = "push" if winner is None else ("won" if team == winner else "lost")
        record[result] += 1
        games.append({
            "game_id": g["id"],
            "matchup": f"{team_abbr(g['away_team'])} @ {team_abbr(g['home_team'])}",
            "team": None if result == "split" else team,
            "team_abbr": None if result == "split" else team_abbr(team),
            "pct": round(n / total * 100) if result != "split" else 50,
            "pickers": total,
            "result": result,
        })

    games.sort(key=lambda r: (-r["pct"], r["game_id"]))
    return {**record, "games": games}


def build_headline(week, scores, winner_ids, prior_wins, upset):
    winners = [r for r in scores if r["user_id"] in winner_ids]
    if not winners:
        return f"Week {week} is in the books"

    top = winners[0]["points"]
    if len(winners) == 2:
        return f"{winners[0]['username']} and {winners[1]['username']} share Week {week} with {top}"
    if len(winners) > 2:
        return f"{len(winners)}-way tie atop Week {week} at {top}"

    w = winners[0]
    others = [r["points"] for r in scores if r["user_id"] != w["user_id"]]
    margin = top - max(others) if others else None
    wins_before = prior_wins.get(w["user_id"], 0)

    if upset and w["username"] in upset["pickers"]:
        if wins_before == 0:
            tail = "a first weekly win"
        else:
            tail = f"weekly win No. {wins_before + 1}"
        return f"{w['username']} rides a {upset['underdog_nickname']} upset to {tail}"
    if wins_before == 0:
        return f"{w['username']} grabs a first weekly win with {top}"
    if margin is not None and margin >= 10:
        return f"{w['username']} runs away with Week {week} by {margin}"
    if margin == 0:
        return f"{w['username']} takes Week {week} on correct picks"
    if margin is not None and margin <= 2:
        return f"{w['username']} edges out Week {week} by {_fmt_points(margin)}"
    return f"{w['username']} takes Week {week} with {top}"


def compute_week_recap(*, season_year, season_type, week, games, members, picks, tiebreaker=None):
    """
    games:   dicts for every game in the season with week <= `week`
             (id, week, home_team, away_team, spread, favorite_team,
              home_score, away_score, status, kickoff)
    members: dicts (user_id, username) for the group
    picks:   dicts (user_id, game_id, team_picked, confidence, points_earned)
             for this group, any week <= `week`
    tiebreaker: optional {"week": int, "diffs": {user_id: abs diff}} once the
             season tiebreaker game is final.

    Returns (headline, data) or None when the week has no games or any game
    is not final.
    """
    week_games = sorted(
        (g for g in games if g["week"] == week),
        key=lambda g: (g.get("kickoff") or "", g["id"]),
    )
    if not week_games or not all(is_final_status(g.get("status")) for g in week_games):
        return None

    usernames = {m["user_id"]: m["username"] for m in members}
    week_of_game = {g["id"]: g["week"] for g in games}

    # every week with games gets an entry, even when nobody picked
    picks_by_week = {w: [] for w in set(week_of_game.values())}
    for p in picks:
        if p["user_id"] in usernames and p["game_id"] in week_of_game:
            picks_by_week[week_of_game[p["game_id"]]].append(p)
    week_picks = picks_by_week[week]

    season_now = _season_ranks(members, picks_by_week, week, tiebreaker)
    season_prev = _season_ranks(members, picks_by_week, week - 1, tiebreaker) if week > 1 else {}

    picks_by_user = defaultdict(list)
    for p in week_picks:
        picks_by_user[p["user_id"]].append(p)

    scores = []
    for m in members:
        uid = m["user_id"]
        mine = picks_by_user.get(uid, [])
        s_rank, s_points, _ = season_now[uid]
        prev_rank = season_prev[uid][0] if uid in season_prev else None
        scores.append({
            "user_id": uid,
            "username": m["username"],
            "points": sum(int(p.get("points_earned") or 0) for p in mine),
            "correct": sum(1 for p in mine if (p.get("points_earned") or 0) > 0),
            "picked": sum(1 for p in mine if p.get("team_picked")),
            "left_on_table": points_left_on_table(mine),
            "season_points": s_points,
            "season_rank": s_rank,
            "prev_season_rank": prev_rank,
            "rank_change": (prev_rank - s_rank) if prev_rank is not None else None,
        })
    assign_ranks(scores, lambda r: (-r["points"], -r["correct"]))

    winner_ids = _weekly_winner_ids(members, picks_by_week, week)
    prior_wins = Counter()
    for w in sorted(picks_by_week):
        if w >= week:
            continue
        if all(is_final_status(g.get("status")) for g in games if g["week"] == w):
            prior_wins.update(_weekly_winner_ids(members, picks_by_week, w))

    upset = compute_upset(week_games, week_picks, usernames)
    awards = compute_awards(week_games, week_picks, usernames, scores, week)
    crowd = compute_crowd(week_games, week_picks)
    headline = build_headline(week, scores, winner_ids, prior_wins, upset)[:200]

    winner_rows = [r for r in scores if r["user_id"] in winner_ids]
    runner_up = next((r for r in scores if r["user_id"] not in winner_ids), None)

    data = {
        "version": RECAP_VERSION,
        "season_year": season_year,
        "season_type": season_type,
        "week": week,
        "games_count": len(week_games),
        "participants": len(scores),
        "winner_user_ids": sorted(winner_ids),
        "winning_score": winner_rows[0]["points"] if winner_rows else None,
        "winning_margin": (
            winner_rows[0]["points"] - runner_up["points"] if winner_rows and runner_up else None
        ),
        "scores": scores,
        "awards": awards,
        "upset": upset,
        "crowd": crowd,
    }
    return headline, data


# ----------------------------- database layer --------------------------------

def week_is_final(season_year: int, season_type: str, week: int) -> bool:
    statuses = [
        s for (s,) in db.session.query(Game.status).filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.week == week,
        ).all()
    ]
    return bool(statuses) and all(is_final_status(s) for s in statuses)


def _game_dict(g: Game) -> dict:
    return {
        "id": g.id,
        "week": g.week,
        "home_team": g.home_team,
        "away_team": g.away_team,
        "spread": g.spread,
        "favorite_team": g.favorite_team,
        "home_score": g.home_team_score,
        "away_score": g.away_team_score,
        "status": g.status,
        "kickoff": g.commence_time_mt.isoformat() if g.commence_time_mt else "",
    }


def group_members(group_id: int) -> list[dict]:
    """Active members of a group, as on the leaderboard."""
    rows = (
        db.session.query(User.id, User.username)
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id, GroupMember.is_active.is_(True))
        .order_by(User.id)
        .all()
    )
    return [{"user_id": r.id, "username": r.username} for r in rows]


def load_recap_inputs(group_id: int, season_year: int, season_type: str, week: int) -> dict:
    games = (
        Game.query
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.week.isnot(None),
            Game.week <= week,
        )
        .order_by(Game.id)
        .all()
    )

    picks = (
        db.session.query(
            Pick.user_id, Pick.game_id, Pick.team_picked, Pick.confidence, Pick.points_earned,
        )
        .join(Game, Game.id == Pick.game_id)
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.week <= week,
            Pick.group_id == group_id,
        )
        .order_by(Pick.id)
        .all()
    )

    tiebreaker = None
    tb_game = (
        Game.query
        .filter(
            Game.season_year == season_year,
            Game.season_type == season_type,
            Game.is_tiebreaker.is_(True),
        )
        .first()
    )
    if (
        tb_game
        and is_final_status(tb_game.status)
        and tb_game.home_team_score is not None
        and tb_game.away_team_score is not None
    ):
        actual = tb_game.home_team_score + tb_game.away_team_score
        guesses = (
            db.session.query(Pick.user_id, Pick.tiebreaker_score)
            .filter(
                Pick.game_id == tb_game.id,
                Pick.group_id == group_id,
                Pick.tiebreaker_score.isnot(None),
            )
            .all()
        )
        tiebreaker = {
            "week": tb_game.week,
            "diffs": {uid: abs(guess - actual) for uid, guess in guesses},
        }

    return {
        "season_year": season_year,
        "season_type": season_type,
        "week": week,
        "games": [_game_dict(g) for g in games],
        "members": group_members(group_id),
        "picks": [
            {
                "user_id": p.user_id,
                "game_id": p.game_id,
                "team_picked": p.team_picked,
                "confidence": p.confidence,
                "points_earned": p.points_earned,
            }
            for p in picks
        ],
        "tiebreaker": tiebreaker,
    }


def generate_recap(group_id: int, season_year: int, season_type: str, week: int) -> str:
    """
    Compute and upsert the recap for one group/week. Returns one of
    'created', 'updated', 'unchanged' or 'not_final'. Commits on change.
    """
    result = compute_week_recap(**load_recap_inputs(group_id, season_year, season_type, week))
    if result is None:
        return "not_final"
    headline, data = result

    row = WeeklyRecap.query.filter_by(
        group_id=group_id, season_year=season_year, season_type=season_type, week=week,
    ).first()

    if row is None:
        db.session.add(WeeklyRecap(
            group_id=group_id,
            season_year=season_year,
            season_type=season_type,
            week=week,
            headline=headline,
            data=data,
            generated_at=datetime.utcnow(),
        ))
        status = "created"
    elif row.headline == headline and row.data == data:
        return "unchanged"
    else:
        row.headline = headline
        row.data = data
        row.generated_at = datetime.utcnow()
        status = "updated"

    db.session.commit()
    return status


def season_weeks(season_year: int, season_type: str) -> list[int]:
    return [
        w for (w,) in (
            db.session.query(Game.week)
            .filter(
                Game.season_year == season_year,
                Game.season_type == season_type,
                Game.week.isnot(None),
            )
            .distinct()
            .order_by(Game.week)
            .all()
        )
    ]


def generate_recaps(season_year: int, season_type: str, weeks=None, group_id: int | None = None) -> list[dict]:
    """Generate recaps for the given weeks (default: every week) across active groups."""
    if group_id is not None:
        group_ids = [group_id]
    else:
        group_ids = [g.id for g in PoolGroup.query.filter_by(is_active=True).order_by(PoolGroup.id).all()]

    weeks = season_weeks(season_year, season_type) if weeks is None else list(weeks)

    results = []
    for w in weeks:
        for gid in group_ids:
            try:
                status = generate_recap(gid, season_year, season_type, w)
            except Exception as e:
                db.session.rollback()
                status = f"error: {e}"
            results.append({"group_id": gid, "week": w, "status": status})
    return results


def get_recap(group_id: int, season_year: int, season_type: str, week: int) -> WeeklyRecap | None:
    """Stored recap for a week, only while every game in that week is final."""
    if not week_is_final(season_year, season_type, week):
        return None
    return WeeklyRecap.query.filter_by(
        group_id=group_id, season_year=season_year, season_type=season_type, week=week,
    ).first()


def recap_weeks(group_id: int, season_year: int, season_type: str) -> list[int]:
    """Weeks with a stored recap for this group (ascending)."""
    return [
        w for (w,) in (
            db.session.query(WeeklyRecap.week)
            .filter_by(group_id=group_id, season_year=season_year, season_type=season_type)
            .order_by(WeeklyRecap.week)
            .all()
        )
    ]
