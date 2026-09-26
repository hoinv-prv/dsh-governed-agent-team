#!/usr/bin/env python3
"""Install AND upgrade ONE Standard Pack package into a project that already has AIWS.

Counterpart of `build_standard_pack_package.py` (which builds the package this tool consumes) and
the executable form of `install_guide.md` — the destinations come from that builder's `INSTALL_MAP`,
never from a second hand-written list, so "where the payload lands" has one definition
(Standard_Pack_Contract_Spec_MVP §7.2 / §12; tooling_authoring_conventions Rule 6).

    py .ai-work/tooling/install_standard_pack.py --package <pkg-dir> --target <project-root>
    py .ai-work/tooling/install_standard_pack.py --package <pkg-dir> --target <project> --dry-run

ORDER IS THE CONTRACT (§9.3): **every guard runs before a single byte is written**. A refusal
therefore leaves the target byte-identical — "cài dở dang tệ hơn không cài". `--dry-run` stops right
after the guards and prints the same plan the real run would apply.

WHAT IT DOES, and why each destination is what it is:

  payload/standard_pack/        -> <target>/.ai-work/standard_pack/            (pack-owned tree, §8.1)
  payload/standard_pack_wiki/   -> <target>/.ai-work/wiki_sources/aiws_meta/standard_pack/   (§12)
  payload/wiki_source_profiles/ -> <target>/.ai-work/wiki_sources/profiles/    (MERGE, never overwrite)
  areas/<A>/skills/<name>/      -> <target>/.claude/skills/<name>/             (§7.2)
  then: rebuild the `aiws` preset index, and pin `standard_pack: {id, version}` in
        <target>/.ai-work/project_profile.yml, INSIDE the `AIWS:BEGIN` block (§9).

UPGRADE IS THE SAME COMMAND (§9.1: never automatic, always a human running it with a new package).
The pack tree is REPLACED — an asset removed from the pack must disappear from the project, or the
project keeps following a checklist the pack owner retired. "Replaced" is implemented as a precise
apply plus deletion of what the package no longer ships, not as rmtree-and-copy: a wholesale rewrite
reports every file as changed on a CRLF checkout and buries the real delta (measured downstream,
IR-2026-08-15 F5 / CR-AIWS-2026-08-073 C2). The observable end state is identical; the diff is not.

THREE THINGS IT REFUSES TO DO SILENTLY:

  * install onto a project whose AIWS is older than the pack's `aiws_min_version`, or whose AIWS
    version cannot be determined at all (§9.3 — a guard that cannot read its input is off, so it
    stops instead: same halt-and-ask contract as `lookup_wiki_source.py --system`);
  * overwrite a `.claude/skills/<name>/` this pack did not install (§7.2 — two skills with one name
    are two capabilities fighting over one trigger, and the loser vanishes without a trace);
  * replace a DIFFERENT pack already installed in the target (`pack_id` mismatch): which pack a
    project follows is a human decision, not a copy step.

Provenance for the skill rule needs no receipt file: the skills this pack installed are exactly the
skills in the pack tree that is *currently* installed at `<target>/.ai-work/standard_pack/`, read
BEFORE that tree is replaced. The installed tree is the record.

Exit codes: 0 OK (or a clean dry run), 2 refusal / failure.
"""
from __future__ import annotations

import argparse
import io
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    PROJECT_PROFILE_BLOCK_BEGIN,
    PROJECT_PROFILE_BLOCK_END,
    PROJECT_PROFILE_SCHEMA_VERSION,
    parse_frontmatter,
    read_text,
)
# ONE definition of "where does payload/<x> land" (Rule 6) — the builder owns it.
from build_standard_pack_package import INSTALL_MAP  # noqa: E402
# ONE pack.yml parser and ONE AIWS-version detector, both already used by lint (Rule 6).
from lint_standard_pack import (  # noqa: E402
    PACK_REQUIRED_KEYS,
    as_list,
    detect_aiws_version,
    parse_yaml,
    version_tuple,
)
# The precise-apply + index-rebuild path preset wiki already uses (§12: "cùng đường đi mà preset
# wiki của AIWS đang dùng"). Not re-implemented here.
from build_preset_wiki import build_in_project, sync_metas_from_payload  # noqa: E402

DEST = {name: dest for name, dest, _ in INSTALL_MAP}
PACK_SECTION = "standard_pack"
META_SECTION = "standard_pack_wiki"
PROFILE_SECTION = "wiki_source_profiles"
SKILLS_DEST = ".claude/skills"
PROFILE_NAME = "project_profile.yml"


def _out() -> None:
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass


def _txt(value) -> str:
    return "" if value is None else str(value).strip()


# ---------- file-level diff (the unit the report speaks in) ----------

class TreePlan:
    """What a section's apply will do — computed before anything is written, printed either way."""

    def __init__(self, label: str) -> None:
        self.label = label
        self.added: "list[str]" = []
        self.updated: "list[str]" = []
        self.unchanged: "list[str]" = []
        self.removed: "list[str]" = []

    @property
    def writes(self) -> int:
        return len(self.added) + len(self.updated) + len(self.removed)

    def line(self) -> str:
        return (f"  {self.label:<34s} {len(self.added):3d} added · {len(self.updated):3d} updated · "
                f"{len(self.unchanged):3d} unchanged · {len(self.removed):3d} removed")


def files_under(root: Path) -> "dict[str, Path]":
    """{relative POSIX path: Path} for every file under root ({} when absent).

    Rule 12: keyed and ordered by the POSIX relative path — `sorted(Path)` is case-folded on Windows
    and case-sensitive on POSIX, and this ordering decides the order of the report.
    """
    if not root.is_dir():
        return {}
    return {p.relative_to(root).as_posix(): p
            for p in sorted(root.rglob("*"), key=lambda x: x.relative_to(root).as_posix())
            if p.is_file()}


def same_content(src: Path, dst: Path) -> bool:
    """EOL-INSENSITIVE comparison, falling back to bytes for anything that is not UTF-8 text.

    A file that differs only in line endings must not count as changed: the package ships LF, a
    Windows checkout may hold CRLF, and copying on that difference manufactures exactly the EOL churn
    CR-AIWS-2026-08-073 C1 removed.
    """
    try:
        a = read_text(src).replace("\r\n", "\n").replace("\r", "\n")
        b = read_text(dst).replace("\r\n", "\n").replace("\r", "\n")
        return a == b
    except (UnicodeDecodeError, OSError):
        try:
            return src.read_bytes() == dst.read_bytes()
        except OSError:
            return False


def plan_tree(label: str, src: Path, dst: Path, *, delete_extraneous: bool) -> TreePlan:
    plan = TreePlan(label)
    have, want = files_under(dst), files_under(src)
    for rel, s in want.items():
        d = have.get(rel)
        if d is None:
            plan.added.append(rel)
        elif same_content(s, d):
            plan.unchanged.append(rel)
        else:
            plan.updated.append(rel)
    if delete_extraneous:
        plan.removed = [rel for rel in have if rel not in want]
    return plan


def apply_tree(src: Path, dst: Path, plan: TreePlan) -> None:
    for rel in plan.added + plan.updated:
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src / rel, target)          # bytes as shipped: the package is LF
    for rel in plan.removed:
        try:
            (dst / rel).unlink()
        except OSError:
            pass
    _prune_empty_dirs(dst)


def _prune_empty_dirs(root: Path) -> None:
    """Remove directories left empty by a deletion, deepest first. Never removes `root` itself."""
    if not root.is_dir():
        return
    for d in sorted((p for p in root.rglob("*") if p.is_dir()),
                    key=lambda p: len(p.relative_to(root).parts), reverse=True):
        try:
            next(d.iterdir())
        except StopIteration:
            try:
                d.rmdir()
            except OSError:
                pass
        except OSError:
            pass


# ---------- pack / package shape ----------

def read_pack_yml(pack_root: Path) -> dict:
    """Parse + validate `pack.yml` (§2.1) with the lint tool's parser — one YAML reader."""
    data = parse_yaml(read_text(pack_root / "pack.yml"))
    if not isinstance(data, dict):
        raise ValueError("pack.yml did not parse to a mapping")
    missing = [k for k in PACK_REQUIRED_KEYS
               if not _txt(data.get(k)) and not (k == "areas" and as_list(data.get("areas")))]
    if missing:
        raise ValueError("pack.yml is missing required key(s): " + ", ".join(missing) + " (§2.1)")
    return data


def pack_skills(pack_root: Path) -> "dict[str, Path]":
    """{skill name: its directory} for `areas/<A>/skills/<name>/SKILL.md` (§7.1).

    The directory name IS the skill name (and must equal `name:` in the frontmatter — that equality
    is `lint_standard_pack`'s business, not this tool's).
    """
    out: "dict[str, Path]" = {}
    areas = pack_root / "areas"
    if not areas.is_dir():
        return out
    for area in sorted((d for d in areas.iterdir() if d.is_dir()), key=lambda p: p.name):
        skills = area / "skills"
        if not skills.is_dir():
            continue
        for sd in sorted((d for d in skills.iterdir() if d.is_dir()), key=lambda p: p.name):
            if (sd / "SKILL.md").is_file():
                out[sd.name] = sd
    return out


# ---------- the pin (§9, third version layer) ----------

def read_pin(profile: Path) -> dict:
    """`standard_pack: {id, version}` as currently written, or {} when there is none."""
    if not profile.is_file():
        return {}
    try:
        meta, _ = parse_frontmatter("---\n" + read_text(profile) + "\n---\n")
    except Exception:  # noqa: BLE001 — an unreadable profile is a guard's problem, not the reader's
        return {}
    pin = meta.get("standard_pack") if isinstance(meta, dict) else None
    return {k: _txt(v) for k, v in pin.items()} if isinstance(pin, dict) else {}


def upsert_pin(profile: Path, pack_id: str, pack_version: str) -> str:
    """Write the pin INSIDE the `AIWS:BEGIN` block. Returns 'added' | 'updated' | 'unchanged'.

    Line-addressed like `_common.profile_upsert`, and for the same reason: parsing this file and
    dumping it back collapses it (measured: 2470 B -> 124 B, all 30 comment lines gone). It is not
    `profile_upsert` itself because that function writes SCALARS, and the pin is a two-key mapping —
    §9 fixes its shape, so it is written as a block, not flattened into a string.

    Everything outside the AIWS block is the project's and is never touched.
    """
    current = read_pin(profile)
    if current.get("id") == pack_id and current.get("version") == pack_version:
        return "unchanged"

    raw = profile.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    if bom:
        raw = raw[3:]
    lines = raw.decode("utf-8").split("\n")
    block = ["standard_pack:   # pinned by install_standard_pack.py (§9, third version layer)",
             f"  id: {pack_id}",
             f"  version: {pack_version}"]

    at = next((i for i, ln in enumerate(lines)
               if ln.strip().startswith("standard_pack:") and not ln.startswith((" ", "\t"))
               and not ln.lstrip().startswith("#")), None)
    if at is not None:
        end = at + 1
        while end < len(lines):
            s = lines[end]
            if not s.strip():                       # a blank line inside the block ends the value
                break
            if not s.startswith((" ", "\t")):       # dedent: next top-level key or comment
                break
            end += 1
        lines[at:end] = block
        status = "updated"
    else:
        begin_at = next((i for i, ln in enumerate(lines)
                         if ln.strip().startswith(PROJECT_PROFILE_BLOCK_BEGIN)), None)
        if begin_at is None:
            while lines and not lines[-1].strip():
                lines.pop()
            lines += ["",
                      f"{PROJECT_PROFILE_BLOCK_BEGIN}{PROJECT_PROFILE_SCHEMA_VERSION}",
                      "# Keys AIWS manages. Everything OUTSIDE this block is yours and is never "
                      "overwritten."]
            lines += block + [PROJECT_PROFILE_BLOCK_END, ""]
        else:
            end_at = next((i for i in range(begin_at + 1, len(lines))
                           if lines[i].strip() == PROJECT_PROFILE_BLOCK_END), None)
            if end_at is None:
                raise ValueError(f"{profile}: AIWS:BEGIN without a matching AIWS:END")
            lines[end_at:end_at] = block
        status = "added"

    out = "\n".join(lines).encode("utf-8")
    profile.write_bytes((b"\xef\xbb\xbf" + out) if bom else out)
    return status


# ---------- guards (§9.3) ----------

class Refused(Exception):
    """A guard said no. Raised only BEFORE anything is written."""


def guard_package(pkg: Path) -> "tuple[Path, dict]":
    if not pkg.is_dir():
        raise Refused(f"package directory not found: {pkg}")
    pack_root = pkg / "payload" / PACK_SECTION
    if not (pack_root / "pack.yml").is_file():
        raise Refused(f"not a Standard Pack package: {pkg}\n"
                      f"       expected payload/{PACK_SECTION}/pack.yml (build one with "
                      f"build_standard_pack_package.py)")
    try:
        meta = read_pack_yml(pack_root)
    except Exception as exc:  # noqa: BLE001
        raise Refused(f"{exc} ({pack_root / 'pack.yml'})") from exc
    return pack_root, meta


def guard_target(target: Path, meta: dict) -> str:
    """`.ai-work/`, the AIWS version, and the profile — all read before any write."""
    if not (target / ".ai-work").is_dir():
        raise Refused(f"the target has no .ai-work/: {target}\n"
                      f"       AIWS is not installed there. A Standard Pack installs ON TOP of "
                      f"AIWS; install AIWS first (§9.3).")
    have = detect_aiws_version(target)
    want = _txt(meta.get("aiws_min_version"))
    if not have:
        raise Refused(
            f"cannot determine the AIWS version of {target}\n"
            f"       looked in .ai-work/install_templates/VERSION and product/aiws_version.md. "
            f"This pack requires AIWS >= {want} (§9.3) and a guard that cannot read its input is a "
            f"guard that is off — so this stops instead of guessing.")
    ht, wt = version_tuple(have), version_tuple(want)
    if ht is None or wt is None:
        raise Refused(f"unreadable version(s): target AIWS={have!r}, aiws_min_version={want!r}")
    if ht < wt:
        raise Refused(f"AIWS too old: the target runs {have}, this pack requires >= {want} "
                      f"(pack.yml > aiws_min_version, §9.3).\n"
                      f"       Nothing was written. Upgrade AIWS first, or install an older pack.")
    if not (target / ".ai-work" / PROFILE_NAME).is_file():
        raise Refused(f"the target has no .ai-work/{PROFILE_NAME}\n"
                      f"       the pack pin (§9) lives in it. Create it first:\n"
                      f"       py .ai-work/tooling/project_profile.py init")
    return have


def guard_same_pack(target: Path, meta: dict) -> dict:
    """An already-installed pack must be THE SAME pack (that is an upgrade); another pack is not."""
    installed = target / ".ai-work" / PACK_SECTION
    if not (installed / "pack.yml").is_file():
        return {}
    try:
        cur = parse_yaml(read_text(installed / "pack.yml")) or {}
    except Exception:  # noqa: BLE001 — a damaged installed pack.yml is still "something is there"
        cur = {}
    cur_id, new_id = _txt(cur.get("pack_id")), _txt(meta.get("pack_id"))
    if cur_id and cur_id != new_id:
        raise Refused(
            f"the target already has a DIFFERENT Standard Pack installed: `{cur_id}` "
            f"{_txt(cur.get('pack_version'))} at {installed}\n"
            f"       this package carries `{new_id}` {_txt(meta.get('pack_version'))}. Installing "
            f"two packs at once is undefined (§13.4) and replacing one with another is a human "
            f"decision — remove the old pack deliberately, then re-run.")
    return cur


def guard_skills(target: Path, new_skills: "dict[str, Path]",
                 ours: "set[str]") -> "list[str]":
    """§7.2 — a name collision with a skill this pack did not install stops the install."""
    clashes = []
    for name in sorted(new_skills):
        dst = target / SKILLS_DEST / name
        if dst.exists() and name not in ours:
            clashes.append(name)
    if clashes:
        raise Refused(
            "skill name collision — NOTHING was written (§7.2):\n"
            + "".join(f"       · {target / SKILLS_DEST / n}\n" for n in clashes)
            + "       These skills already exist in the target and were not installed by this pack.\n"
              "       Two skills with one name are two capabilities fighting over one trigger and\n"
              "       the loser disappears without a trace, so this tool never overwrites one.\n"
              "       Ask the human: rename the project's skill, rename the pack's, or drop one.")
    return clashes


# ---------- install ----------

def install(pkg: Path, target: Path, dry_run: bool) -> int:
    pack_root, meta = guard_package(pkg)
    pack_id, pack_version = _txt(meta["pack_id"]), _txt(meta["pack_version"])
    aiws_version = guard_target(target, meta)
    installed_meta = guard_same_pack(target, meta)

    new_skills = pack_skills(pack_root)
    # Provenance WITHOUT a receipt file: whatever the currently-installed pack tree ships is what
    # this tool put in .claude/skills/ last time. Read BEFORE the tree is replaced.
    ours = set(pack_skills(target / ".ai-work" / PACK_SECTION))
    guard_skills(target, new_skills, ours)

    ai_work = target / ".ai-work"
    meta_src = pkg / "payload" / META_SECTION
    prof_src = pkg / "payload" / PROFILE_SECTION

    print(f"Standard Pack install — {pack_id} {pack_version} ({_txt(meta.get('title'))})")
    print(f"  package:      {pkg}")
    print(f"  target:       {target}  (AIWS {aiws_version} >= aiws_min_version "
          f"{_txt(meta.get('aiws_min_version'))})")
    if installed_meta:
        print(f"  installed:    {_txt(installed_meta.get('pack_id'))} "
              f"{_txt(installed_meta.get('pack_version'))} → UPGRADE")
    else:
        print("  installed:    (none) → FRESH INSTALL")

    # ---- plans (nothing is written yet) ----
    plans = []
    tree_plan = plan_tree(f"{DEST[PACK_SECTION]}/", pack_root, ai_work / PACK_SECTION,
                          delete_extraneous=True)
    plans.append(tree_plan)

    meta_dst = ai_work / "wiki_sources" / "aiws_meta" / PACK_SECTION
    meta_plan = plan_tree(f"{DEST[META_SECTION]}/", meta_src, meta_dst, delete_extraneous=True)
    plans.append(meta_plan)

    prof_plan = TreePlan(f"{DEST[PROFILE_SECTION]}/")
    for rel, src in files_under(prof_src).items():
        dst = ai_work / "wiki_sources" / "profiles" / rel
        # MERGE, never overwrite: the profiles directory belongs to the project (§2 of the guide).
        (prof_plan.added if not dst.exists() else prof_plan.unchanged).append(rel)
    plans.append(prof_plan)

    skill_plans = {name: plan_tree(f"{SKILLS_DEST}/{name}/", d, target / SKILLS_DEST / name,
                                   delete_extraneous=True)
                   for name, d in new_skills.items()}
    dropped_skills = sorted(ours - set(new_skills))

    profile_path = ai_work / PROFILE_NAME
    pin_now = read_pin(profile_path)
    pin_status = ("unchanged" if pin_now.get("id") == pack_id
                  and pin_now.get("version") == pack_version
                  else ("updated" if pin_now else "added"))

    print("\nPlan (file-level):")
    for p in plans:
        print(p.line())
    for name in sorted(skill_plans):
        print(skill_plans[name].line())
    for name in dropped_skills:
        print(f"  {SKILLS_DEST + '/' + name + '/':<34s} left in place — this pack no longer ships "
              f"it (§7.2: removing an installed skill is the project's decision)")
    print(f"  {'project_profile.yml standard_pack':<34s} pin {pin_status}: "
          f"{pin_now.get('id') or '—'}@{pin_now.get('version') or '—'} → {pack_id}@{pack_version}")

    if dry_run:
        total = sum(p.writes for p in plans) + sum(p.writes for p in skill_plans.values())
        print(f"\nDRY RUN — nothing written. {total} file operation(s) would be applied, "
              f"plus the pin ({pin_status}) and an `aiws` index rebuild.")
        return 0

    # ---- apply (guards are behind us) ----
    print()
    apply_tree(pack_root, ai_work / PACK_SECTION, tree_plan)
    print(f"applied {DEST[PACK_SECTION]}/ — the pack tree is REPLACED (§8.1): "
          f"{len(tree_plan.removed)} file(s) the package no longer ships were deleted")

    # Metas: the shipped precise apply (write only what differs), staged so the bundle lands in its
    # own `standard_pack/` group inside aiws_meta/ (§12) rather than at the root of it.
    if files_under(meta_src):
        with tempfile.TemporaryDirectory(prefix="stdpack-metas-") as tmp:
            staged = Path(tmp) / PACK_SECTION
            shutil.copytree(meta_src, staged)
            sync_metas_from_payload(Path(tmp), target)
    # ...and deletion, which the shared precise apply deliberately does not do: for a project's own
    # aiws_meta a stale file is a human decision, but THIS group mirrors a pack-owned tree, so a meta
    # whose asset was removed must go with it — otherwise lookups keep answering with a dead locator.
    for rel in meta_plan.removed:
        try:
            (meta_dst / rel).unlink()
        except OSError:
            pass
    if meta_plan.removed:
        print(f"removed {len(meta_plan.removed)} meta(s) whose asset the pack no longer ships")

    for rel in prof_plan.added:
        dst = ai_work / "wiki_sources" / "profiles" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(prof_src / rel, dst)
    if prof_plan.unchanged:
        print(f"kept the project's own {', '.join(prof_plan.unchanged)} (MERGE, never overwrite)")

    for name, plan in skill_plans.items():
        apply_tree(new_skills[name], target / SKILLS_DEST / name, plan)
    if new_skills:
        print(f"installed {len(new_skills)} skill(s) → {target / SKILLS_DEST}")

    status = upsert_pin(profile_path, pack_id, pack_version)
    print(f"pin {status} in {profile_path} (inside the AIWS:BEGIN block): "
          f"standard_pack.id={pack_id} version={pack_version}")

    rc = build_in_project(target)
    if rc != 0:
        print(f"error: the `aiws` index rebuild failed (rc={rc}). The files are installed; the "
              f"metas are NOT queryable until it succeeds:\n"
              f"       py .ai-work/tooling/build_preset_wiki.py --target {target}", file=sys.stderr)
        return 2

    print("\nReport:")
    for p in plans + [skill_plans[n] for n in sorted(skill_plans)]:
        print(p.line())
    print(f"  {'pin (project_profile.yml)':<34s} {status}")
    return 0


def main(argv: "list[str] | None" = None) -> int:
    _out()
    p = argparse.ArgumentParser(
        description="Install/upgrade one Standard Pack package into a project that has AIWS")
    p.add_argument("--package", required=True, metavar="DIR",
                   help="package directory built by build_standard_pack_package.py")
    p.add_argument("--target", required=True, metavar="DIR",
                   help="target project root (the one holding .ai-work/)")
    p.add_argument("--dry-run", action="store_true",
                   help="run every guard, print the plan, write nothing")
    ns = p.parse_args(argv)

    try:
        return install(Path(ns.package).resolve(), Path(ns.target).resolve(), ns.dry_run)
    except Refused as exc:
        print(f"refuse: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
