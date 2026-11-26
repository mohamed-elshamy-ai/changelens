import html
from .compare import Severity

_COLOR = {Severity.HIGH: "\033[31m", Severity.MEDIUM: "\033[33m", Severity.LOW: "\033[36m", Severity.FORMAT: "\033[90m"}
_HEX = {Severity.HIGH: "#c0392b", Severity.MEDIUM: "#d68910", Severity.LOW: "#2471a3", Severity.FORMAT: "#7f8c8d"}


def _short(s, n=160):
    return s if len(s) <= n else s[: n - 3] + "..."


def text_report(name, changes, color=False):
    lines = ["CHANGE REPORT", "", name, "", f"{len(changes)} change(s) detected", ""]
    for c in changes:
        tag = f"[{c.severity.name}]"
        if color:
            tag = f"{_COLOR[c.severity]}{tag}\033[0m"
        lines.append(f"{tag} {c.title}" + (f"  ({c.location})" if c.location else ""))
        if c.old:
            lines.append(f"    Old: {_short(c.old)}")
        if c.new:
            lines.append(f"    New: {_short(c.new)}")
        lines.append("")
    if not changes:
        lines.append("No differences found.")
    lines.append("Severity is a rule-based guess from patterns, not legal or professional advice.")
    return "\n".join(lines)


def html_report(name, changes):
    rows = []
    for c in changes:
        col = _HEX[c.severity]
        old = f'<div class="old"><b>Old</b> {html.escape(c.old)}</div>' if c.old else ""
        new = f'<div class="new"><b>New</b> {html.escape(c.new)}</div>' if c.new else ""
        rows.append(f'<div class="card" style="border-left-color:{col}"><span class="tag" style="background:{col}">{c.severity.name}</span> '
                    f'<b>{html.escape(c.title)}</b> <span class="loc">{html.escape(c.location)}</span>{old}{new}</div>')
    body = "\n".join(rows) or "<p>No differences found.</p>"
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ChangeLens report</title><style>
body{{font-family:system-ui,sans-serif;max-width:860px;margin:1rem auto;padding:0 .8rem;background:#f6f7f9;color:#222}}
h1{{margin-bottom:0}} .sub{{color:#666;margin-bottom:1.5rem}}
.card{{background:#fff;border-left:6px solid #999;border-radius:6px;padding:.8rem 1rem;margin:.7rem 0;box-shadow:0 1px 3px #0001}}
.tag{{color:#fff;font-size:.75rem;padding:.1rem .5rem;border-radius:10px;margin-right:.5rem}}
.loc{{color:#888;font-size:.85rem;margin-left:.5rem}} .old{{background:#fdecea;margin-top:.5rem;padding:.3rem .5rem;border-radius:4px;overflow-wrap:anywhere}}
.new{{background:#e9f7ef;margin-top:.3rem;padding:.3rem .5rem;border-radius:4px;overflow-wrap:anywhere}} .note{{color:#777;font-size:.8rem;margin-top:2rem}}
</style></head><body><h1>Change report</h1><div class="sub">{html.escape(name)} &middot; {len(changes)} change(s)</div>
{body}<p class="note">Severity is a rule-based guess from patterns, not legal or professional advice.</p></body></html>"""
