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
        )
    except ChallengeValidationError as exc:
        flash(str(exc), "danger")
        return _render_create_form(group, status=400)

    flash(f'Challenge "{challenge.name}" created successfully.', "success")
    return redirect(url_for("main.groups", section="challenges"))
