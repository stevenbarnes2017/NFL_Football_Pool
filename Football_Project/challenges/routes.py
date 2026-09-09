from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from Football_Project.models import PoolGroup
from Football_Project.services.challenge_creation_service import (
    ChallengeValidationError,
    create_challenge as create_challenge_record,
    load_eligible_current_week_games,
    load_eligible_group_members,
    validate_active_group_membership,
)
from Football_Project.services.challenge_access_service import (
    build_challenge_detail,
    can_view_challenge,
    get_challenge_for_detail,
)
from Football_Project.services.challenge_pick_service import (
    ChallengePickAuthorizationError,
    ChallengePickValidationError,
    save_challenge_picks,
)
from Football_Project.services.challenge_cancellation_service import (
    ChallengeCancellationError,
    cancel_challenge as cancel_challenge_record,
    can_cancel_challenge,
)
from Football_Project.services.challenge_deletion_service import (
    can_delete_challenge,
    delete_challenge as delete_challenge_record,
)

from . import challenges_bp


def _authorized_group_or_403(group_id):
    try:
        validate_active_group_membership(current_user.id, group_id)
    except ChallengeValidationError:
        abort(403)
    return PoolGroup.query.get_or_404(group_id)


def _render_create_form(group, *, status=200):
    return (
        render_template(
            "create_challenge.html",
            group=group,
            members=load_eligible_group_members(group.id),
            games=load_eligible_current_week_games(),
            form_data=request.form,
            selected_participant_ids=set(request.form.getlist("participant_ids")),
            selected_game_ids=set(request.form.getlist("game_ids")),
        ),
        status,
    )


@challenges_bp.route("/groups/<int:group_id>/challenges/new", methods=["GET"])
@login_required
def new_challenge(group_id):
    group = _authorized_group_or_403(group_id)
    return _render_create_form(group)


@challenges_bp.route("/groups/<int:group_id>/challenges", methods=["POST"])
@login_required
def create_challenge(group_id):
    group = _authorized_group_or_403(group_id)
    try:
        challenge = create_challenge_record(
            group_id=group.id,
            creator_user_id=current_user.id,
            name=request.form.get("name", ""),
            description=request.form.get("description"),
            selected_participant_ids=request.form.getlist("participant_ids"),
            selected_game_ids=request.form.getlist("game_ids"),
            challenge_type=request.form.get("challenge_type", "winner"),
            over_under_lines={
                key.removeprefix("over_under_line_"): value
                for key, value in request.form.items()
                if key.startswith("over_under_line_")
            },
        )
    except ChallengeValidationError as exc:
        flash(str(exc), "danger")
        return _render_create_form(group, status=400)

    flash(f'Challenge "{challenge.name}" created successfully.', "success")
    return redirect(url_for("main.groups", section="challenges"))


@challenges_bp.route("/challenges/<int:challenge_id>", methods=["GET"])
@login_required
def challenge_detail(challenge_id):
    challenge = get_challenge_for_detail(challenge_id)
    if challenge is None:
        abort(404)
    if not can_view_challenge(current_user, challenge):
        abort(403)
    return render_template(
        "challenge_detail.html",
        detail=build_challenge_detail(challenge, user=current_user),
    )


@challenges_bp.route("/challenges/<int:challenge_id>/picks", methods=["POST"])
@login_required
def submit_challenge_picks(challenge_id):
    challenge = get_challenge_for_detail(challenge_id)
    if challenge is None:
        abort(404)

    submitted = []
    for key, value in request.form.items(multi=True):
        if key.startswith("pick_"):
            submitted.append((key.removeprefix("pick_"), value))
    submitted_scores = []
    for key, home_score in request.form.items():
        if key.startswith("home_score_"):
            challenge_game_id = key.removeprefix("home_score_")
            submitted_scores.append((
                challenge_game_id,
                home_score,
                request.form.get(f"away_score_{challenge_game_id}"),
            ))

    try:
        result = save_challenge_picks(
            challenge=challenge,
            user_id=current_user.id,
            submitted_picks=submitted,
            submitted_scores=submitted_scores,
        )
    except ChallengePickAuthorizationError as exc:
        abort(403, description=str(exc))
    except ChallengePickValidationError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("challenges.challenge_detail", challenge_id=challenge.id))

    if result["locked"]:
        flash(
            f'Picks saved. {result["locked"]} locked game(s) were left unchanged.',
            "success",
        )
    else:
        flash("Picks saved successfully.", "success")
    return redirect(url_for("challenges.challenge_detail", challenge_id=challenge.id))


@challenges_bp.route("/challenges/<int:challenge_id>/cancel", methods=["POST"])
@login_required
def cancel_challenge(challenge_id):
    challenge = get_challenge_for_detail(challenge_id)
    if challenge is None:
        abort(404)
    if not can_cancel_challenge(current_user, challenge):
        abort(403)

    try:
        cancel_challenge_record(challenge, current_user)
    except ChallengeCancellationError as exc:
        flash(str(exc), "danger")
        return redirect(
            url_for("challenges.challenge_detail", challenge_id=challenge.id)
        )

    flash(f'Challenge "{challenge.name}" cancelled successfully.', "success")
    return redirect(
        url_for("challenges.challenge_detail", challenge_id=challenge.id)
    )


@challenges_bp.route("/challenges/<int:challenge_id>/delete", methods=["POST"])
@login_required
def delete_challenge(challenge_id):
    challenge = get_challenge_for_detail(challenge_id)
    if challenge is None:
        abort(404)
    if not can_delete_challenge(current_user, challenge):
        abort(403)

    name = challenge.name
    delete_challenge_record(challenge, current_user)
    flash(f'Challenge "{name}" permanently deleted.', "success")
    return redirect(url_for("main.groups", section="challenges"))
