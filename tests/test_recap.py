import unittest

from flask import Flask

from Football_Project.extensions import db
from Football_Project.models import Game, GroupMember, Pick, PoolGroup, User, WeeklyRecap
from Football_Project.services.recap import (
    assign_ranks,
    ats_winner,
    compute_crowd,
    compute_upset,
    compute_week_recap,
    generate_recap,
    generate_recaps,
    get_recap,
    headline_story,
    points_left_on_table,
)


def game(gid, week=1, home="Home", away="Away", hs=20, as_=10, spread=-3.0, fav="Home", status="STATUS_FINAL"):
    return {
        "id": gid, "week": week, "home_team": home, "away_team": away,
        "spread": spread, "favorite_team": fav, "home_score": hs, "away_score": as_,
        "status": status, "kickoff": f"2026-09-1{week}T17:00:{gid:02d}",
    }


def pick(uid, gid, team, conf, pts):
    return {"user_id": uid, "game_id": gid, "team_picked": team, "confidence": conf, "points_earned": pts}


MEMBERS = [
    {"user_id": 1, "username": "alice"},
    {"user_id": 2, "username": "bob"},
    {"user_id": 3, "username": "cara"},
    {"user_id": 4, "username": "dan"},
    {"user_id": 5, "username": "nopicks"},
]


class AtsWinnerTests(unittest.TestCase):
    def test_favorite_covers(self):
        self.assertEqual(ats_winner(game(1, hs=24, as_=17, spread=-3.5)), "Home")

    def test_favorite_wins_but_does_not_cover(self):
        self.assertEqual(ats_winner(game(1, hs=20, as_=17, spread=-3.5)), "Away")

    def test_push_goes_to_underdog_like_scoring(self):
        self.assertEqual(ats_winner(game(1, hs=20, as_=17, spread=-3.0)), "Away")

    def test_no_spread_is_straight_up(self):
        self.assertEqual(ats_winner(game(1, hs=10, as_=17, spread=None, fav=None)), "Away")
        self.assertIsNone(ats_winner(game(1, hs=17, as_=17, spread=None, fav=None)))


class RankTests(unittest.TestCase):
    def test_equal_keys_share_rank_with_gaps(self):
        rows = [
            {"username": "a", "points": 10},
            {"username": "b", "points": 12},
            {"username": "c", "points": 10},
            {"username": "d", "points": 5},
        ]
        assign_ranks(rows, lambda r: -r["points"])
        self.assertEqual([(r["username"], r["rank"]) for r in rows],
                         [("b", 1), ("a", 2), ("c", 2), ("d", 4)])


class PointsLeftOnTableTests(unittest.TestCase):
    def test_perfect_ordering_leaves_nothing(self):
        picks = [pick(1, 1, "x", 3, 3), pick(1, 2, "x", 2, 2), pick(1, 3, "x", 1, 0)]
        self.assertEqual(points_left_on_table(picks), 0)

    def test_misordered_confidence(self):
        # correct on the 1 and 2, wrong on the 3: best is 3+2=5, actual 3
        picks = [pick(1, 1, "x", 3, 0), pick(1, 2, "x", 2, 2), pick(1, 3, "x", 1, 1)]
        self.assertEqual(points_left_on_table(picks), 2)

    def test_no_picks(self):
        self.assertEqual(points_left_on_table([]), 0)


class UpsetAndCrowdTests(unittest.TestCase):
    def test_biggest_covering_underdog(self):
        games = [
            game(1, hs=20, as_=24, spread=-3.0),            # dog wins, line 3
            game(2, hs=27, as_=21, spread=-7.5),            # fav by 6 < 7.5: dog covers, line 7.5
            game(3, hs=30, as_=10, spread=-10.0),           # fav covers
            game(4, hs=24, as_=14, spread=-10.0),           # push at 10: not an upset
        ]
        picks = [pick(1, 2, "Away", 5, 5), pick(2, 2, "Home", 4, 0), pick(3, 2, "Home", 3, 0)]
        upset = compute_upset(games, picks, {1: "alice", 2: "bob", 3: "cara"})
        self.assertEqual(upset["game_id"], 2)
        self.assertEqual(upset["spread"], 7.5)
        self.assertFalse(upset["won_outright"])
        self.assertEqual(upset["pickers"], ["alice"])
        self.assertEqual((upset["picked_count"], upset["game_pickers"]), (1, 3))

    def test_no_upset_when_every_favorite_covers(self):
        self.assertIsNone(compute_upset([game(1, hs=30, as_=10)], [], {}))

    def test_crowd_record(self):
        games = [game(1, hs=30, as_=10), game(2, hs=20, as_=19), game(3, hs=14, as_=10)]
        picks = [
            pick(1, 1, "Home", 3, 3), pick(2, 1, "Home", 2, 2), pick(3, 1, "Away", 1, 0),
            pick(1, 2, "Home", 2, 0), pick(2, 2, "Home", 3, 0),
            pick(1, 3, "Home", 1, 1), pick(2, 3, "Away", 1, 0),
        ]
        crowd = compute_crowd(games, picks)
        self.assertEqual((crowd["won"], crowd["lost"], crowd["split"]), (1, 1, 1))
        by_game = {g["game_id"]: g for g in crowd["games"]}
        self.assertEqual(by_game[1]["pct"], 67)
        self.assertEqual(by_game[2]["result"], "lost")
        self.assertEqual(by_game[3]["result"], "split")


class ComputeWeekRecapTests(unittest.TestCase):
    def setUp(self):
        # Week 1: game 1 favorite covers, game 2 underdog (Away, +7.5) covers.
        # Week 2: game 3 favorite covers.
        self.games = [
            game(1, week=1, hs=30, as_=10, spread=-3.0),
            game(2, week=1, hs=21, as_=24, spread=-7.5, home="Detroit Lions", away="Chicago Bears", fav="Detroit Lions"),
            game(3, week=2, hs=28, as_=10, spread=-3.0),
        ]
        # 10 pickers on game 2 so 1 Bears picker = 10% (< 20% contrarian threshold)
        self.members = MEMBERS + [{"user_id": i, "username": f"u{i}"} for i in range(6, 12)]
        self.picks = [
            pick(1, 1, "Home", 1, 1), pick(1, 2, "Chicago Bears", 2, 2),   # alice 3
            pick(2, 1, "Home", 2, 2), pick(2, 2, "Detroit Lions", 1, 0),   # bob 2
            pick(3, 1, "Away", 2, 0), pick(3, 2, "Detroit Lions", 1, 0),   # cara 0
            pick(4, 1, None, 2, 0), pick(4, 2, "Detroit Lions", 1, 0),     # dan missed game 1
        ] + [pick(i, 2, "Detroit Lions", 1, 0) for i in range(6, 12)] + [
            pick(3, 3, "Home", 3, 3),                                      # week 2: cara 3
        ]

    def recap(self, week, **kw):
        return compute_week_recap(
            season_year=2026, season_type="REG", week=week,
            games=[g for g in self.games if g["week"] <= week],
            members=self.members, picks=self.picks, **kw,
        )

    def test_not_final_week_has_no_recap(self):
        self.games[2]["status"] = "STATUS_SCHEDULED"
        self.assertIsNone(self.recap(2))

    def test_week_without_games_has_no_recap(self):
        self.assertIsNone(self.recap(3))

    def test_week_one_scores_awards_and_headline(self):
        headline, data = self.recap(1)
        scores = {r["username"]: r for r in data["scores"]}

        self.assertEqual(len(data["scores"]), len(self.members))
        self.assertEqual(scores["nopicks"]["points"], 0)
        self.assertEqual(scores["alice"]["rank"], 1)
        self.assertEqual(scores["bob"]["rank"], 2)
        self.assertEqual(scores["alice"]["rank_change"], None)
        self.assertIsNone(data["awards"]["biggest_mover"])

        self.assertEqual(data["awards"]["best_call"]["username"], "alice")
        self.assertEqual(data["awards"]["best_call"]["confidence"], 2)
        self.assertEqual(data["awards"]["worst_miss"]["username"], "cara")
        self.assertEqual(data["awards"]["contrarian"]["team"], "Chicago Bears")
        self.assertEqual(data["awards"]["contrarian"]["share_pct"], 10.0)

        self.assertEqual(data["upset"]["underdog"], "Chicago Bears")
        self.assertIn("alice", headline)
        self.assertIn("Bears", headline)
        self.assertIn("first weekly win", headline)

    def test_missed_pick_is_not_worst_miss(self):
        _, data = self.recap(1)
        self.assertNotEqual(data["awards"]["worst_miss"]["username"], "dan")

    def test_ties_share_weekly_rank(self):
        _, data = self.recap(1)
        zero_rows = [r for r in data["scores"] if r["points"] == 0]
        self.assertEqual({r["rank"] for r in zero_rows}, {3})

    def test_week_two_biggest_mover(self):
        _, data = self.recap(2)
        mover = data["awards"]["biggest_mover"]
        self.assertEqual(mover["username"], "cara")
        self.assertEqual((mover["from_rank"], mover["to_rank"]), (3, 2))

    def test_deterministic(self):
        self.assertEqual(self.recap(2), self.recap(2))


def score_row(uid, name, points, correct=5, season_rank=None, prev_season_rank=None):
    return {"user_id": uid, "username": name, "points": points, "correct": correct,
            "season_rank": season_rank, "prev_season_rank": prev_season_rank}


class HeadlineStoryTests(unittest.TestCase):
    def setUp(self):
        self.scores = [score_row(1, "alice", 60, season_rank=3, prev_season_rank=3),
                       score_row(2, "bob", 55), score_row(3, "cara", 40)]

    def story(self, week=5, winner_ids=frozenset({1}), prior_wins=None, upset=None, **facts):
        return headline_story(week, self.scores, set(winner_ids), {1: 1} if prior_wins is None else prior_wins, upset, **facts)

    def test_no_winner(self):
        self.assertEqual(self.story(winner_ids=set()), ("no_winner", "Week 5 is in the books"))

    def test_two_way_tie(self):
        kind, text = self.story(winner_ids={1, 2})
        self.assertEqual(kind, "tie")
        self.assertIn("alice", text)
        self.assertIn("bob", text)

    def test_season_high_beats_other_stories(self):
        upset = {"underdog_nickname": "Bears", "pickers": ["alice"], "picked_count": 1, "game_pickers": 3}
        kind, text = self.story(prior_best=58, upset=upset, streak=2)
        self.assertEqual(kind, "season_high")
        self.assertIn("60", text)

    def test_season_high_needs_history(self):
        kind, _ = self.story(week=2, prior_best=58)
        self.assertNotEqual(kind, "season_high")

    def test_not_a_season_high_when_tied_or_below(self):
        kind, _ = self.story(prior_best=60)
        self.assertNotEqual(kind, "season_high")

    def test_upset_counts_win_number(self):
        upset = {"underdog_nickname": "Bears", "pickers": ["alice"], "won_outright": True,
                 "picked_count": 1, "game_pickers": 3}
        kind, text = self.story(upset=upset, prior_wins={1: 2})
        self.assertEqual(kind, "upset")
        self.assertIn("No. 3", text)

    def test_upset_needs_outright_win_most_of_the_pool_missed(self):
        upset = {"underdog_nickname": "Bears", "pickers": ["alice"], "won_outright": True,
                 "picked_count": 2, "game_pickers": 3}
        self.assertNotEqual(self.story(upset=upset)[0], "upset")
        upset.update(picked_count=1, won_outright=False)
        self.assertNotEqual(self.story(upset=upset)[0], "upset")

    def test_back_to_back_and_longer_streaks(self):
        self.assertEqual(self.story(streak=1)[0], "streak")
        kind, text = self.story(streak=3)
        self.assertEqual(kind, "streak")
        self.assertIn("4", text)

    def test_takes_over_first_place(self):
        self.scores[0].update(season_rank=1, prev_season_rank=4)
        kind, text = self.story()
        self.assertEqual(kind, "takes_lead")
        self.assertIn("alice", text)

    def test_contrarian_only_for_the_winner(self):
        lone = {"user_id": 1, "team_nickname": "Cardinals", "team_pickers": 1}
        kind, text = self.story(awards={"contrarian": lone})
        self.assertEqual(kind, "contrarian")
        self.assertIn("Cardinals", text)
        other = dict(lone, user_id=2)
        self.assertNotEqual(self.story(awards={"contrarian": other})[0], "contrarian")

    def test_first_win_mentions_how_it_was_won(self):
        kind, text = self.story(prior_wins={})
        self.assertEqual(kind, "first_win")
        self.scores[1]["points"] = 59
        self.assertIn("1 pt", self.story(prior_wins={})[1])
        self.scores[1]["points"] = 40
        self.assertIn("20", self.story(prior_wins={})[1])

    def test_blowout_and_photo_finishes(self):
        self.scores[1]["points"] = 45
        self.assertEqual(self.story()[0], "blowout")
        self.scores[1]["points"] = 60
        self.assertEqual(self.story()[0], "photo_finish")
        self.scores[1]["points"] = 59
        kind, text = self.story()
        self.assertEqual(kind, "photo_finish")
        self.assertIn("1 pt", text)

    def test_rough_week_for_the_crowd(self):
        kind, text = self.story(crowd={"won": 4, "lost": 9})
        self.assertEqual(kind, "rough_week")

    def test_milestone_then_plain_win(self):
        self.assertEqual(self.story(prior_wins={1: 2})[0], "milestone")
        self.assertEqual(self.story(prior_wins={1: 1})[0], "win")

    def test_wording_is_stable_but_varies_by_week(self):
        self.assertEqual(self.story(), self.story())
        texts = {self.story(week=w)[1].replace(f"Week {w}", "Week N") for w in range(1, 19)}
        self.assertGreater(len(texts), 1)


class GenerateRecapDbTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask("recap-tests")
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        db.init_app(self.app)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        users = [User(username=n, password="x") for n in ("alice", "bob", "nopicks")]
        db.session.add_all(users)
        group = PoolGroup(name="G", slug="g")
        other = PoolGroup(name="Other", slug="other")
        db.session.add_all([group, other])
        db.session.flush()
        for u in users:
            db.session.add(GroupMember(user_id=u.id, group_id=group.id))
        g1 = Game(game_id="e1", season_year=2026, season_type="REG", week=1,
                  home_team="Home", away_team="Away", spread=-3.0, favorite_team="Home",
                  home_team_score=30, away_team_score=10, status="STATUS_FINAL")
        g2 = Game(game_id="e2", season_year=2026, season_type="REG", week=2,
                  home_team="Home", away_team="Away", spread=-3.0, favorite_team="Home",
                  status="STATUS_SCHEDULED")
        db.session.add_all([g1, g2])
        db.session.flush()
        db.session.add_all([
            Pick(user_id=users[0].id, game_id=g1.id, week=1, team_picked="Home", confidence=1,
                 points_earned=1, group_id=group.id),
            Pick(user_id=users[1].id, game_id=g1.id, week=1, team_picked="Away", confidence=1,
                 points_earned=0, group_id=group.id),
        ])
        db.session.commit()
        self.group_id, self.other_id = group.id, other.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_generate_is_idempotent(self):
        self.assertEqual(generate_recap(self.group_id, 2026, "REG", 1), "created")
        self.assertEqual(generate_recap(self.group_id, 2026, "REG", 1), "unchanged")
        self.assertEqual(WeeklyRecap.query.count(), 1)

    def test_not_final_week_is_skipped(self):
        self.assertEqual(generate_recap(self.group_id, 2026, "REG", 2), "not_final")
        self.assertIsNone(get_recap(self.group_id, 2026, "REG", 2))

    def test_generate_all_and_group_scoping(self):
        results = generate_recaps(2026, "REG")
        statuses = {(r["group_id"], r["week"]): r["status"] for r in results}
        self.assertEqual(statuses[(self.group_id, 1)], "created")
        self.assertEqual(statuses[(self.group_id, 2)], "not_final")

        mine = get_recap(self.group_id, 2026, "REG", 1)
        theirs = get_recap(self.other_id, 2026, "REG", 1)
        self.assertEqual(len(mine.data["scores"]), 3)
        self.assertEqual(theirs.data["scores"], [])
        self.assertEqual(mine.data["scores"][0]["username"], "alice")


if __name__ == "__main__":
    unittest.main()
