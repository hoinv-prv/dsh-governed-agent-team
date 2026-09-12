#!/usr/bin/env python3
"""
aiws-util-personal-notebook helper.

This script intentionally stays small:
- initialize a Personal Notebook folder
- append inbox notes
- create individual note files
- mark simple capture candidates
- archive files

It does not promote content to Knowledge Hub and does not treat notes as source of truth.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import date
from pathlib import Path


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9_-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "note"


def ensure_notebook(path: Path) -> None:
    (path / "notes").mkdir(parents=True, exist_ok=True)
    (path / "archive").mkdir(parents=True, exist_ok=True)
    readme = path / "README.md"
    inbox = path / "inbox.md"
    if not readme.exists():
        readme.write_text(
            "# Personal Notebook\n\n"
            "This notebook is not source of truth by default.\n\n"
            "AI must not auto-promote notes to Knowledge Hub.\n",
            encoding="utf-8",
        )
    if not inbox.exists():
        inbox.write_text("# Personal Notebook Inbox\n\n---\n\n## Notes\n", encoding="utf-8")


def build_note_block(args: argparse.Namespace) -> str:
    today = date.today().isoformat()
    review = args.review_needed or "no"
    return (
        f"\n\n### {today} — {args.title}\n\n"
        f"- Status: {args.status}\n"
        f"- Authority: {args.authority}\n"
        f"- Source: {args.source}\n"
        f"- Intended use: {args.intended_use}\n"
        f"- Review needed: {review}\n\n"
        f"#### Note\n{args.body.strip()}\n"
    )


def append_inbox(args: argparse.Namespace) -> dict:
    nb = Path(args.notebook_path)
    ensure_notebook(nb)
    inbox = nb / "inbox.md"
    with inbox.open("a", encoding="utf-8") as f:
        f.write(build_note_block(args))
    return {
        "status": "success",
        "operation": "append_inbox_note",
        "written_to": str(inbox),
        "note_title": args.title,
        "warnings": [
            "This note is not source of truth by default.",
            "No promotion to Knowledge Hub was performed.",
        ],
    }


def create_note_file(args: argparse.Namespace) -> dict:
    nb = Path(args.notebook_path)
    ensure_notebook(nb)
    today = date.today().isoformat()
    filename = f"{today}_{slugify(args.title)}.md"
    dest = nb / "notes" / filename
    if dest.exists() and not args.force:
        return {"status": "error", "reason": f"File already exists: {dest}"}
    content = (
        "---\n"
        f"status: {args.status}\n"
        f"authority: {args.authority}\n"
        f"source: {args.source}\n"
        f"created_at: {today}\n"
        f"updated_at: {today}\n"
        f"review_needed: {args.review_needed or 'no'}\n"
        "---\n\n"
        f"# {args.title}\n\n"
        "## Summary\n\n"
        f"{args.title}\n\n"
        "## Note\n\n"
        f"{args.body.strip()}\n\n"
        "## Intended use\n\n"
        f"{args.intended_use}\n"
    )
    dest.write_text(content, encoding="utf-8")
    return {
        "status": "success",
        "operation": "create_note_file",
        "written_to": str(dest),
        "note_title": args.title,
        "warnings": [
            "This note is not source of truth by default.",
            "No promotion to Knowledge Hub was performed.",
        ],
    }


def mark_capture_candidate(args: argparse.Namespace) -> dict:
    target = Path(args.target_file)
    if not target.exists():
        return {"status": "error", "reason": f"Target file not found: {target}"}
    note = (
        "\n\n---\n"
        "## Capture candidate marker\n\n"
        "- Status: capture_candidate\n"
        "- Authority: candidate\n"
        f"- Source: {args.source}\n"
        "- Review needed: yes\n"
        "- Promotion status: not_promoted\n"
        "\nThis marker does not promote the note to Knowledge Hub.\n"
    )
    with target.open("a", encoding="utf-8") as f:
        f.write(note)
    return {
        "status": "success",
        "operation": "mark_capture_candidate",
        "updated_file": str(target),
        "warnings": ["Capture candidate is not promotion."],
    }


def archive_note(args: argparse.Namespace) -> dict:
    nb = Path(args.notebook_path)
    ensure_notebook(nb)
    target = Path(args.target_file)
    if not target.exists():
        return {"status": "error", "reason": f"Target file not found: {target}"}
    dest = nb / "archive" / target.name
    if dest.exists() and not args.force:
        return {"status": "error", "reason": f"Archive target already exists: {dest}"}
    shutil.move(str(target), str(dest))
    return {
        "status": "success",
        "operation": "archive_note",
        "archived_to": str(dest),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", required=True, choices=[
        "init_notebook",
        "append_inbox_note",
        "create_note_file",
        "mark_capture_candidate",
        "archive_note",
    ])
    parser.add_argument("--notebook-path", default="")
    parser.add_argument("--title", default="Untitled note")
    parser.add_argument("--status", default="idea")
    parser.add_argument("--authority", default="personal")
    parser.add_argument("--source", default="self")
    parser.add_argument("--intended-use", default="personal reference")
    parser.add_argument("--review-needed", default="no")
    parser.add_argument("--body", default="")
    parser.add_argument("--target-file", default="")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.operation in {"init_notebook", "append_inbox_note", "create_note_file", "archive_note"}:
        if not args.notebook_path:
            print(json.dumps({"status": "error", "reason": "notebook_path is required"}, ensure_ascii=False, indent=2))
            return

    if args.operation == "init_notebook":
        nb = Path(args.notebook_path)
        ensure_notebook(nb)
        result = {"status": "success", "operation": "init_notebook", "path": str(nb)}
    elif args.operation == "append_inbox_note":
        result = append_inbox(args)
    elif args.operation == "create_note_file":
        result = create_note_file(args)
    elif args.operation == "mark_capture_candidate":
        result = mark_capture_candidate(args)
    elif args.operation == "archive_note":
        result = archive_note(args)
    else:
        result = {"status": "error", "reason": "unknown operation"}

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
