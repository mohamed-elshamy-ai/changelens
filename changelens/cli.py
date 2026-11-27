import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .compare import compare, Severity
from .report import text_report, html_report


def main(argv=None):
    ap = argparse.ArgumentParser(prog="changelens", description="See which changes between two document versions matter.")
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--important", action="store_true", help="What's Important? mode: hide formatting-only and trivial changes")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--html", metavar="FILE", help="also write a styled HTML report")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    try:
        changes = compare(a.old, a.new, important_only=a.important)
    except (ValueError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 3
    except Exception as e:
        import os
        bad = [p for p in (a.old, a.new) if not os.path.exists(p)]
        empty = [p for p in (a.old, a.new) if os.path.isfile(p) and os.path.getsize(p) == 0]
        if bad: print(f"error: file not found: {', '.join(bad)}", file=sys.stderr)
        elif empty: print(f"error: file is empty: {', '.join(empty)}", file=sys.stderr)
        else: print(f"error: could not read the files. They may be damaged, password protected, or not the type their extension says ({type(e).__name__}: {e})", file=sys.stderr)
        return 3
    name = f"{Path(a.old).name}  ->  {Path(a.new).name}"
    if a.json:
        print(json.dumps([c.to_dict() for c in changes], ensure_ascii=False, indent=2))
    else:
        print(text_report(name, changes, color=sys.stdout.isatty()))
    if a.html:
        Path(a.html).write_text(html_report(name, changes), encoding="utf-8")
    return 1 if any(c.severity == Severity.HIGH for c in changes) else 0


if __name__ == "__main__":
    sys.exit(main())
