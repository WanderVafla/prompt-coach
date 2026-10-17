"""SessionStart hook: save the options for skill scripts, and remind the user
when last week has prompts but no review yet."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import options, paths, reviews, weeks  # noqa: E402


def main() -> None:
    data = paths.data_dir()
    opts = options.from_env()
    options.save_snapshot(data, opts)
    opts = options.load(data)

    folder = options.reviews_dir(opts)
    week = weeks.last_completed()
    if folder is None or not paths.log_file(data, week).exists():
        return
    if reviews.note_path(folder, week, opts["author"]).exists():
        return
    print(json.dumps({"systemMessage": f"📊 prompt-coach: no review for {week} yet. Run /prompt-coach:review-prompts"}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"prompt-coach: {error}", file=sys.stderr)
