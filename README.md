# ChangeLens

**Someone sent you "the updated version". What actually changed?**

ChangeLens compares two versions of a document and reports each change with a severity (HIGH, MEDIUM, LOW) and a short reason, instead of dumping a raw diff. A "What's Important?" mode hides formatting-only and trivial changes.

Runs offline. No AI model: severity comes from readable rules in [`changelens/rules.py`](changelens/rules.py).

![report](demo/report.png)

## Supported files

`.txt` `.md` `.docx` `.pdf` `.xlsx`. Both files must be the same family (two text documents, or two spreadsheets).

## Install and use

```bash
git clone https://github.com/mohamed-elshamy-ai/changelens
cd changelens
pip install -e .

changelens old.docx new.docx                 # text report
changelens old.pdf new.pdf --important       # What's Important? mode
changelens old.xlsx new.xlsx --json          # for scripts
changelens old.txt new.txt --html report.html
```

Exit code is 1 if any HIGH change is found, 0 otherwise, 3 on read errors.

Real output from [`demo/`](demo/) (more in `demo/demo-output.txt`):

```
[HIGH] Obligation wording changed  (line 1)
    Old: 1. Services. The Contractor shall deliver the website by 1 March 2027.
    New: 1. Services. The Contractor may deliver the website by 1 March 2027.

[HIGH] Number changed  (line 2)
    Old: 2. Payment. The Client shall pay each invoice within 30 days.
    New: 2. Payment. The Client shall pay each invoice within 15 days.

[HIGH] New text added (touches: price, penalty, cancellation)  (line 7)
    New: 7. Cancellation. If the Client cancels, a penalty of 20% of the contract price applies.
```

## How it works

1. **Extract** the text: paragraphs and table rows for Word, text blocks per page for PDF, one entry per cell for Excel.
2. **Align** the two versions. Text is matched block by block with Python's `difflib`; a changed block is paired with its most similar block in the new version. Excel cells are matched by address (for example `Results!D14`).
3. **Judge** each difference with rules:
   - a number, amount or percentage changed (Arabic digits count as the same numbers): HIGH
   - an obligation word changed, such as `shall` to `may`: HIGH
   - a negation was added or removed: HIGH
   - a new or removed clause mentioning payment, penalty, termination, liability and similar words: HIGH or MEDIUM
   - most of a block was rewritten: MEDIUM
   - only case, spacing or punctuation changed: FORMAT (hidden by `--important`)
4. **Report** in the terminal, JSON or a styled HTML page.

### الشرح بالعربي

الأداة بتاخد نسختين من نفس الملف (عقد، Word، PDF، Excel) وبتطلعلك التغييرات الفعلية مش بس فرق نصوص. بتستخرج النص، وبتطابق كل فقرة بالنسخة اللي تقابلها، وبعدين بتحكم على كل فرق بقواعد واضحة: لو رقم اتغير (مثلاً ٣٠ يوم بقت ١٥) أو كلمة التزام اتخففت (يجب/shall بقت يجوز/may) أو اتضافت أو اتشالت كلمة نفي أو بند فيه دفع أو غرامة أو إلغاء، ده بيتصنف HIGH. التغيير في حروف كبيرة وصغيرة أو تنسيق بس بيتصنف FORMAT ويختفي لما تستخدم `--important`. مفيش AI ولا إنترنت.

## Limits

- Severity is a guess from patterns. It can miss an important change and can rate a harmless one HIGH. It is not legal advice. Read the HIGH items yourself.
- Moved paragraphs show up as one removed and one added block.
- PDF comparison relies on extractable text. Scanned PDFs and images (OCR) are not supported yet.
- PowerPoint is not supported yet. Word comparison ignores headers, footers, text boxes and tracked-change markup.
- Excel: only cell values and formulas as text are compared, not formatting, charts or hidden sheets.
- The keyword lists cover English and some Arabic. Other languages only get the number and formatting checks.
- There is no desktop window yet, only the CLI and HTML report.

## Development

```bash
pip install -e ".[dev]" && pytest
```

## Roadmap (not built)

OCR for scanned documents, PowerPoint, desktop window, optional LLM explanation of changes.

## License

MIT
