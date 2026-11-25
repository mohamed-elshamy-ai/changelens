"""Runs ChangeLens on each sample pair and saves the real output next to the files."""
import io, pathlib, subprocess, sys

root = pathlib.Path(__file__).resolve().parent.parent
pairs = [("contract_v1.docx", "contract_v2.docx", "contract"), ("budget_v1.xlsx", "budget_v2.xlsx", "budget"),
         ("deck_v1.pptx", "deck_v2.pptx", "deck"), ("arabic_v1.txt", "arabic_v2.txt", "arabic")]
for a, b, name in pairs:
    cmd = ["changelens", f"examples/{a}", f"examples/{b}", "--html", f"examples/{name}-report.html"]
    r = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    (root / "examples" / f"{name}-output.txt").write_text("$ " + " ".join(cmd[:3]) + "\n" + r.stdout, encoding="utf-8")
    print(f"{name}: exit {r.returncode}")
