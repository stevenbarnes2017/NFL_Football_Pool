# app/utils/scoring.py
def norm_status(s: str) -> str:
    s = (s or '').strip().upper()
    if s in {'LIVE', 'IN_PROGRESS', 'STATUS_IN_PROGRESS'}:
        return 'STATUS_IN_PROGRESS'
    if s in {'FINAL', 'COMPLETED', 'COMPLETE', 'STATUS_FINAL'}:
        return 'STATUS_FINAL'
    if s in {'SCHEDULED', 'NOT_STARTED', 'PREGAME', 'STATUS_SCHEDULED'}:
        return 'STATUS_SCHEDULED'
    return s

