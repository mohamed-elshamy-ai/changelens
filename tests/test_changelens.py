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
