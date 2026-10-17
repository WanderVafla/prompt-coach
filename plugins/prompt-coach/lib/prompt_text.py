"""Cleaning of raw prompt text before matching and logging."""

import re

PASTED = re.compile(r"<pasted_content[^>]*>(.*?)</pasted_content[^>]*>", re.S)
PASTED_MARK = re.compile(r"\[pasted \d+ chars: .*?…\]", re.S)  # what `loggable` leaves
OVERRIDE = "#tool"
MAX_LOGGED = 1500
PASTED_PREVIEW = 200

# Messages the harness sends on the user's behalf, and slash commands.
NOISE_PREFIXES = ("<task-notification", "<command-", "<local-command", "[Request interrupted",
                  "Caveat:", "This session is being continued", "/")


def is_noise(text: str) -> bool:
    stripped = text.strip()
    return not stripped or stripped.startswith(NOISE_PREFIXES)


def is_override(text: str) -> bool:
    return text.lstrip().lower().startswith(OVERRIDE)


def own_text(text: str) -> str:
    """The user's own words, without pasted blocks (raw or already logged)."""
    return PASTED_MARK.sub(" ", PASTED.sub(" ", text)).strip()


def loggable(text: str) -> str:
    """Own words kept, each pasted block shortened to a preview."""
    def preview(match: re.Match) -> str:
        body = match.group(1).strip()
        short = body[:PASTED_PREVIEW].replace("\n", " ")
        return f"[pasted {len(body)} chars: {short}…]"

    return PASTED.sub(preview, text).strip()[:MAX_LOGGED]
