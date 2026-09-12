"""Derive a wiki `source_id` from a scanned file.

One template covers the common case; overrides cover historical drift. On the reference
corpus the drift is real and not cosmetic: most libraries in one system omit the system
segment while a few keep it, and the discriminating key turned out to need THREE parts.
Keyed on `(system, library)` alone, 215 ids could not be reproduced; adding `file_type`
brought that to 2 out of 8912.

Overrides are matched MOST SPECIFIC FIRST — a rule naming system+library+file_type beats
one naming system+library — so a general rule and a narrow exception can coexist without
ordering games in the file.
"""
from __future__ import annotations

from pathlib import Path

# `name` is the last resort and exists because drift is not always library-wide: one
# library here holds 136 ids in the system-bearing shape and 2 in the older shape. A
# (system, library, file_type) rule cannot express that, and NORMALISING the two would
# change identities that are already committed and referenced elsewhere.
_MATCH_KEYS = ("system", "library", "file_type", "name")


def _specificity(rule: dict) -> int:
    return sum(1 for k in _MATCH_KEYS if str(rule.get(f"match_{k}") or "").strip())


def _matches(rule: dict, *, system: str, library: str, file_type: str, name: str = "") -> bool:
    values = {"system": system.lower(), "library": library.upper(),
              "file_type": file_type, "name": name.upper()}
    for key in _MATCH_KEYS:
        want = str(rule.get(f"match_{key}") or "").strip()
        if not want:
            continue
        got = values[key]
        cmp = want.lower() if key in ("system", "file_type") else want.upper()
        if got != cmp:
            return False
    return True


def load_overrides_file(cfg, project_root: Path) -> None:
    """Load `system,library,file_type,template` rows declared outside the config.

    A corpus with dozens of drifted libraries would otherwise bury the readable part of
    the config under a wall of near-identical rules.
    """
    ref = str(getattr(cfg, "id_overrides_file", "") or "")
    if not ref:
        return
    path = Path(ref)
    if not path.is_absolute():
        path = project_root / path
    if not path.is_file():
        return
    import csv

    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.reader(fh):
            if not row or row[0].startswith("#") or len(row) < 4:
                continue
            if row[0].strip().lower() == "system":
                continue  # header
            cfg.id_overrides.append(
                {
                    "match_system": row[0].strip(),
                    "match_library": row[1].strip(),
                    "match_file_type": row[2].strip(),
                    "template": row[3].strip(),
                    "match_name": (row[4].strip() if len(row) > 4 else ""),
                }
            )


def template_for(cfg, *, system: str, library: str, file_type: str, name: str = "") -> str:
    best, best_score = cfg.id_template, -1
    for rule in cfg.id_overrides:
        if not _matches(rule, system=system, library=library, file_type=file_type, name=name):
            continue
        score = _specificity(rule)
        if score > best_score:
            best, best_score = str(rule.get("template") or cfg.id_template), score
    return best


def source_id(cfg, *, system: str, library: str, file_type: str, name: str,
              lib_path: str = "") -> str:
    """Render the id. Empty placeholders collapse so no `--` doubles appear.

    `{library}` renders EVERY directory level (`FQYO-FQYO`), because that is what the
    reference ids carry; the meta's own `library` field keeps the first level only.
    """
    template = template_for(cfg, system=system, library=library, file_type=file_type,
                            name=name)
    rendered = template.format(
        prefix=cfg.id_prefix,
        system=system.upper(),
        library=(lib_path or library).upper(),
        library_root=library.upper(),
        name=name.upper(),
        file_type=file_type,
    )
    parts = [p for p in rendered.split("-") if p]
    return "-".join(parts)
