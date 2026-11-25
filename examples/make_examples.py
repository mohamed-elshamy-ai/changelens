"""Builds the sample files in this folder. Run: python examples/make_examples.py"""
import pathlib
import docx, openpyxl
from pptx import Presentation

here = pathlib.Path(__file__).parent

V1 = [
 "Freelance Services Agreement",
 "1. Scope. The Freelancer shall design and build a five-page website with a contact form.",
 "2. Delivery. The Freelancer shall deliver the final website by 1 March 2027.",
 "3. Fees. The Client shall pay a total fee of EGP 20,000, split into two equal payments.",
 "4. Payment terms. Each invoice is due within 30 days of the invoice date.",
 "5. Revisions. The Client may request up to three rounds of revisions at no extra cost.",
 "6. Ownership. The Client owns the final website after full payment.",
 "7. Confidentiality. Both parties shall keep project information confidential.",
 "8. Governing law. This agreement is governed by Egyptian law.",
]
V2 = [
 "Freelance Services Agreement",
 "1. Scope. The Freelancer shall design and build a five-page website with a contact form.",
 "2. Delivery. The Freelancer shall deliver the final website by 1 March 2027.",
 "3. Fees. The Client shall pay a total fee of EGP 20,000, split into two equal payments.",
 "4. Payment terms. Each invoice is due within 15 days of the invoice date.",
 "5. Revisions. The Client may request up to one round of revisions at no extra cost.",
 "7. Confidentiality. Both parties shall keep project information confidential.",
 "6. Ownership. The Freelancer owns the final website until the Client has paid all invoices and any late fees.",
 "8. Governing law. This agreement is governed by Egyptian law.",
 "9. Cancellation. If the Client cancels after work has started, a penalty of 30% of the total fee applies.",
]
for name, lines in (("contract_v1.docx", V1), ("contract_v2.docx", V2)):
    d = docx.Document()
    d.add_heading(lines[0], 1)
    for l in lines[1:]:
        d.add_paragraph(l)
    d.save(here / name)

for name, rent, total in (("budget_v1.xlsx", 4000, 5700), ("budget_v2.xlsx", 5200, 7500)):
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Budget"
    ws.append(["Item", "Monthly cost (EGP)"]); ws.append(["Rent", rent]); ws.append(["Internet", 450]); ws.append(["Software", 1250])
    ws.append(["Total", total])
    if name.endswith("v2.xlsx"):
        ws.append(["Insurance", 600])
    wb.save(here / name)

for name, price, extra in (("deck_v1.pptx", "EGP 20,000", False), ("deck_v2.pptx", "EGP 26,000", True)):
    prs = Presentation()
    s = prs.slides.add_slide(prs.slide_layouts[1]); s.shapes.title.text = "Project proposal"
    s.placeholders[1].text = f"Total price: {price}\nDelivery in 6 weeks"
    s.notes_slide.notes_text_frame.text = "Warranty is not included" if extra else "Mention the warranty period"
    prs.save(here / name)

(here / "arabic_v1.txt").write_text("يجب على العميل سداد الفاتورة خلال 30 يوم.\nيجوز لأي طرف إنهاء العقد بإخطار كتابي.\n", encoding="utf-8")
(here / "arabic_v2.txt").write_text("يجب على العميل سداد الفاتورة خلال ١٥ يوم.\nيجوز لأي طرف إنهاء العقد بإخطار كتابي.\nتطبق غرامة ٢٠٪ عند الإلغاء.\n", encoding="utf-8")
