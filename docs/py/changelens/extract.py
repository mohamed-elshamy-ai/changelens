"""Turn a file into a list of (location, text) blocks."""
from pathlib import Path

SUPPORTED = (".txt", ".md", ".docx", ".pdf", ".xlsx", ".pptx")


def extract(path):
    """Return (kind, blocks). kind is "text" (ordered paragraphs) or "cells" (keyed by location)."""
    ext = Path(path).suffix.lower()
    if ext in (".txt", ".md"):
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        return "text", [(f"line {i + 1}", ln) for i, ln in enumerate(text.splitlines()) if ln.strip()]
    if ext == ".docx":
        import docx
        d = docx.Document(path)
        out = [(f"paragraph {i + 1}", p.text) for i, p in enumerate(d.paragraphs) if p.text.strip()]
        for ti, t in enumerate(d.tables):
            for ri, row in enumerate(t.rows):
                cells = [c.text.strip() for c in row.cells]
                if any(cells):
                    out.append((f"table {ti + 1} row {ri + 1}", " | ".join(cells)))
        return "text", out
    if ext == ".pptx":
        from pptx import Presentation
        out = []
        for n, slide in enumerate(Presentation(path).slides, 1):
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for para in shape.text_frame.paragraphs:
                        t = "".join(r.text for r in para.runs).strip()
                        if t:
                            out.append((f"slide {n}", t))
                if getattr(shape, "has_table", False) and shape.has_table:
                    for row in shape.table.rows:
                        cells = [c.text.strip() for c in row.cells]
                        if any(cells):
                            out.append((f"slide {n} table", " | ".join(cells)))
            if slide.has_notes_slide:
                for t in slide.notes_slide.notes_text_frame.text.splitlines():
                    if t.strip():
                        out.append((f"slide {n} notes", t.strip()))
        return "text", out
    if ext == ".pdf":
        import pypdfium2 as pdfium
        out = []
        doc = pdfium.PdfDocument(path)
        try:
            for pno in range(len(doc)):
                page = doc[pno]
                tp = page.get_textpage()
                text = tp.get_text_range()
                tp.close()
                page.close()
                # pdfium returns lines, not blocks: join lines into paragraphs,
                # starting a new one after a blank line or a line that ends a sentence.
                para = []
                for line in text.replace("\r", "").split("\n") + [""]:
                    line = " ".join(line.split())
                    if line:
                        para.append(line)
                    if para and (not line or line[-1] in ".!?:;\u061f"):
                        out.append((f"page {pno + 1}", " ".join(para)))
                        para = []
        finally:
            doc.close()
        return "text", out
    if ext == ".xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=False)
        out = []
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    if c.value is not None and str(c.value).strip() != "":
                        out.append((f"{ws.title}!{c.coordinate}", str(c.value)))
        return "cells", out
    raise ValueError(f"Unsupported file type '{ext}'. Supported: {', '.join(SUPPORTED)}")
