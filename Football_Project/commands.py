# Football_Project/commands.py
"""Flask CLI commands (`flask --app wsgi recaps ...`)."""

import click
from flask.cli import AppGroup

from .models import Settings
from .services.recap import generate_recaps


recaps_cli = AppGroup("recaps", help="Generate weekly recaps.")


def _season_defaults(season_year, season_type):
    settings = Settings.query.first()
    if season_year is None:
        if not settings:
            raise click.UsageError("No Settings row; pass --season-year.")
        season_year = settings.season_year
    if season_type is None:
        season_type = settings.season_type if settings else "REG"
    return season_year, season_type


def _report(results):
    counts = {}
    for r in results:
        click.echo(f"group={r['group_id']} week={r['week']}: {r['status']}")
        key = r["status"] if not r["status"].startswith("error") else "error"
        counts[key] = counts.get(key, 0) + 1
    click.echo("summary: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    if counts.get("error"):
        raise SystemExit(1)


_season_options = [
    click.option("--season-year", type=int, default=None, help="Defaults to Settings.season_year."),
    click.option("--season-type", type=str, default=None, help="PRE/REG/POST. Defaults to Settings.season_type."),
    click.option("--group-id", type=int, default=None, help="Only this group (default: all active groups)."),
]


def _with_season_options(f):
    for option in reversed(_season_options):
        f = option(f)
    return f


@recaps_cli.command("generate")
@click.option("--week", type=int, required=True)
@_with_season_options
def generate_week(week, season_year, season_type, group_id):
    """Generate (or refresh) recaps for one week."""
    season_year, season_type = _season_defaults(season_year, season_type)
    _report(generate_recaps(season_year, season_type, weeks=[week], group_id=group_id))


@recaps_cli.command("generate-all")
@_with_season_options
def generate_all(season_year, season_type, group_id):
    """Generate (or refresh) recaps for every week of a season."""
    season_year, season_type = _season_defaults(season_year, season_type)
    _report(generate_recaps(season_year, season_type, group_id=group_id))
