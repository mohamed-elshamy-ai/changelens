# ChangeLens: technical notes

**Modules**
- `extract.py`: turns a file into blocks `(location, text)`. Word: paragraphs and table rows (python-docx). PDF: text per page (pypdfium2), lines joined into paragraphs. PowerPoint: shape text, tables, speaker notes per slide (python-pptx). Excel: one block per cell, keyed by address (openpyxl). Returns kind `text` (ordered) or `cells` (keyed).
- `compare.py`: alignment and judging.
- `rules.py`: word lists (English and Arabic), obligation strength table, number extraction (digits, Arabic digits, number words).
- `report.py`: terminal and HTML output. `cli.py`: command line.

**Algorithm**
1. Ordered documents: `difflib.SequenceMatcher` over normalised blocks gives equal, replace, delete, insert regions.
2. Inside a replaced region each old block is paired with the most similar new block (similarity of at least 0.5), or with the block that has the same clause label such as "6. Ownership".
3. A second pass merges a removed block and an added block into a "moved" change when they are at least 85% similar or share a clause label.
4. Each pair is judged by `_judge_modified`: compare the numbers in both blocks, the strength of obligation words (`shall` > `may`), the count of negations, key legal and money words in the changed tokens, and how much of the block was rewritten. Case, spacing or punctuation only is `FORMAT`.
5. Added or removed blocks are judged by the key words and numbers they contain.
6. Spreadsheets are compared by cell address, not by order.

**Design decisions**
- Rules, not an AI model: results are repeatable, explainable and work offline. Every severity comes with a reason string.
- Severity is deliberately cautious about numbers and obligations, because those are the changes that cost people money.
- The same core is loaded unchanged in the browser demo through Pyodide.

**Testing** (19 tests, `pytest`): each rule on small inputs, all five file types built on the fly, moves, number words, Arabic digits, CLI exit codes and HTML output, and the real sample files in `examples/` (outputs are saved next to them).

**Limits**: see the README. In short: severity is a guess, no OCR, PowerPoint images and charts are ignored, a moved and heavily rewritten paragraph without a label can show as removed plus added.
