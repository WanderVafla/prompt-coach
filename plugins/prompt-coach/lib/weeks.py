"""ISO week ids like `2026-W42`."""

from datetime import date, datetime, timedelta


def week_id(day: date) -> str:
    year, week, _ = day.isocalendar()
    return f"{year}-W{week:02d}"


def current() -> str:
    return week_id(date.today())


def last_completed() -> str:
    return week_id(date.today() - timedelta(days=7))


def bounds(week: str) -> tuple[date, date]:
    """Monday and Sunday of the week."""
    monday = datetime.strptime(f"{week}-1", "%G-W%V-%u").date()
    return monday, monday + timedelta(days=6)


def of_timestamp(ts: str) -> str:
    """Week of an ISO timestamp, in local time."""
    moment = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return week_id(moment.astimezone().date())
