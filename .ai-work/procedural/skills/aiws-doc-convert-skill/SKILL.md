---
name: aiws-doc-convert-skill
description: >
  Convert / extract / ingest any document into AI-readable Markdown. Use this skill
  whenever the user wants to turn a file — PDF, Excel (xlsx/xls), PowerPoint (pptx/ppt),
  Word (docx/doc), images (png/jpg/tiff/bmp/gif/webp), drawio, svg, csv/txt/md/html/json/
  xml/yaml/eml — into Markdown for AI / RAG / LLM processing. Trigger even if the user
  just says "convert this file", "extract content", "ingest these docs", "turn this into
  markdown", "read this document for AI", or mentions xberg or docling.
  Extraction ONLY (input → Markdown); this skill does not reconstruct Markdown back into
  styled Office files.
user-invocable: true
---

# SKILL: aiws-doc-convert-skill

## Purpose
Ingest documents into structured, AI-readable Markdown — one command, any file type.
Meaning that lives in visuals (colored cells, borders, flowcharts, screenshots, logos)
is preserved: each unit (sheet/slide/page) gets a linked image render + its faithful
extracted text + a summary, and diagrams become Mermaid.

**Two engines** (user picks once, on first use):
- **xberg** *(recommended)* — Rust core (kreuzberg), fast, local, ~33 MB, no ML model
  download, all file types. This is the pipeline in `scripts/xberg/`.
- **docling** *(not recommended)* — alternate engine; heavier (~1 GB ML models on first
  use). Scripts in `scripts/docling/`.

Extraction only. No MD → Excel/Word/PDF reconstruction.

---

## Engine selection — ASK ONCE, then remember

Preference file (per user): `~/.aiws_doc_convert/engine.json`

```
On invocation:
  1. Read ~/.aiws_doc_convert/engine.json
  2. If it does NOT exist  (first time ever):
       Ask the user, exactly:
         "Which conversion engine should I use (saved for next time)?
            ① xberg   (recommended) — fast, local, ~33 MB, all file types
            ② docling (not recommended) — one-time ~1 GB model download"
       Save their choice:  {"engine": "xberg"}  or  {"engine": "docling"}
  3. If it exists: use the saved engine SILENTLY. Do NOT ask again.
  4. Only re-ask if the user EXPLICITLY says to switch (e.g. "use docling instead",
     "switch back to xberg") — then overwrite engine.json and continue.
```

Never call the other engine's scripts once a choice is saved — route strictly to the
chosen engine. (docling's ~1 GB deps are installed only if/when docling is the choice —
see Prerequisites.)

---

## First-use manual — OFFER ONCE, then never again

There is a bundled quick manual at `references/MANUAL.html` (a standalone, offline HTML
page: what the skill does, the two engines, the pipeline, the output shape). Offer it
exactly once, tracked by the `manual_prompted` flag in the same `~/.aiws_doc_convert/engine.json`.

```
On the FIRST invocation (engine.json missing OR "manual_prompted" not set):
  After the engine question, also ask the user, exactly:
     "Xem hướng dẫn nhanh về skill này không? (có / không)
      — engine, quy trình, kết quả. Mở trong trình duyệt."
  If the user says YES: open the bundled manual in their default browser —
     Windows:  cmd /c start "" "<skill_dir>\references\MANUAL.html"
     macOS:    open "<skill_dir>/references/MANUAL.html"
     Linux:    xdg-open "<skill_dir>/references/MANUAL.html"
     (<skill_dir> = the folder that contains this skill's scripts/ and references/.)
  Whether they say yes or no, set  "manual_prompted": true  in engine.json
  (merge — keep the existing "engine" value).

NEVER prompt about the manual again. Re-open it ONLY when the user explicitly asks
("mở hướng dẫn", "open the manual", "show the manual").
```

---

## ENGINE A — xberg (recommended)

### Phase 1 — mechanical extraction (no VLM)
```
python scripts/xberg/ingest.py "<input_file>" "<output_dir>" [--dpi 200]
```
`ingest.py` detects the extension and routes to the right handler:

| Input | Handler | Needs |
|---|---|---|
| xlsx/xlsm/xls | extract_hybrid.py | Excel COM (Windows) |
| pptx/ppt | extract_pptx.py | PowerPoint COM |
| docx/doc | extract_word.py | Word COM |
| pdf | extract_pdf.py | xberg + pymupdf |
| png/jpg/jpeg/tif/tiff/bmp/gif/webp | extract_image.py | xberg |
| drawio | extract_drawio.py | (XML→Mermaid) + draw.io CLI for PNG |
| svg | extract_svg.py | pymupdf |
| csv/txt/md/rtf/html/json/xml/yaml/eml | extract.py | xberg |

Output shape (uniform):
```
<output_dir>/
  source.md    top = source file path; then one section per unit:
               ### <unit> / **Image:** render / **Extracted:** faithful text / <!-- summary: pending -->
  pages/*.png   index-named renders: slide_01.png / page_01.png / sheet_01.png
  figures/**    embedded rasters pulled out (logos, screenshots)
  manifest.json counts + route + warnings + caption_status
```
Large Excel data sheets (>300 rows or >60 cols) are **sampled** (text slice, render
skipped) with a ⚠️ warning — full data stays in the source file (path at top of source.md).

### Phase 2 — enhancement pass (opt-in; the VLM = you, Claude)
After Phase 1, **always ask**: "Run the enhancement pass? (writes a summary — plus Mermaid
for any diagram — into source.md per unit; ~5k tokens per image)."
If yes: for each `<!-- summary: pending -->`, open the linked PNG and replace the marker
with `**Summary:** …` (+ a ```mermaid block for graph/flow/ER diagrams). No OCR dump —
transcribe only meaningful labels; the image stays as detail-on-demand. Then set
`caption_status: "done"` in manifest.json. Report any sampled sheets to the user.

---

## ENGINE B — docling (alternate)
Same job (input → Markdown), heavier engine (~1 GB ML models). Scripts in `scripts/docling/`.

Run:
```bash
python scripts/docling/extract.py "<input_file>" --out-dir "<output_dir>" \
    [--format md|json|html|rich] [--render-pages] [--dpi 300] [--force-ocr] [--ocr-lang jpn,eng]
```
Full engine instructions (modes, flags, quality-check): `scripts/docling/DOCLING_ENGINE.md`
(+ `SKILL_INVOCATION_SUMMARY.md`). `build_image_index.py` builds the figure index.

Prereq — install ONLY when docling is the chosen engine (this is the ~1 GB path):
```bash
pip install docling          # pulls torch + ML models (~1 GB, first run downloads from Hugging Face)
pip install python-docx      # only if MD→DOCX is needed
```
An xberg-picker never installs this. docling still runs fully local after the one-time model download.

---

## Prerequisites (installed lazily by chosen engine)
```
# xberg path (recommended) — all platforms
pip install xberg python-pptx pymupdf
pip install pywin32          # Windows only, for xlsx/pptx/docx COM render (needs MS Office)

# docling path — install ONLY when docling is the chosen engine (~1 GB)
pip install docling
```
Do not install docling for xberg users — that is the whole point of the chooser: a
first-time user who picks xberg never downloads the 1 GB stack.

Core xberg extraction needs no ML model and no internet. Handlers import their heavy
deps lazily, so a missing dep (e.g. Office on non-Windows) only disables that one route.

---

## When to use
Any request to convert / extract / ingest a document into Markdown for AI. Not for
reconstruction (MD → styled Office) — that is out of scope for this skill.
