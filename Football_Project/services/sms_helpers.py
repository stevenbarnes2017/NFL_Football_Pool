# Football_Project/services/sms_helpers.py
import os, re, requests
from datetime import datetime, timedelta, timezone as dt_tz
from pytz import timezone as pytz_timezone
from sqlalchemy import func
from ..extensions import db
from ..models import Game, User
from zoneinfo import ZoneInfo

MT = pytz_timezone("US/Mountain")

PB_PUSHES_URL      = "https://api.pushbullet.com/v2/pushes"
PB_TEXT_URL  = "https://api.pushbullet.com/v2/texts"
PB_PACKAGE         = "com.pushbullet.android"      # for SMS ephemeral
PB_EPHEMERAL_TYPE  = "push"
PB_PUSH_TYPE       = "messaging_extension_reply"

PHONE_RE = re.compile(r"^[+\d][\d\s\-().]{7,}$")   # quick-and-safe phone check

class PBConfigError(RuntimeError): pass

# add near the existing regexes
E164 = re.compile(r"^\+\d{7,15}$")

def _normalize_to_e164_us(number: str) -> str:
    """Turn 719-555-1212 or (719)555-1212 -> +17195551212; pass through if already +E.164."""
    if not number:
        return number
    s = number.strip()
    if E164.match(s):  # already +E.164
        return s
    digits = re.sub(r"\D", "", s)
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    if len(digits) == 10:
        return f"+1{digits}"
    # fallback (might still fail upstream, but better than raw)
    return f"+{digits}" if digits else s


def _post(url: str, payload: dict):
    resp = requests.post(
        url,
        json=payload,
        headers={"Access-Token": os.environ.get("PUSHBULLET_API_KEY", ""), "Content-Type": "application/json"},
        timeout=15
    )
    # If PB returns 400, show their error text to logs
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise requests.HTTPError(f"{e} | body={resp.text}") from e
    return resp.json() if resp.text else {}

def _send_push_note(title: str, body: str, *, device_iden: str | None = None,
                    channel_tag: str | None = None, email: str | None = None):
    if not os.environ.get("PUSHBULLET_API_KEY"):
        raise PBConfigError("Missing PUSHBULLET_API_KEY")

    payload = {"type": "note", "title": title, "body": body}
    if channel_tag:
        payload["channel_tag"] = channel_tag
    elif device_iden:
        payload["device_iden"] = device_iden
    elif email:
        payload["email"] = email
    else:
        # default to a device if provided
        default_iden = os.environ.get("PUSHBULLET_DEVICE_IDEN")
        if default_iden:
            payload["device_iden"] = default_iden

    return _post(PB_PUSHES_URL, payload)

def _send_carrier_sms_via_pushbullet(phone_e164: str, message: str) -> None:
    """
    Sends a real carrier SMS from YOUR Android phone using Pushbullet's /v2/texts API.
    Requires PUSHBULLET_API_KEY and PUSHBULLET_DEVICE_IDEN in env.
    """
    api_key = os.environ.get("PUSHBULLET_API_KEY")
    device_iden = os.environ.get("PUSHBULLET_DEVICE_IDEN")
    if not api_key:
        raise PBConfigError("Missing PUSHBULLET_API_KEY")
    if not device_iden:
        raise PBConfigError("Missing PUSHBULLET_DEVICE_IDEN (from /v2/devices)")

    payload = {
        "data": {
            "target_device_iden": device_iden,    # your Pixel device iden
            "addresses": [phone_e164],            # must be a list; use +E.164 format
            "message": message
        }
    }

    resp = requests.post(
        "https://api.pushbullet.com/v2/texts",
        json=payload,
        headers={
            "Access-Token": api_key,
            "Content-Type": "application/json"
        },
        timeout=15
    )
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise requests.HTTPError(f"{e} | payload={payload} | body={resp.text}") from e


def send_sms(to_e164: str, text: str, tag: str | None = None) -> dict:
    """
    Backward-compatible name. If `to_e164` looks like a phone number, send via SMS ephemeral.
    Otherwise:
      - "channel:<tag>" => Pushbullet channel note
      - "email:<addr>"  => Pushbullet user by email
      - "<device_iden>" => specific device note
      - ""/None         => default device or channel (if set)
    """
    body  = f"[{tag}] {text}" if tag else text
    title = f"NFL Pool {tag}" if tag else "NFL Pool"

    # 1) Phone number → real SMS via your phone
    if to_e164 and PHONE_RE.match(to_e164.strip()):
        phone = _normalize_to_e164_us(to_e164)
        _send_carrier_sms_via_pushbullet(phone, body)
        return {"status": "ok", "via": "sms_ephemeral"}

    # 2) Channel / email / device note
    channel_tag = None
    device_iden = None
    email       = None

    if to_e164:
        if to_e164.startswith("channel:"):
            channel_tag = to_e164.split(":", 1)[1].strip()
        elif to_e164.startswith("email:"):
            email = to_e164.split(":", 1)[1].strip()
        else:
            device_iden = to_e164.strip()

    if not (channel_tag or device_iden or email):
        env_channel = os.environ.get("PUSHBULLET_CHANNEL_TAG")
        if env_channel:
            channel_tag = env_channel

    _send_push_note(title, body, device_iden=device_iden, channel_tag=channel_tag, email=email)
    return {"status": "ok", "via": "note"}

def sms_week_reminder_job(app, week: int):
    """
    Loop through opted-in users and send a real SMS to each phone number.
    """
    sent = 0
    failed = 0

    with app.app_context():
        targets = (
            db.session.query(User)
            .filter(
                User.sms_opt_in.is_(True),
                User.phone.isnot(None),
                User.phone != ""
            )
            .all()
        )
        app.logger.info("[PUSH] Week %s targets: %s", week, [(u.id, u.username) for u in targets])

        msg = f"Reminder: finish your Week {week} picks before kickoff!"
        for u in targets:
            try:
                # IMPORTANT: pass the PHONE NUMBER here
                send_sms(u.phone, msg, tag=f"week {week}_reminder")
                sent += 1
            except Exception as e:
                failed += 1
                app.logger.exception(f"[PUSH] send failed for user {u.id}: {e}")

        app.logger.info(f"[PUSH] Week {week} reminder finished. sent={sent} failed={failed} targets={len(targets)}")

def schedule_first_kick_sms_for_week(app, week: int, scheduler):
    """
    Schedule a one-time job 2h before first kickoff of 'week'.
    """
    with app.app_context():
        first_dt = (
            db.session.query(func.min(Game.commence_time_mt))
            .filter(Game.week == week)
            .scalar()
        )
        if not first_dt:
            app.logger.info(f"[PUSH] No games found for week {week}; not scheduling.")
            return
        if first_dt.tzinfo is None:
            first_dt = first_dt.replace(tzinfo=ZoneInfo("America/Denver"))

        run_dt_mtn = first_dt.astimezone(MT) - timedelta(hours=2)
        now_mtn = datetime.now(MT)
        job_id = f"sms_first_kick_wk_{week}"

        if run_dt_mtn <= now_mtn:
            try:
                scheduler.remove_job(job_id)
            except Exception:
                pass
            app.logger.info(f"[PUSH] Week {week} reminder window already passed ({run_dt_mtn.isoformat()} MT). Not scheduling.")
            return

        scheduler.add_job(
            func=lambda: sms_week_reminder_job(app, week),
            trigger="date",
            run_date=run_dt_mtn,
            id=job_id,
            replace_existing=True,
        )
        app.logger.info(f"[PUSH] Scheduled week {week} reminder at {run_dt_mtn.isoformat()} MT.")
