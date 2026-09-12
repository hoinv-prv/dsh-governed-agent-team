# Docling-Extract: Interactive Invocation Summary

## How It Works Now

### User Invokes
```
User: "convert this PDF to markdown"
User: "/docling-extract report.pdf"
User: "extract content from this file" [attachment: data.xlsx]
```

### Skill Flow

```
┌─────────────────────────────────────────────┐
│ 1. Identify File                            │
│    - From $ARGUMENTS or user message        │
│    - Validate exists & supported            │
│    - Get stats (size, pages)                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 2. Auto-Enable Defaults                     │
│    ✓ Text, tables, images                   │
│    ✓ Markdown output                        │
│    ✓ JSON output (coordinates)              │
│    (No questions - always included)         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 3. Ask About Additional Features            │
│    Using AskUserQuestion tool:              │
│                                             │
│    ☐ Render pages to PNG (recommended)     │
│    ☐ Generate image captions (AI)          │
│    ☐ Extract charts to CSV                 │
│    ☐ Extract formulas to LaTeX             │
│    ☐ Force OCR (fix broken text)           │
│    ☐ None - defaults only                  │
│                                             │
│    (Multi-select, clear descriptions)       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 4. Show Execution Plan                      │
│    "Extraction plan:                        │
│     ✓ MD + JSON                             │
│     ✓ Render pages (selected)               │
│     Output: ~6 MB, ~2 minutes               │
│     Proceed?"                               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 5. Build & Execute Command                  │
│    python extract.py file.pdf \             │
│      --render-pages \                       │
│      --non-interactive                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 6. Report Results                            │
│    "✓ Extraction complete                   │
│     Output: output/                         │
│       ├── file.md (150 KB)                  │
│       ├── file.json (400 KB)                │
│       └── pages/ (15 PNGs)                  │
│                                             │
│     Config saved for reuse."                │
└─────────────────────────────────────────────┘
```

---

## Example Conversation

**User:** "Convert this research paper to markdown"

**Claude (via skill):**
```
I'll extract content from research_paper.pdf (2.3 MB, 15 pages).

Auto-including:
✓ Markdown output
✓ JSON output (coordinates & structure)
✓ Text, tables, and images

[Presents AskUserQuestion with checkboxes]

Additional extraction features for research_paper.pdf?

☐ Render pages to PNG (recommended)
   Visual fallback for broken text, preserves exact layout. 
   Free, ~250KB per page.

☐ Generate image captions (AI)
   Auto-describe images with AI. Downloads 500MB model first time.
   Slow on CPU.

☐ Extract charts to CSV
   Extract data from chart images. Slow, ~10-30s per chart.

☐ Extract math formulas to LaTeX
   Convert equations to LaTeX. Downloads 800MB model. Slow.

☐ Force full-page OCR
   Ignore text layer, OCR everything. Use if text extraction broken.
   ~5s per page.

☐ None - use defaults only
   Just extract text, tables, images to MD + JSON. Fast.
```

**User:** [Selects: "Render pages" + "Generate captions"]

**Claude:**
```
Extraction plan for research_paper.pdf:

Auto-enabled:
  ✓ Markdown output
  ✓ JSON output (coordinates + structure)
  ✓ Text, tables, images

Selected features:
  ✓ Render pages to PNG
  ✓ Generate image captions

Output will be created in: output/
  ├── research_paper.md
  ├── research_paper.json
  ├── pages/ (est. ~3.8 MB)
  └── figures/ (with AI captions)

Estimated time: ~2 minutes
First run: Will download 500MB model

Running extraction...

[Executes command, shows progress]

✓ Extraction complete

Output in output/:
  ├── research_paper.md (152 KB) - Markdown with text, tables, images
  ├── research_paper.json (387 KB) - Full structure with coordinates
  ├── pages/ (15 PNGs, 3.8 MB) - Page renders
  └── figures/ (17 images, 2.1 MB)
      ├── fig_001.png - "System architecture diagram showing..."
      ├── fig_002.png - "Bar chart comparing sales across quarters..."
      └── ...

Your saved default preferences (.claude/skills/docling-extract/user_config.json)
will be applied automatically next time.
```

---

## Key Benefits

### ✅ Discoverable
- User sees all features through questions
- No need to read docs or remember flags
- Descriptions explain what each does

### ✅ Guided
- Smart defaults (always include essentials)
- Ask only about optional features
- Show execution plan before running

### ✅ Educational
- Learn features through use
- See what's possible
- Understand trade-offs (time/size)

### ✅ Flexible
- Any combination of features
- No pigeonholing into profiles
- Can select none (defaults only) or all

### ✅ Transparent
- Shows what will happen
- Estimates time/size
- Warns about downloads

### ✅ Reusable
- Saves config after first run
- Easy to repeat on similar files
- Can share configs with team

---

## Special Cases

### Excel Files
**Auto-adds option:**
```
☐ Extract cell formulas
   Get =SUM(), =VLOOKUP() formulas from cells. Free.
```

### Broken PDFs (Auto-Detected)
**If extraction returns minimal content:**
```
⚠ Warning: Text extraction returned very little content.
This PDF might have a broken text layer.

Recommend: Enable "Force full-page OCR"

[Auto-selects Force OCR option]
```

### First-Time AI Features
**When user selects caption/chart/formula for first time:**
```
Note: This will download AI models (~500-800 MB) on first use.
Models are cached for future extractions.
Internet connection required.

Proceed? [Yes/No]
```

---

## Non-Interactive Override

**For scripts/automation:**
```bash
# Skip skill, run script directly
python .claude/skills/docling-extract/scripts/extract.py file.pdf \
  --render-pages \
  --caption-images \
  --non-interactive

# Excel with cell formulas (auto-upgrades to rich)
python .claude/skills/docling-extract/scripts/extract.py file.xlsx \
  --excel-formulas \
  --non-interactive
```

**Skill still available for interactive use when needed.**

---

## Files Updated

✅ `SKILL.md` - Added "When Invoked as Skill" section (6 steps)
✅ `INTERACTIVE_EXTRACTION_DESIGN.md` - Full UI/UX spec
✅ `SKILL_INVOCATION_SUMMARY.md` - This file (quick reference)

**Status:** Ready for implementation. Script (`extract.py`) needs to support the flags mentioned.
