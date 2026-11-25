import openpyxl, docx
from reportlab.pdfgen import canvas
from changelens import compare, Severity
from changelens.cli import main


def write(p, text):
    p.write_text(text, encoding="utf-8")
    return str(p)


OLD = """1. Payment is due within 30 days of the invoice date.
2. The supplier shall deliver the goods in Cairo.
3. This agreement is governed by Egyptian law.
4. Either party may end this agreement with notice."""


def test_number_change_is_high(tmp_path):
    new = OLD.replace("30 days", "15 days")
    ch = compare(write(tmp_path / "a.txt", OLD), write(tmp_path / "b.txt", new))
    assert len(ch) == 1 and ch[0].severity == Severity.HIGH
    assert "number" in ch[0].title.lower() and "30" in ch[0].old and "15" in ch[0].new


def test_added_clause_with_keyword_is_high(tmp_path):
    new = OLD + "\n5. The client must pay a penalty of 5% on cancellation."
    ch = compare(write(tmp_path / "a.txt", OLD), write(tmp_path / "b.txt", new))
    assert ch[0].kind == "added" and ch[0].severity == Severity.HIGH


def test_format_only_hidden_in_important_mode(tmp_path):
    new = OLD.replace("Cairo", "CAIRO")
    a, b = write(tmp_path / "a.txt", OLD), write(tmp_path / "b.txt", new)
    ch = compare(a, b)
    assert ch and ch[0].severity == Severity.FORMAT
    assert compare(a, b, important_only=True) == []


def test_obligation_softened(tmp_path):
    new = OLD.replace("shall deliver", "may deliver")
    ch = compare(write(tmp_path / "a.txt", OLD), write(tmp_path / "b.txt", new))
    assert ch[0].severity == Severity.HIGH and "obligation" in ch[0].title.lower()


def test_negation(tmp_path):
    new = OLD.replace("may end", "may not end")
    ch = compare(write(tmp_path / "a.txt", OLD), write(tmp_path / "b.txt", new))
    assert ch[0].severity == Severity.HIGH and "negation" in ch[0].title.lower()


def test_removed_clause(tmp_path):
    new = "\n".join(OLD.splitlines()[:3])
    ch = compare(write(tmp_path / "a.txt", OLD), write(tmp_path / "b.txt", new))
    assert ch[0].kind == "removed"


def test_arabic_digits_equal_numbers(tmp_path):
    a = write(tmp_path / "a.txt", "الدفع خلال 30 يوم")
    b = write(tmp_path / "b.txt", "الدفع خلال ١٥ يوم")
    ch = compare(a, b)
    assert ch[0].severity == Severity.HIGH


def test_identical(tmp_path):
    a = write(tmp_path / "a.txt", OLD)
    assert compare(a, a) == []


def test_xlsx_cells(tmp_path):
    for name, v in (("a", 100), ("b", 90)):
        wb = openpyxl.Workbook()
        wb.active.title = "Results"
        wb.active["D14"] = v
        wb.active["A1"] = "Accuracy"
        wb.save(tmp_path / f"{name}.xlsx")
    ch = compare(str(tmp_path / "a.xlsx"), str(tmp_path / "b.xlsx"))
    assert ch[0].location == "Results!D14" and ch[0].severity == Severity.HIGH


def test_docx(tmp_path):
    for name, t in (("a", "Payment within 30 days."), ("b", "Payment within 15 days.")):
        d = docx.Document()
        d.add_paragraph(t)
        d.save(tmp_path / f"{name}.docx")
    ch = compare(str(tmp_path / "a.docx"), str(tmp_path / "b.docx"))
    assert ch[0].severity == Severity.HIGH


def test_pdf(tmp_path):
    for name, t in (("a", "Fee is 500 EGP"), ("b", "Fee is 700 EGP")):
        c = canvas.Canvas(str(tmp_path / f"{name}.pdf"))
        c.drawString(72, 700, t)
        c.save()
    ch = compare(str(tmp_path / "a.pdf"), str(tmp_path / "b.pdf"))
    assert ch[0].severity == Severity.HIGH and ch[0].location == "page 1"


def test_cli_and_html(tmp_path, capsys):
    a = write(tmp_path / "a.txt", OLD)
    b = write(tmp_path / "b.txt", OLD.replace("30", "15"))
    rc = main([a, b, "--html", str(tmp_path / "r.html")])
    out = capsys.readouterr().out
    assert rc == 1 and "CHANGE REPORT" in out and "[HIGH]" in out
    assert "Old" in (tmp_path / "r.html").read_text()


def test_mixed_kinds_error(tmp_path):
    import pytest
    wb = openpyxl.Workbook(); wb.save(tmp_path / "a.xlsx")
    with pytest.raises(ValueError):
        compare(str(tmp_path / "a.xlsx"), write(tmp_path / "b.txt", "x"))


def test_unsupported(tmp_path):
    assert main([str(tmp_path / "a.zip"), str(tmp_path / "b.zip")]) == 3


def test_moved_paragraph_is_one_change(tmp_path):
    a = "A. Intro text about the project.\nB. Payment is due within 30 days of the invoice.\nC. Closing remarks and signatures."
    b = "A. Intro text about the project.\nC. Closing remarks and signatures.\nB. Payment is due within 30 days of the invoice."
    ch = compare(write(tmp_path / "a.txt", a), write(tmp_path / "b.txt", b))
    moved = [c for c in ch if c.kind == "moved"]
    assert len(moved) == 1 and not [c for c in ch if c.kind in ("added", "removed")]
    assert moved[0].severity == Severity.LOW


def test_moved_and_edited_keeps_severity(tmp_path):
    a = "Intro.\nPayment is due within 30 days of the invoice date.\nEnd."
    b = "Intro.\nEnd.\nPayment is due within 15 days of the invoice date."
    ch = compare(write(tmp_path / "a.txt", a), write(tmp_path / "b.txt", b))
    mv = [c for c in ch if c.kind == "moved"]
    assert mv and mv[0].severity == Severity.HIGH


def test_pptx(tmp_path):
    from pptx import Presentation
    for name, price in (("a", "30 days"), ("b", "15 days")):
        prs = Presentation()
        s = prs.slides.add_slide(prs.slide_layouts[1])
        s.shapes.title.text = "Terms"
        s.placeholders[1].text = f"Payment within {price}"
        s.notes_slide.notes_text_frame.text = "Speaker note stays"
        prs.save(tmp_path / f"{name}.pptx")
    ch = compare(str(tmp_path / "a.pptx"), str(tmp_path / "b.pptx"))
    assert len(ch) == 1 and ch[0].severity == Severity.HIGH and ch[0].location == "slide 1"


def test_number_words_equal_digits(tmp_path):
    a = write(tmp_path / "a.txt", "The Client may request up to three rounds of revisions.")
    b = write(tmp_path / "b.txt", "The Client may request up to one round of revisions.")
    assert compare(a, b)[0].severity == Severity.HIGH
    c = write(tmp_path / "c.txt", "The Client may request up to 3 rounds of revisions.")
    assert all(x.severity < Severity.HIGH for x in compare(a, c))  # three == 3, only the wording differs


def test_rewritten_clause_is_paired_by_label(tmp_path):
    a = write(tmp_path / "a.txt", "6. Ownership. The Client owns the final website after full payment.")
    b = write(tmp_path / "b.txt", "6. Ownership. The Freelancer keeps all rights until every invoice and late fee is settled.")
    ch = compare(a, b)
    assert len(ch) == 1 and ch[0].kind == "modified"
