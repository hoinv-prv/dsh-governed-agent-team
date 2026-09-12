---
name: docling-extract
description: >
  Extract structured content from documents to Markdown, JSON, or HTML.
  Use when the user wants to: convert any file (PDF, DOCX, PPTX, XLSX, XLSM, images) to readable format;
  extract text, tables, images, or charts from documents; analyze document structure;
  get document content for AI processing; or mentions "extract", "analyze", "convert to markdown".
user-invocable: true
---

# SKILL: docling-extract

## Purpose
Extract structured content from various document formats using docling.

**Input formats:** PDF, DOCX, PPTX, XLSX, XLSM, PNG/JPG/images  
**Output formats:** Markdown, JSON, HTML, plain text, page images, extracted figures

---

## When Invoked as Skill

User triggers: 
- "convert this PDF" / "extract from file.xlsx" / `/docling-extract document.pdf` → **Extraction Mode**
- `/docling-extract config` / "update extraction preferences" → **Config Management Mode**
- `/docling-extract check <path>` / "check conversion quality" → **Quality Check Mode**

### Determine Mode

Check $ARGUMENTS and user message:
- Contains "check" / "quality" / "verify" + output path → **Quality Check Mode** (Step 200)
- Contains "config" / "preferences" / "settings" → **Config Mode** (Step 100)
- Contains file path OR extraction keywords → **Extraction Mode** (Step 1)

---

## EXTRACTION MODE

### Step 1: Identify Input File

- Check `$ARGUMENTS` for file path
- Or identify from user message ("this PDF", "the Excel file", attached file)
- Validate:
  - File exists
  - Supported format (PDF/DOCX/PPTX/XLSX/XLSM/images)
  - Get file stats (size, page count if applicable)

If file not found or ambiguous, ask user to specify.

### Step 2: Check for Saved Preferences

**Config location:** `.claude/skills/docling-extract/user_config.json`

**If config exists:**
```
Found saved extraction preferences:
  ✓ Render pages to PNG
  ✗ Generate image captions
  ✗ Extract charts to CSV
  ✗ Extract formulas
  
Proceed with these settings? [Y/n/customize]

Options:
  Y - Use saved preferences
  n - Customize for this extraction only
  
(Run '/docling-extract config' to update your defaults)
```

- If user chooses **Y**: Skip to Step 3 (use saved config)
- If user chooses **n/customize**: Continue to Step 2b (ask questions)

**If no config exists (first time):**
```
First extraction! Let's set your preferences.
Your choices will be saved as defaults for future extractions.
```

Continue to Step 2b.

### Step 2b: Ask About Additional Features

**Always auto-enable (no questions) — the lean rich set:**
- Text & tables extraction
- Markdown output (Excel: collapsed per-sheet with screenshot pointers + text)
- HTML output (formatted, human-readable)
- Images extracted to `figures/`
- Excel: per-sheet screenshots (`sheets/`) — visual truth
- PDF: page renders (`pages/`) when Render pages is chosen

Not produced by default (pass `--full`): the verbose JSON structure + image
index. JSON is machine-only and can be 900 MB+ on big image-heavy workbooks; add
`--full` only if a downstream step needs exact cell geometry.

**Ask user about additional features using AskUserQuestion:**

```markdown
Question: "Additional extraction features for [filename] ([size], [pages] pages)?"
Header: "Features"
Multi-select: true

Options:
  1. Label: "Render pages to PNG (recommended)"
     Description: "Visual fallback for broken text, preserves exact layout. Free, ~250KB per page."
  
  2. Label: "Generate image captions (AI)"
     Description: "Auto-describe images with AI. Downloads 500MB model first time. Slow on CPU."
  
  3. Label: "Recognize chart data (PDF only)"
     Description: "docling reads chart data into the JSON/MD output. No separate CSV file. Slow. PDF only."
  
  4. Label: "Enrich math formulas as LaTeX (PDF only)"
     Description: "Formulas written as LaTeX inline in the JSON/MD output. No separate .tex file. Downloads 800MB model. Slow. PDF only."
  
  5. Label: "Force full-page OCR"
     Description: "ONLY for scanned/image PDFs. Uses Chinese OCR models - may garble Japanese/other languages. Try without this first. ~5s per page."

  6. Label: "None - use defaults only"
     Description: "Just extract text, tables, images to MD + JSON. Fast."
```

> **AI features (captions, chart recognition, formula enrichment, image
> classification, OCR) apply to PDF / image inputs only.** docling parses
> office formats (XLSX/DOCX/PPTX) with a structural backend that does not run
> these models — selecting them for an Excel/Word file has no effect.

**Excel-specific (add if .xlsx/.xlsm):**
```markdown
  7. Label: "Extract cell formulas"
     Description: "Get =SUM(), =VLOOKUP() formulas from cells. Free."
```

**Additional question if Force OCR selected:**
```markdown
Question: "OCR language?"
Header: "Language"
Options:
  - Label: "Auto-detect"
  - Label: "Japanese (jpn)" + Note: "Still uses Chinese models. Works OK for kanji, poor for kana."
  - Label: "English (eng)"
  - Label: "Chinese (chi)" + Note: "Best quality - native models"
  - Label: "Mixed (jpn,eng)"
```

### Step 2c: Save Preferences (First Time Only)

**If no config existed (first extraction):**

Ask user:
```
Save these as your default preferences for future extractions? [Y/n]

Y - These settings will auto-apply next time
n - Use for this extraction only (ask again next time)
```

If user chooses **Y**:
- Create config file: `.claude/skills/docling-extract/user_config.json`
- Save selected features:
  ```json
  {
    "version": "1.0",
    "preferences": {
      "render_pages": true,
      "caption_images": false,
      "extract_charts": false,
      "extract_formulas": false,
      "classify_images": false,
      "force_ocr": false,
      "ocr_lang": "auto",
      "excel_formulas": false
    },
    "created_at": "2026-06-18T12:00:00Z",
    "updated_at": "2026-06-18T12:00:00Z"
  }
  ```
- Confirm: "✓ Preferences saved. Future extractions will use these automatically."

If user chooses **n**:
- Don't save config
- Note: "Using settings for this extraction only. You'll be asked again next time."

**If config already existed:**
- Skip this step (user chose to customize this one time, don't update saved config)

### Step 3: Show Execution Plan

Before running, show what will happen:

```
Extraction plan for [filename]:

Auto-enabled (lean rich set):
  ✓ Markdown (Excel: collapsed per-sheet + screenshot pointers)
  ✓ HTML (formatted)
  ✓ Text, tables, images → figures/
  ✓ Excel: per-sheet screenshots → sheets/

Selected features:
  ✓ [e.g. Extract cell formulas → _formulas.md]

Output will be created in: [output_dir]/
  ├── [filename].md
  ├── [filename].html
  ├── figures/
  ├── sheets/        (Excel screenshots)
  └── manifest.json
  (JSON + image index only with --full)

Estimated time: ~[time]

Proceed?
```

### Step 4: Build Command

Based on user selections, build command:

```python
command = [
    "python",
    "scripts/docling/extract.py",
    str(file_path),
    "--non-interactive"  # Skip script's own prompts
]

# Add flags based on selections
if "Render pages" selected:
    command.append("--render-pages")

if "Generate image captions" selected:
    command.append("--caption-images")

if "Extract charts" selected:
    command.append("--extract-charts")

if "Extract formulas" selected:
    command.append("--extract-formulas")

if "Force OCR" selected:
    command.append("--force-ocr")
    if ocr_lang != "Auto-detect":
        command.append(f"--ocr-lang={lang_code}")

if "Extract cell formulas" selected:
    command.append("--excel-formulas")

if "Skip Excel screenshots" selected:      # screenshots are ON by default
    command.append("--no-screenshots")

if "Full output (JSON + image index)" selected:
    command.append("--full")

# Set output directory
command.extend(["--out-dir", output_dir])
```

Note: rich (lean) output is the default — no `--rich`/`--format` needed. Excel
per-sheet screenshots run automatically (Windows + Excel + pywin32 required).

### Step 5: Execute with Progress

Run the command:
```bash
cd [project_root]
python scripts/docling/extract.py [file] [flags] --out-dir [output]
```

Monitor output and show progress to user.

### Step 6: Report Results

After completion, report:

```
✓ Extraction complete

Output in [output_dir]/:
  ├── [filename].md - Markdown (Excel: collapsed per-sheet + screenshot pointers)
  ├── [filename].html - Formatted human-readable view
  ├── manifest.json - Asset index
  ├── sheets/ (Excel per-sheet screenshots)   [Excel only]
  ├── [filename]_formulas.md                   [if --excel-formulas]
  ├── pages/ (page renders)                    [PDF, if --render-pages]
  └── figures/ (extracted embedded images)

[Show any warnings or errors]
```

(Your saved default preferences live in
`.claude/skills/docling-extract/user_config.json` and are applied automatically
next time — see Config Management Mode.)

### Error Handling

**File not found:**
```
Error: Could not find file at [path]
Please provide the full path or attach the file.
```

**Unsupported format:**
```
Error: Format [.ext] not supported.
Supported: PDF, DOCX, PPTX, XLSX, XLSM, PNG, JPG, JPEG, TIFF, BMP, WEBP
```

**Script execution failed:**
```
Error during extraction: [error message]

This might help:
- If text looks garbled: Try "Force full-page OCR"
- If file is very large: Extraction may take longer
- If model download failed: Check internet connection
```

---

## CONFIG MANAGEMENT MODE

Triggered by: `/docling-extract config` OR "update extraction preferences" / "change extraction settings"

### Step 100: Load Current Config

Check for existing config: `.claude/skills/docling-extract/user_config.json`

**If exists:**
- Load current preferences
- Show to user

**If doesn't exist:**
- Use defaults (all features OFF except essentials)

### Step 101: Show Current Settings

```
Docling extraction preferences:

Current defaults:
  ✓ Render pages to PNG
  ✗ Generate image captions
  ✗ Extract charts to CSV
  ✗ Extract math formulas
  ✗ Classify image types
  ✗ Force full-page OCR
  OCR language: auto

These settings auto-apply to all future extractions.
```

### Step 102: Ask for Updates

Use AskUserQuestion with **current values pre-selected**:

```markdown
Question: "Update your default extraction preferences?"
Header: "Features"
Multi-select: true

Options:
  1. Label: "Render pages to PNG (recommended)"
     Description: "Visual fallback, ~250KB per page. Currently: ON"
     [PRE-SELECT if currently enabled]
  
  2. Label: "Generate image captions (AI)"
     Description: "Downloads 500MB model first time. Currently: OFF"
     [PRE-SELECT if currently enabled]
  
  3. Label: "Recognize chart data (PDF only)"
     Description: "Chart data into JSON/MD, no CSV file. Slow. PDF only. Currently: OFF"
     [PRE-SELECT if currently enabled]
  
  4. Label: "Enrich formulas as LaTeX (PDF only)"
     Description: "LaTeX inline in JSON/MD, no .tex file. Downloads 800MB model. PDF only. Currently: OFF"
     [PRE-SELECT if currently enabled]
  
  5. Label: "Classify image types"
     Description: "Chart/diagram/photo classification. Currently: OFF"
     [PRE-SELECT if currently enabled]
  
  6. Label: "Force full-page OCR"
     Description: "Always OCR, ignore text layer. Currently: OFF"
     [PRE-SELECT if currently enabled]
```

**If Force OCR selected, also ask:**
```markdown
Question: "Default OCR language?"
Header: "Language"
Current: auto

Options:
  - Auto-detect (recommended)
  - Japanese (jpn)
  - English (eng)
  - Chinese (chi)
  - Mixed (jpn,eng)
```

### Step 103: Save Updated Config

After user makes selections:

1. **Create/update** `.claude/skills/docling-extract/user_config.json`:
   ```json
   {
     "version": "1.0",
     "preferences": {
       "render_pages": true,
       "caption_images": false,
       "extract_charts": false,
       "extract_formulas": false,
       "classify_images": false,
       "force_ocr": false,
       "ocr_lang": "auto",
       "excel_formulas": false
     },
     "created_at": "2026-06-18T10:00:00Z",
     "updated_at": "2026-06-18T12:30:00Z"
   }
   ```

2. **Confirm to user:**
   ```
   ✓ Preferences updated and saved.
   
   Your new defaults:
     ✓ Render pages to PNG
     ✓ Generate image captions
     ✗ Extract charts
   
   These will auto-apply to all future extractions.
   
   To customize for a specific file:
     - Run extraction normally
     - Choose "customize" when prompted
   ```

### Step 104: Done

Config management complete. Return to conversation.

---

## QUALITY CHECK MODE

Triggered by: `/docling-extract check <path>` OR "check conversion quality" / "verify extraction"

**Purpose:** Report-only audit — *can an AI understand the source from these
outputs alone?* Flags silent data loss and recommends actions. It does **not**
enrich, rewrite, or delete anything (report + suggestions only, zero
hallucination risk). Mirrors xberg-extract's Check Mode so the two engines can be
compared on the same document.

### Step 200: Locate the output(s)

Take path(s) from `$ARGUMENTS`/message (or the most recent extraction in the
conversation). Each must contain `manifest.json`. If none found, ask which folder.

### Step 201: Inventory & assess

Read `manifest.json`, then inventory the lean outputs and judge each's value to an
AI reader:

- **`<name>.md`** — text complete? tables present? For Excel, is it the collapsed
  per-sheet form (each sheet = screenshot pointer + its own text)?
- **`sheets/`** (Excel) — one screenshot per sheet? readable? multi-page sheets split?
- **`pages/`** (PDF) — present if `--render-pages`? readable at DPI (150 ok for text,
  higher for dense diagrams)?
- **`figures/`** — real separated assets, or noise/duplicates of the render?
- **`<name>_formulas.md`** (Excel, if requested) — formulas captured?
- **`<name>.html`** — present (formatted human-readable view)?

### Step 202: Emit the report

```
AI Consumption Quality Report: <filename>
=================================================
Source: <name> (<size>, <sheet/page count>)
Engine: docling

WHAT WAS CAPTURED:
  [OK/WARN/FAIL] Text + tables         - <note>
  [OK/WARN/FAIL] Per-sheet screenshots - <N sheets>        (Excel)
  [OK/WARN/FAIL] Page renders          - <N @ DPI>         (PDF)
  [OK/WARN/FAIL] Embedded figures      - <N>
  [OK/WARN/FAIL] Cell formulas         - <N / not requested> (Excel)
  [OK/WARN/FAIL] Collapsed per-sheet MD - <each sheet has screenshot + text?>

FOR AI CONSUMPTION:
  PRIMARY:  <name>.md   - text + tables + per-sheet screenshot pointers
  SUPPORT:  sheets/ or pages/ - visual ground truth, opened on demand
  ASSETS:   figures/    - <keep real images / drop render duplicates>
  READABLE: <name>.html - formatted human view

GAPS / ACTIONS:
  - <e.g. sheet X blank/failed -> re-render or check the source>
  - <e.g. MD text sparse on a diagram-only sheet -> rely on its screenshot>
  - <e.g. figures are render duplicates -> safe to delete>
  - <e.g. a downstream step needs exact cell geometry -> re-run with --full for JSON>
```

Be concrete and honest — the point is to catch silent data loss (empty/failed
sheets, missing screenshots, sparse text, unreadable renders), not to
rubber-stamp. **Do not modify any files** — only report and recommend.

### Step 203: Batch summary (if multiple outputs)

If several folders were checked, add a one-line verdict per folder plus any common
issues seen across them.

### Step 204: Done

Report complete. Return to conversation. (No files were changed.)

---

## Quick Start

**Simple conversion (any format → Markdown):**
```bash
python scripts/docling/extract.py <file> --format md
```

**Rich extraction (PDF → everything):**
```bash
python scripts/docling/extract.py <file.pdf> --rich --out-dir output/
```

Output structure (rich mode, default = lean):
```
output/
├── document.md           # Markdown (Excel: collapsed per-sheet w/ screenshot ptrs + text)
├── document.html         # Formatted human-readable view (merged cells render)
├── manifest.json         # Small asset index
├── figures/              # Extracted embedded images
├── sheets/               # Per-sheet screenshots (Excel only)
└── pages/                # Full-page renders (PDF only, needs --render-pages)

# with --full, also:
├── document.json         # Full docling structure (coordinates, spans) — can be huge
└── image_index.json / IMAGE_INDEX.md
```

**Default is lean** — optimized for AI ingestion: MD (text) + HTML (readable) +
screenshots (visual) + figures. The verbose JSON structure and image index are
omitted unless you pass `--full` (JSON can be 900 MB+ on big image-heavy
workbooks and is not read during normal ingestion). Tables are captured inside
the MD/HTML — no separate per-table CSV files.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `extract.py` | **Main extractor** — any format → MD/JSON/HTML/rich output |
| `build_image_index.py` | Build navigation index for images in Excel files |

---

## Main Options

```bash
extract.py <input_file> [options]

Formats:
  --format md|json|html|text|rich   Output format (default: md; Excel auto-upgrades to rich)
  --rich                            Rich pipeline: MD+HTML+figures+manifest (+screenshots for xlsx, +pages if --render-pages)
  --full                            Also emit JSON structure + image index (default: lean, omits them)

Extraction:
  --ocr-lang jpn,eng                OCR languages (post-processing only; see Known Issues)
  --force-ocr                       Force full-page OCR, ignore text layer (PDF only)
  --extract-charts                  Recognize chart data into JSON/MD (PDF only, no CSV file)
  --extract-formulas                Enrich math formulas as LaTeX in JSON/MD (PDF only, no .tex file)
  --caption-images                  Auto-generate image captions via VLM (PDF only)
  --classify-images                 Classify image types: chart/diagram/photo (PDF only)
  --excel-formulas                  Extract Excel cell formulas to <name>_formulas.md (xlsx/xlsm)

Rendering:
  --render-pages                    Render pages to PNG (PDF only; forces rich)
  --dpi N                           Page render DPI (default: 300)
  --no-screenshots                  Skip per-sheet Excel screenshots (default: on for xlsx/xlsm)

Output:
  --out-dir DIR                     Output directory (default: ./output)
  --non-interactive                 Skip interactive prompts (for automation)
```

---

## Output Formats

### Markdown (default)
- Human-readable text
- Tables, headings, lists
- Images as references or base64
- Best for: Reading, editing, LLM context

### JSON
- Full docling structure
- Text with coordinates (bboxes)
- Layout hierarchy
- Best for: AI agents, spatial queries, reconstruction

### HTML
- Web-ready output
- Preserves styling
- Images embedded
- Best for: Display, publishing

### Rich (all formats + assets)
- MD + JSON + HTML
- Page renders (PNG, PDF only, needs --render-pages)
- Extracted figures
- Tables captured inside JSON/MD (no separate CSV files)
- Manifest index
- Best for: Comprehensive analysis, AI workflows

---

## Excel-Specific Features

Excel files get additional processing (in rich mode):

1. **Per-sheet screenshots** — each sheet rendered to PNG via Excel's own
   renderer (`sheets/sheet_NN_<name>.png`), capturing the **visual layout**
   (grid, merged cells, borders, fills). Wide sheets fit to 1 page wide;
   multi-page sheets split to `_p1`, `_p2`, ...
2. **Collapsed per-sheet MD** — the main `<name>.md` is rebuilt as ONE file,
   one section per sheet, each = heading + screenshot pointer + that sheet's text
   (read from openpyxl, so merged cells appear **once**, not duplicated):
   ```
   # Sheet: 表紙
   **Screenshot:** ![表紙](sheets/sheet_01_表紙.png)
   | VTI資料コード | 01-BM/PM/VTI | 担当者 |
   | 資料バージョン | 1.0 | 更新日 |
   ```
   (Screenshot = visual truth; text = searchable. One file, no separate nav MD.)
3. **Image index** (`image_index.json` + `IMAGE_INDEX.md`) linking images to sheets
4. **Embedded images** extracted to `figures/`
5. **Cell formulas** (optional, `--excel-formulas`) → `<name>_formulas.md`

**Why the screenshot matters:** docling's MD flattens merged cells and a table is
cells (not an image), so `figures/` never contains the table layout. The
screenshot is the only output that shows *visually* which value sits under which
header — the reliable check for merged-header spreadsheets.

Scripts:
- `extract.py <file.xlsx>` → auto-upgrades to rich and runs the full Excel
  pipeline (screenshots + collapsed per-sheet MD + image index).
  Add `--excel-formulas` for formulas. `--no-screenshots` to skip screenshots.
- `build_image_index.py` → manual image index creation
- Screenshots need **Windows + Excel + pywin32** (skipped gracefully otherwise).

**Best sources per need:**
- **Visual layout** → per-sheet screenshot (`sheets/`), linked in the MD.
- **Searchable text** → the collapsed `<name>.md` (openpyxl text, merges once).
- **Exact cell geometry** → JSON (`col_span`/offsets) — but huge on big workbooks.

**Known limits (docling structural backend for Excel):**
- Merged cells are flattened in MD (values duplicated across the span). Use JSON
  or the screenshot when cell grouping matters.
- AI features (captions, chart/formula/OCR) do **not** run on Excel — PDF only.

---

## Advanced Features

### Auto Image Captions (VLM)
```bash
extract.py <file.pdf> --caption-images
```
Generates descriptions for diagrams, charts, photos using vision model.

### Chart Recognition (PDF only)
```bash
extract.py <file.pdf> --extract-charts
```
Enables docling's chart recognition. Recognized chart data is written **into the
JSON and MD output** — the script does not emit separate CSV or Python files.

### Formula Enrichment (PDF only)
```bash
extract.py <file.pdf> --extract-formulas
```
Enriches math equations as **LaTeX inline in the JSON/MD output**. No separate
`.tex` files are written.

### Excel Cell Formulas (xlsx/xlsm)
```bash
extract.py <file.xlsx> --excel-formulas
```
Reads cell formulas (`=SUM()`, `=VLOOKUP()`, ...) via openpyxl and writes them,
grouped per sheet, to `<name>_formulas.md`.

---

## Known Issues

### Windows: AI Features Require Developer Mode

**Problem:** AI features (image captions, chart extraction, formula extraction, image classification) fail on Windows with symlink errors.

**Cause:** HuggingFace model downloads use symlinks, which Windows blocks unless:
- Developer Mode is enabled, OR
- Running as Administrator

**Error message:**
```
OSError: symbolic link privilege not held
Cannot create symlink for model download
```

**Fix:**
1. **Enable Developer Mode** (recommended):
   - Settings → Privacy & Security → For Developers
   - Toggle "Developer Mode" ON
   - Restart terminal
   - AI features will work

2. **Run as Admin** (not recommended for daily use)

3. **Skip AI features** (workaround):
   - Use only: page renders, OCR, text/table extraction
   - Avoid: captions, charts, formulas, classification

**These features work without Developer Mode:**
- ✅ Render pages to PNG (PyMuPDF)
- ✅ Force OCR (RapidOCR built-in)
- ✅ Text, tables, images extraction
- ✅ All output formats (MD, JSON, HTML)

**These need Developer Mode (and are PDF-only):**
- ⚠️ Generate image captions
- ⚠️ Chart recognition
- ⚠️ Formula enrichment (LaTeX)
- ⚠️ Classify image types

---

### Excel image extraction (docling v2.102+)

**Problem:** Images show as `<!-- image -->` instead of base64.

**Fix:** `extract.py` forces `ImageRefMode.EMBEDDED` automatically.

**Details:** Docling v2.102+ changed default from EMBEDDED → PLACEHOLDER. Our script overrides this for all conversions.

---

### --force-ocr: When NOT to use it

**Problem:** `--force-ocr` can make text extraction WORSE if the PDF already has a native text layer.

**Why:**
- Most PDFs (non-scanned) have **native text layer** — text is real text, not pixels
- Docling extracts native text perfectly without OCR
- `--force-ocr` ignores native text and runs OCR instead
- RapidOCR uses Chinese models regardless of `--ocr-lang` setting
- Chinese OCR on Japanese/other languages = garbled text (especially hiragana/katakana)

**Models always loaded by RapidOCR:**
```
ch_PP-OCRv4_det_mobile     ← Chinese detection
ch_ppocr_mobile_v2.0_cls   ← Chinese classifier  
ch_PP-OCRv4_rec_mobile     ← Chinese recognition
```

`--ocr-lang jpn` only affects post-processing, NOT model selection.

**When to use --force-ocr:**
- ✅ Scanned documents (images of paper)
- ✅ Screenshots embedded in PDFs
- ✅ Image-only PDFs (no text layer)
- ✅ PDFs with corrupted text layer (mojibake in output)

**When NOT to use --force-ocr:**
- ❌ Normal PDFs with text (Word → PDF, digital documents)
- ❌ Japanese/Korean/non-Chinese text PDFs
- ❌ "Just to be safe" (default should be OFF)

**How to check if PDF has text layer:**
1. Try extraction WITHOUT --force-ocr first
2. Check JSON text element count and sample text quality
3. If text is clean → don't use OCR
4. If text is missing/garbled → THEN use --force-ocr

**Recommendation for quality check:**
When checking conversions, flag if --force-ocr was used on a PDF that had native text.

---

## Examples

**Convert PDF to Markdown:**
```bash
extract.py document.pdf
# Output: output/document.md
```

**Extract with rich pipeline (PDF):**
```bash
extract.py flowchart.pdf --rich --out-dir flowchart_analysis/
# Output: MD + JSON + page PNGs + extracted figures + manifest
```

**Excel with image index:**
```bash
extract.py report.xlsx --format rich
# Output: MD + per-sheet MD + image index + all images extracted
```

**Japanese PDF with OCR:**
```bash
extract.py japanese.pdf --force-ocr --ocr-lang jpn
```

**Extract charts and formulas:**
```bash
extract.py research.pdf --extract-charts --extract-formulas
```

---

## When to Use This Skill

✅ **Use docling-extract when:**
- Converting documents to readable format
- Extracting content for analysis
- Getting document structure/layout
- Preparing content for LLM processing
- Need text, tables, images FROM documents

---

## Dependencies

```bash
pip install docling              # Core extraction
pip install pymupdf              # Page/sheet rendering to PNG
pip install pywin32             # Excel per-sheet screenshots (Windows + Excel only)
```

Docling auto-installs: openpyxl (also used for --excel-formulas + per-sheet
text), python-pptx, torch (OCR models).

- `pymupdf` + `pywin32` are needed for Excel per-sheet screenshots. If either is
  missing (or not on Windows/no Excel), screenshots are skipped gracefully and
  the rest of the pipeline still runs.

First run downloads AI models (~1GB) — internet required.

---

## Verified Environment

- Windows 11, Python 3.13.3
- docling 2.102.2, torch 2.11.0+cpu
- PyMuPDF 1.24+ (for page renders)
