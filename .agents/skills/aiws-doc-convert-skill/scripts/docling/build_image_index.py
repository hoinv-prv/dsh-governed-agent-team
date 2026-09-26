"""
build_image_index.py - Build image-to-sheet index for Excel files

Maps extracted images to their source sheets in Excel files.
Creates a JSON index and optional Markdown reference.

Usage:
    python build_image_index.py <excel_output_dir> [--format json|md|both]

Examples:
    build_image_index.py output/report_xlsx/
    build_image_index.py output/data/ --format both
"""
import argparse
import json
import re
import sys
from pathlib import Path


def parse_excel_md(md_path: Path) -> dict:
    """
    Parse Excel markdown to extract sheet structure.

    Returns dict: {sheet_name: {images: [], tables: [], line_range: (start, end)}}
    """
    if not md_path.exists():
        return {}

    content = md_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    sheets = {}
    current_sheet = None
    sheet_start = 0

    for i, line in enumerate(lines):
        # Detect sheet headers: # Sheet: SheetName or ## SheetName
        sheet_match = re.match(r'^#+ (?:Sheet: )?(.+)$', line)

        if sheet_match:
            # Save previous sheet range
            if current_sheet:
                sheets[current_sheet]['line_range'] = (sheet_start, i - 1)

            # Start new sheet
            current_sheet = sheet_match.group(1).strip()
            sheet_start = i
            sheets[current_sheet] = {
                'images': [],
                'tables': [],
                'line_range': None
            }

        # Detect images: ![alt](path) or ![Figure N](figures/...)
        elif current_sheet:
            img_matches = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            for alt, path in img_matches:
                sheets[current_sheet]['images'].append({
                    'alt': alt,
                    'path': path,
                    'line': i
                })

    # Save last sheet range
    if current_sheet:
        sheets[current_sheet]['line_range'] = (sheet_start, len(lines) - 1)

    return sheets


def scan_figures_directory(figures_dir: Path) -> list:
    """Scan figures/ directory for all extracted images."""
    if not figures_dir.exists():
        return []

    images = []
    img_files = sorted(
        list(figures_dir.glob('*.png'))
        + list(figures_dir.glob('*.jpg'))
        + list(figures_dir.glob('*.jpeg'))
    )
    for img_file in img_files:
        images.append({
            'filename': img_file.name,
            'path': str(img_file.relative_to(figures_dir.parent)),
            'size_bytes': img_file.stat().st_size
        })

    return images


def build_index(output_dir: Path) -> dict:
    """
    Build complete image index from Excel extraction output.

    Returns: {
        'source_file': str,
        'sheets': {sheet_name: {images: [], line_range: []}},
        'all_figures': [{filename, path, size_bytes}],
        'orphaned_images': [images not linked to any sheet]
    }
    """
    output_dir = Path(output_dir)

    # Find MD file(s)
    md_files = list(output_dir.glob('*.md'))
    if not md_files:
        raise FileNotFoundError(f"No .md files found in {output_dir}")

    md_path = md_files[0]  # Use first MD file

    # Parse sheet structure from MD
    sheets = parse_excel_md(md_path)

    # Scan figures directory
    figures_dir = output_dir / 'figures'
    all_figures = scan_figures_directory(figures_dir)

    # Find orphaned images (in figures/ but not referenced in MD)
    referenced_paths = set()
    for sheet_data in sheets.values():
        for img in sheet_data['images']:
            referenced_paths.add(img['path'])

    orphaned = [
        fig for fig in all_figures
        if fig['path'] not in referenced_paths
    ]

    index = {
        'source_file': md_path.stem,
        'sheets': sheets,
        'all_figures': all_figures,
        'orphaned_images': orphaned,
        'stats': {
            'total_sheets': len(sheets),
            'total_figures': len(all_figures),
            'orphaned_count': len(orphaned)
        }
    }

    return index


def write_json_index(index: dict, output_path: Path):
    """Write index as JSON."""
    output_path.write_text(
        json.dumps(index, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"JSON index: {output_path}")


def write_markdown_index(index: dict, output_path: Path):
    """Write index as human-readable Markdown."""
    lines = [
        f"# Image Index: {index['source_file']}",
        "",
        f"**Total sheets:** {index['stats']['total_sheets']}  ",
        f"**Total figures:** {index['stats']['total_figures']}  ",
        f"**Orphaned:** {index['stats']['orphaned_count']}",
        "",
        "---",
        ""
    ]

    # Per-sheet breakdown
    for sheet_name, sheet_data in index['sheets'].items():
        lines.append(f"## Sheet: {sheet_name}")
        lines.append("")

        if sheet_data['images']:
            lines.append(f"**Images ({len(sheet_data['images'])}):**")
            for img in sheet_data['images']:
                lines.append(f"- `{img['path']}` - {img['alt']} (line {img['line']})")
            lines.append("")
        else:
            lines.append("*No images*")
            lines.append("")

    # Orphaned images section
    if index['orphaned_images']:
        lines.append("---")
        lines.append("")
        lines.append(f"## ⚠️ Orphaned Images ({len(index['orphaned_images'])})")
        lines.append("")
        lines.append("Images in `figures/` not referenced in any sheet:")
        lines.append("")
        for img in index['orphaned_images']:
            size_kb = img['size_bytes'] / 1024
            lines.append(f"- `{img['filename']}` ({size_kb:.1f} KB)")
        lines.append("")

    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"MD index: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Build image-to-sheet index for Excel extraction output"
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Directory containing Excel extraction output (.md + figures/)"
    )
    parser.add_argument(
        "--format",
        choices=['json', 'md', 'both'],
        default='both',
        help="Output format (default: both)"
    )

    args = parser.parse_args()

    # Validate directory
    if not args.output_dir.exists():
        print(f"Error: Directory not found: {args.output_dir}", file=sys.stderr)
        sys.exit(1)

    # Build index
    print(f"Building image index for: {args.output_dir}")
    try:
        index = build_index(args.output_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Write outputs
    if args.format in ['json', 'both']:
        json_path = args.output_dir / 'image_index.json'
        write_json_index(index, json_path)

    if args.format in ['md', 'both']:
        md_path = args.output_dir / 'IMAGE_INDEX.md'
        write_markdown_index(index, md_path)

    # Summary
    print(f"\n✓ Index built:")
    print(f"  Sheets: {index['stats']['total_sheets']}")
    print(f"  Figures: {index['stats']['total_figures']}")
    if index['stats']['orphaned_count'] > 0:
        print(f"  ⚠ Orphaned: {index['stats']['orphaned_count']}")


if __name__ == '__main__':
    main()
