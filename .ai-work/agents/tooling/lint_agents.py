#!/usr/bin/env python3
"""lint_agents.py — AI Agents Pack staging lint.

Two layers:
  * Governance-invariant floor (AP-CR-31, Detailed Design §6D) — ADVISORY (warn, exit 0 per OP-148-03):
    WARN when an instance's OWN `process/` dropped or weakened a `governance_invariant` step that its
    base process (`.blueprint_snapshot/process/` or the blueprint's resolved `process_docs`) carries.
  * Broad structural checks (AP-CR-40, ports DDR-30) — STRUCTURAL DEFECTS are ERRORS (exit 1):
    YAML tab-indentation + run_state quote-safety (F-04), JSONL parse, blueprint structure, instance
    structure, blueprint-ref resolves to an existing blueprint, instance memory/ matches the blueprint
    `memory_profile` (F-05 / AP-CR-36), run-folder completeness (advisory), no placeholder learning
    candidate in a completed run (F-09), and no Post-MVP folder (e.g. shared_workspaces) in the MVP tree.

Severity: structural defects -> ERRORS (return 1). The GI floor + soft gaps (missing profile, run-folder
gaps) stay warnings (return 0 if warn-only) so the advisory contract of AP-CR-31/OP-148-03 is preserved.

Stdlib-only (no-pip; regex/structural YAML, `json` for JSONL). Read-only — never mutates the corpus.
Integrated into /aiws-lint (`lint_all.py`): whole-tree runs this as a leg (CR-AIWS-2026-06-049 T1),
warnings pass through to the aggregate and structural-defect exits become aggregate errors
(CR-AIWS-2026-08-051); scoped finalize runs it when the footprint touches the pack.

Usage:  py tooling/lint_agents.py   (run from the pack root)
"""
import json
import re
import sys
from pathlib import Path


# --- CR-AIWS-2026-08-006 P2: desk-file dual-read helpers (new names primary) -----------------
def _desk_yaml(inst_dir):
    """desk.yaml (new) with dual-read fallback to legacy instance.yaml (P2 transition)."""
    p = inst_dir / "desk.yaml"
    return p if p.exists() else inst_dir / "instance.yaml"


def _snapshot_dir(inst_dir):
    """.atdb_snapshot (new; also the create target) with dual-read fallback to legacy
    .blueprint_snapshot (P2 transition)."""
    new = inst_dir / ".atdb_snapshot"
    old = inst_dir / ".blueprint_snapshot"
    return new if (new.exists() or not old.exists()) else old


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]          # the pack root (canonical: product/agents/ · installed: .ai-work/agents/; dev tree deleted — CR-039, comment refreshed CR-043 C3)
# CR-AIWS-2026-08-006 P2 dual-read (see run_agent.py)
INSTANCES = ROOT / "agents" / "task_desks"
if not INSTANCES.is_dir():
    INSTANCES = ROOT / "agents" / "instances"
BLUEPRINTS = ROOT / "agents" / "blueprints"

# A governance-invariant marker is exactly:  **governance_invariant** `<id>`
# (the bold form — so the explanatory legend prose, which writes the word inside backticks, never matches).
GI_RE = re.compile(r"\*\*governance_invariant\*\*\s+`([a-z_]+)`")

# run_state free-text keys whose values must be quote-safe (AP-CR-35 / F-04).
_FREE_TEXT_KEYS = ("notes", "stopped_reason")


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def _gi_ids(text: str) -> "set":
    return set(GI_RE.findall(text))


def _yaml_list(text: str, key: str) -> "list":
    """Read a simple 'key:\n  - item\n  - item' block (stdlib; no YAML lib). Returns the item strings."""
    m = re.search(rf"(?ms)^[ \t]*{re.escape(key)}:[ \t]*\n(.*?)(?=^\S|\Z)", text)
    if not m:
        return []
    return [x.strip().strip('"').strip("'") for x in re.findall(r"(?m)^[ \t]*-[ \t]*(\S.*?)[ \t]*$", m.group(1))]


def _blueprint_id_of(inst_dir: Path) -> str:
    m = re.search(r"(?m)^\s*blueprint_id:\s*(\S+)", _read(inst_dir / "blueprint_ref.yaml"))
    return m.group(1).strip().strip('"').strip("'") if m else ""


def _resolve_blueprint_by_id(root: Path, bid: str) -> "Path | None":
    """Resolve an ATDB dir by id, falling back to a blueprint's `previous_ids` alias.

    Mirrors `run_agent._resolve_blueprint_by_id` (CR-AIWS-2026-08-017): after the `aiws_*` rename a desk
    pinned to the OLD id must still resolve. `_shared` and other underscore dirs are never alias donors.
    """
    if not bid or bid == "null":
        return None
    direct = root / bid
    if direct.is_dir():
        return direct
    if not root.is_dir():
        return None
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        y = d / "blueprint.yaml"
        if not y.is_file():
            continue
        text = _read(y)
        inline = re.search(r"(?m)^[ \t]*previous_ids:[ \t]*\[([^\]]*)\]", text)
        if inline:
            prev = [x.strip().strip('"').strip("'") for x in inline.group(1).split(",")]
        else:
            m = re.search(r"(?ms)^[ \t]*previous_ids:[ \t]*\n(.*?)(?=^\S|\Z)", text)
            prev = re.findall(r"(?m)^[ \t]*-[ \t]*(\S+)", m.group(1)) if m else []
        if bid in [p.strip().strip('"').strip("'") for p in prev if p]:
            return d
    return None


def _resolve_blueprint_process(inst_dir: Path) -> "dict":
    """Fallback when no snapshot: resolve the current blueprint's process_docs set for the instance."""
    ref = _read(inst_dir / "blueprint_ref.yaml")
    bp = None
    mp = re.search(r"(?m)^\s*blueprint_path:\s*(\S+)", ref)
    if mp:
        val = mp.group(1).strip().strip('"').strip("'")
        cand = (inst_dir / val).resolve() if ("/" in val or "\\" in val or val.startswith(".")) else (BLUEPRINTS / val)
        if cand.is_dir():
            bp = cand
    if bp is None:
        mid = re.search(r"(?m)^\s*blueprint_id:\s*(\S+)", ref)
        if mid:
            bp = _resolve_blueprint_by_id(BLUEPRINTS, mid.group(1).strip().strip('"').strip("'"))
    if bp is None:
        return {}
    files = {}
    mm = re.search(r"(?ms)^process_docs:\s*\n(.*?)(?=^\S|\Z)", _read(bp / "blueprint.yaml"))
    if mm:
        for rel in re.findall(r":\s*(\S+\.md)\s*$", mm.group(1), re.M):
            p = (bp / rel).resolve()
            if p.is_file():
                files[p.name] = _read(p)
    pdir = bp / "process"
    if pdir.is_dir():
        for c in sorted(pdir.iterdir()):
            if (c.is_file() and c.suffix == ".md"
                    and not c.name.lower().startswith("readme") and c.name not in files):
                files[c.name] = _read(c)
    return files


# --- AP-CR-40 broad structural checks --------------------------------------

def _check_yaml(errors: list) -> None:
    """YAML hygiene (stdlib, conservative — NO full parse): tab-indentation (YAML forbids tabs) +
    run_state free-text scalar quote-safety (the F-04 class)."""
    for p in sorted(set(BLUEPRINTS.rglob("*.yaml")) | set(INSTANCES.rglob("*.yaml"))):
        rel = p.relative_to(ROOT)
        txt = _read(p)
        for i, line in enumerate(txt.splitlines(), 1):
            lead = line[:len(line) - len(line.lstrip())]
            if "\t" in lead:
                errors.append(f"{rel}:{i} YAML tab indentation (YAML forbids tabs)")
        if p.name == "run_state.yaml":
            for i, line in enumerate(txt.splitlines(), 1):
                m = re.match(r"^(\w+):[ \t]+(.*)$", line)
                if m and m.group(1) in _FREE_TEXT_KEYS:
                    val = m.group(2).strip()
                    if val and val != "null" and not val.startswith(('"', "'")) and ": " in val:
                        errors.append(f"{rel}:{i} run_state `{m.group(1)}` unquoted scalar contains ': ' "
                                      f"— emit via _yq (AP-CR-35 / F-04)")


def _check_jsonl(errors: list) -> None:
    for p in sorted(INSTANCES.rglob("*.jsonl")):
        rel = p.relative_to(ROOT)
        for i, line in enumerate(_read(p).splitlines(), 1):
            if line.strip():
                try:
                    json.loads(line)
                except Exception as e:
                    errors.append(f"{rel}:{i} invalid JSONL: {str(e)[:60]}")


def _check_blueprints(errors: list) -> None:
    if not BLUEPRINTS.is_dir():
        return
    for b in sorted(p for p in BLUEPRINTS.iterdir() if p.is_dir() and p.name != "_shared"):
        for req in ("blueprint.yaml", "profile.md", "skills/skill_index.yaml"):
            if not (b / req).exists():
                errors.append(f"blueprints/{b.name}: missing required {req}")


def _check_instances(errors: list, warnings: list) -> None:
    if not INSTANCES.is_dir():
        return
    for i in sorted(p for p in INSTANCES.iterdir() if p.is_dir()):
        name = i.name
        if not (_desk_yaml(i)).exists():
            errors.append(f"instances/{name}: missing instance.yaml")
        ref, snap = i / "blueprint_ref.yaml", i / "agent_design_snapshot.yaml"
        if not ref.exists() and not snap.exists():
            errors.append(f"instances/{name}: missing blueprint_ref.yaml AND agent_design_snapshot.yaml")
        bid = _blueprint_id_of(i) if ref.exists() else ""
        # alias-aware since CR-AIWS-2026-08-017: a desk pinned to a pre-rename id resolves via previous_ids
        bdir = _resolve_blueprint_by_id(BLUEPRINTS, bid) if bid and bid != "null" else None
        if bid and bid != "null" and bdir is None:
            errors.append(f"instances/{name}: blueprint_ref blueprint_id '{bid}' resolves to no blueprints/ dir (direct or via previous_ids alias)")
        # memory/ matches the blueprint memory_profile (AP-CR-36 / F-05)
        mem = i / "memory"
        prof = []
        if bdir is not None and (bdir / "blueprint.yaml").exists():
            prof = [Path(x).name for x in _yaml_list(_read(bdir / "blueprint.yaml"), "required_files")]
        if prof and mem.is_dir():
            disk = {p.name for p in mem.glob("*") if p.is_file() and p.name != "candidate_queue.jsonl"}
            miss = set(prof) - disk
            if miss:
                errors.append(f"instances/{name}: memory/ missing memory_profile files {sorted(miss)} (AP-CR-36)")
        # placeholder learning-candidate row in a COMPLETED run (F-09)
        comp = i / "workspace" / "completed_runs"
        if comp.is_dir():
            for lc in comp.rglob("learning_candidates.jsonl"):
                for j, line in enumerate(_read(lc).splitlines(), 1):
                    # placeholder = the template's angle-bracket sentinels, NOT a real `LC-001` id
                    if line.strip() and ("<instance_id>" in line or "RUN-YYYYMMDD" in line or "<learning content" in line):
                        errors.append(f"{lc.relative_to(ROOT)}:{j} placeholder learning-candidate row in a completed run (F-09)")
        # run-folder completeness (advisory)
        for sub in ("active_runs", "completed_runs"):
            base = i / "workspace" / sub
            if base.is_dir():
                for d in sorted(base.iterdir()):
                    if d.is_dir() and d.name.startswith("RUN-") and not (d / "run_state.yaml").exists():
                        warnings.append(f"{d.relative_to(ROOT)}: run folder missing run_state.yaml")
        # digest hint ↔ file pair-check (advisory — CR-AIWS-2026-07-017): a retrieval_hints entry
        # carrying digest_id must point at an existing memory/knowledge_digests file (pointer drift).
        hints = mem / "retrieval_hints.jsonl"
        if hints.exists():
            import json as _json
            for j, line in enumerate(_read(hints).splitlines(), 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    h = _json.loads(line)
                except Exception:
                    continue  # malformed hints stay F-04's concern (jsonl parse), not this check
                if h.get("digest_id"):
                    pth = (h.get("path") or "").strip()
                    tgt = (i / pth) if pth else (mem / "knowledge_digests")
                    if not pth or not tgt.exists():
                        warnings.append(
                            f"instances/{name}: retrieval_hints.jsonl:{j} digest hint "
                            f"'{h.get('digest_id')}' points at missing/absent path '{pth}' (CR-017 pair-check)")


def _check_run_close(warnings: list) -> None:
    """CR-AIWS-2026-07-015 T5 (advisory, WARNING-first — ERROR escalation is a separate explicit
    gate per AP-CR-40 pattern): a COMPLETED run must carry a reference trace — a filled
    used_references.md / output/references_used.md table row, a filled ARC §4A Selected References
    row, or an explicit 'no-references-needed: <reason>' declaration in the ARC.
    Scope: runs WITH run_state.yaml only (legacy no-run_state runs are R-6 exempt). TW-backed runs
    are located via run_index.jsonl — a READ-ONLY traversal outside the pack root (declared scope)."""
    if not INSTANCES.is_dir():
        return
    proj_root = ROOT.resolve().parents[1]

    def _has_table_row(p: Path) -> bool:
        if not p.exists():
            return False
        for ln in _read(p).splitlines():
            s = ln.strip()
            if s.startswith("|") and "---" not in s and s.strip("| ").strip() \
               and not s.lower().startswith(("| reference", "| input")) and "<" not in s and "(fill)" not in s:
                return True
        return False

    def _check_one(run_dir: Path, label: str) -> None:
        if not (run_dir / "run_state.yaml").exists():
            return  # legacy run — exempt (R-6)
        st = ""
        m = re.search(r"(?m)^status:\s*([a-z_]+)", _read(run_dir / "run_state.yaml"))
        if m:
            st = m.group(1)
        if st != "completed":
            return
        if _has_table_row(run_dir / "used_references.md") or _has_table_row(run_dir / "output" / "references_used.md"):
            return
        arc = _read(run_dir / "00_active_run_context.md")
        if "no-references-needed" in arc:
            return
        sel = arc.split("### Selected References", 1)
        if len(sel) == 2:
            block = sel[1].split("###", 1)[0]
            for ln in block.splitlines():
                s = ln.strip()
                if s.startswith("|") and "---" not in s and "(fill)" not in s \
                   and not s.lower().startswith("| intent") and s.strip("| ").strip():
                    return
        warnings.append(f"{label}: completed run has NO reference trace "
                        f"(used_references/references_used/ARC §4A empty and no 'no-references-needed' declaration) (CR-015 run-close)")

    for i in sorted(p for p in INSTANCES.iterdir() if p.is_dir()):
        for sub in ("active_runs", "completed_runs"):
            base = i / "workspace" / sub
            if base.is_dir():
                for d in sorted(base.iterdir()):
                    if d.is_dir() and d.name.startswith("RUN-"):
                        _check_one(d, str(d.relative_to(ROOT)))
        ridx = i / "workspace" / "run_index.jsonl"
        for ln in _read(ridx).splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            rel = (r.get("task_workspace") or "").replace("\\", "/")
            if rel:
                tw = (proj_root / rel)
                if tw.is_dir():
                    _check_one(tw, f"{i.name} → {rel}")


def _check_post_mvp(errors: list) -> None:
    for bad in ("shared_workspaces",):
        for d in ROOT.rglob(bad):
            if d.is_dir():
                errors.append(f"{d.relative_to(ROOT)}: Post-MVP folder '{bad}' must not be present in the MVP tree")


def _check_gi_floor(warnings: list) -> int:
    """AP-CR-31 governance-invariant floor — ADVISORY (warnings only)."""
    checked = 0
    if not INSTANCES.is_dir():
        return 0
    for inst_dir in sorted(p for p in INSTANCES.iterdir() if p.is_dir()):
        proc = inst_dir / "process"
        inst_md = {p.name: _read(p) for p in proc.glob("*.md")} if proc.is_dir() else {}
        if not inst_md:
            continue  # pre-fork / no instance process — nothing to compare
        snap = _snapshot_dir(inst_dir) / "process"
        if snap.is_dir():
            base = {p.name: _read(p) for p in snap.glob("*.md")}
            base_src = ".blueprint_snapshot/process"
        else:
            base = _resolve_blueprint_process(inst_dir)
            base_src = "blueprint process_docs"
        if not base:
            continue  # custom no-Blueprint (no base) — floor comparison N/A
        checked += 1
        for fname, btext in base.items():
            bids = _gi_ids(btext)
            if not bids:
                continue
            if fname not in inst_md:
                warnings.append(f"{inst_dir.name}: process/{fname} MISSING — base ({base_src}) carries "
                                f"governance_invariant {sorted(bids)}")
                continue
            dropped = bids - _gi_ids(inst_md[fname])
            if dropped:
                warnings.append(f"{inst_dir.name}: process/{fname} dropped/weakened governance_invariant "
                                f"{sorted(dropped)} (base {base_src})")
    return checked


def _check_blueprint_profiles(warnings: list) -> None:
    """CR-AIWS-2026-08-013 — WARN `blueprint_missing_executor_profile`.

    Invariant: every shipped blueprint declares an executor output-contract profile
    (`required_core` or `required_core_policy`). Without it, a desk switched to
    `executor: claude_subagent` meets an unsatisfiable contract and improvises a fold. The runtime
    guard in run_agent.py refuses such a start; this rule surfaces the same invariant WITHOUT
    needing a run, so the gap is visible before anyone flips a desk.
    """
    if not BLUEPRINTS.is_dir():
        return
    for bp in sorted(p for p in BLUEPRINTS.iterdir() if p.is_dir() and not p.name.startswith("_")):
        f = bp / "blueprint.yaml"
        if not f.is_file():
            continue  # another rule's finding
        if not re.search(r"(?m)^\s*(required_core|required_core_policy)\s*:", _read(f)):
            warnings.append(
                f"blueprint_missing_executor_profile: blueprints/{bp.name} declares no "
                "`required_core`/`required_core_policy` — a desk on executor `claude_subagent` "
                "would face an unsatisfiable output_contract (see agent_runtime_design.md §8E)")


def _changelog_versions(bp: Path) -> "list[str]":
    """Version headings of a blueprint changelog, newest first, in file order.

    Heading shape is `## <version> — <date>[ — <title>]`; non-version headings (`## Provenance`)
    are skipped, so "the newest version entry" means the topmost heading that names a version.
    """
    txt = _read(bp / "changelog.md")
    return re.findall(r"(?m)^##\s+(\d+(?:\.\d+)*)\s", txt)


def _check_blueprint_version_changelog(warnings: list) -> None:
    """CR-AIWS-2026-08-074 C5 — WARN `blueprint_version_changelog_mismatch` (DP-074-B = a: WARN now,
    ERROR one release later, once the C6 backfill has settled).

    Invariant: `blueprint_version` and the newest `changelog.md` entry name the SAME version.

    Why it matters, concretely: `/aiws-agent-upgrade` compares a desk's pinned version against the
    blueprint's to decide whether the desk is behind, and then presents the changelog as the WHY a
    HUMAN reconciles against (spec §4A). v1.2.0 changed three blueprints (CR-08-008/-012/-017) while
    `blueprint_version` stayed "0.1": the comparison said "no change" while the on-disk snapshot said
    DRIFT, and the text put in front of the HUMAN described only the 0.1 birth. The gate stayed open
    with nothing to decide on. Bumping the field alone would have restored the signal and left the
    explanation missing, so the rule ties the two together in BOTH directions:
      - entry present, field not bumped → the v1.2.0 shape, caught one step earlier;
      - field bumped, no entry          → a version the HUMAN cannot act on.

    LIMIT, stated plainly: this is a pairing check, not a content check. "blueprint.yaml changed
    therefore the version must change" needs a baseline to diff against, and lint has none on an
    installed tree (no release history, no git guarantee). An edit that touches neither the version
    nor the changelog still passes here. Closing that half needs a recorded content hash — a schema
    change, out of this CR's scope.
    """
    if not BLUEPRINTS.is_dir():
        return
    for bp in sorted(p for p in BLUEPRINTS.iterdir() if p.is_dir() and not p.name.startswith("_")):
        f = bp / "blueprint.yaml"
        if not f.is_file():
            continue  # another rule's finding
        m = re.search(r"(?m)^blueprint_version:\s*[\"']?([^\"'\s#]+)", _read(f))
        if not m:
            warnings.append(
                "blueprint_version_changelog_mismatch: blueprints/" + bp.name + " declares no "
                "`blueprint_version` — /aiws-agent-upgrade has nothing to compare a desk's pin against")
            continue
        ver = m.group(1)
        if not (bp / "changelog.md").is_file():
            warnings.append(
                "blueprint_version_changelog_mismatch: blueprints/" + bp.name + " is at version "
                + ver + " but has no changelog.md — the HUMAN reconcile gate would present no WHY "
                "(spec /aiws-agent-upgrade §4A)")
            continue
        vers = _changelog_versions(bp)
        if not vers:
            warnings.append(
                "blueprint_version_changelog_mismatch: blueprints/" + bp.name + " changelog.md has "
                "no version heading (expected `## " + ver + " — <date>`)")
        elif vers[0] != ver:
            warnings.append(
                "blueprint_version_changelog_mismatch: blueprints/" + bp.name + " declares "
                "blueprint_version " + ver + " but the newest changelog entry is " + vers[0]
                + " — bump the field and add the entry together, or /aiws-agent-upgrade shows a "
                "drift it cannot explain (CR-AIWS-2026-08-074 C5)")
        elif ver not in vers:
            warnings.append(
                "blueprint_version_changelog_mismatch: blueprints/" + bp.name + " version " + ver
                + " has no matching changelog entry")


def _desk_run_policy_raw(inst_dir: Path) -> str:
    return _read(_desk_yaml(inst_dir))


def _check_shim_desk_binding(warnings: list) -> None:
    """CR-AIWS-2026-08-044 C3 — WARN `shim_desk_binding_drift` + executors_allowed vocab.

    Invariant (CR-044 §3 C5i): dispatch handle == desk_id, shim 1:1 generated. Every desk whose
    allowed-executor set contains `claude_subagent` must have a generated shim
    `.claude/agents/<desk_id>.md` whose frontmatter `name:` equals the desk id and whose body points
    at THIS desk's path. Drift/absence is surfaced here without needing a run (same philosophy as
    `blueprint_missing_executor_profile`). Also validates `executors_allowed` values ⊆ vocab."""
    vocab = {"main_session", "claude_subagent"}
    shim_root = ROOT.parents[1] / ".claude" / "agents"
    for inst in sorted(p for p in INSTANCES.iterdir() if p.is_dir()) if INSTANCES.is_dir() else []:
        txt = _desk_run_policy_raw(inst)
        m = re.search(r"(?m)^[ \t]+executors_allowed:[ \t]*\[([^\]]*)\]", txt)
        allowed = ([v.strip().strip('"').strip("'") for v in m.group(1).split(",") if v.strip()]
                   if m else [])
        bad = [v for v in allowed if v not in vocab]
        if bad:
            warnings.append(
                f"executors_allowed_offvocab: task_desks/{inst.name} declares executors_allowed "
                f"values {bad} outside {sorted(vocab)} (CR-AIWS-2026-08-044 C1)")
        me = re.search(r"(?m)^[ \t]+executor:[ \t]*([^#\n]*?)[ \t]*(?:#.*)?$", txt)
        declared = (me.group(1).strip().strip('"').strip("'") if me else "")
        effective = allowed or ([declared] if declared else ["main_session"])
        if "claude_subagent" not in effective:
            continue
        shim = shim_root / f"{inst.name}.md"
        if not shim.is_file():
            warnings.append(
                f"shim_desk_binding_drift: task_desks/{inst.name} allows executor claude_subagent "
                f"but no shim .claude/agents/{inst.name}.md exists — regenerate via "
                "build_agent_shims.py (CR-AIWS-2026-08-044 C3)")
            continue
        stxt = _read(shim)
        if not re.search(rf"(?m)^name:\s*{re.escape(inst.name)}\s*$", stxt):
            warnings.append(
                f"shim_desk_binding_drift: .claude/agents/{inst.name}.md frontmatter `name:` does "
                f"not equal the desk id '{inst.name}' (CR-AIWS-2026-08-044 C3)")
        elif inst.name not in stxt.replace(shim.name, "", 1):
            warnings.append(
                f"shim_desk_binding_drift: .claude/agents/{inst.name}.md body carries no pointer to "
                f"desk '{inst.name}' (CR-AIWS-2026-08-044 C3)")


def _check_tier_config(warnings: list) -> None:
    """CR-AIWS-2026-08-045 — WARN `tiers_supported_invalid` + `provider_profile_invalid`.

    Registry (agents/execution_tiers.yaml) is OPTIONAL — absent = tiers unused, silent. Present →
    (a) default_provider must have a profile; (b) each provider profile maps EVERY layer-1 tier and
    its efforts ∈ that profile's effort_vocab; (c) each desk's tiers_supported keys ⊆ registry tiers
    and ceilings ∈ {low, medium, high}."""
    reg_path = ROOT / "agents" / "execution_tiers.yaml"
    if not reg_path.is_file():
        return
    txt = _read(reg_path)
    m = re.search(r"(?m)^default_provider:[ \t]*([^#\n]*?)[ \t]*(?:#.*)?$", txt)
    default_provider = (m.group(1).strip() if m else "")
    tiers: list = []
    providers: dict = {}
    sec = prov = ""
    for line in txt.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        body = line.split("#")[0].strip()
        if indent == 0:
            sec = body[:-1] if body.endswith(":") else ""
            prov = ""
            continue
        if sec == "tiers" and indent == 2 and body.endswith(":"):
            tiers.append(body[:-1].strip())
        elif sec == "provider_profiles":
            if indent == 2 and body.endswith(":"):
                prov = body[:-1].strip()
                providers[prov] = {"effort_vocab": [], "map": {}}
            elif prov and body.startswith("effort_vocab:"):
                mv = re.search(r"\[([^\]]*)\]", body)
                if mv:
                    providers[prov]["effort_vocab"] = [x.strip() for x in mv.group(1).split(",") if x.strip()]
            elif prov and indent >= 6:
                mm = re.match(r"^([A-Za-z0-9_\-]+):\s*\{\s*model:\s*[^,}]+,\s*effort:\s*([^,}]+)\s*\}\s*$", body)
                if mm:
                    providers[prov]["map"][mm.group(1)] = mm.group(2).strip()
    if not default_provider or default_provider not in providers:
        warnings.append(
            f"provider_profile_invalid: execution_tiers.yaml default_provider "
            f"'{default_provider or '(unset)'}' has no provider_profiles entry (CR-AIWS-2026-08-045)")
    for pname, pdata in providers.items():
        missing = [t for t in tiers if t not in pdata["map"]]
        if missing:
            warnings.append(
                f"provider_profile_invalid: provider '{pname}' maps no {missing} — every layer-1 tier "
                "needs a mapping (CR-AIWS-2026-08-045)")
        ev = pdata["effort_vocab"]
        for t, eff in pdata["map"].items():
            if ev and eff not in ev:
                warnings.append(
                    f"provider_profile_invalid: provider '{pname}' tier '{t}' effort '{eff}' is outside "
                    f"its effort_vocab {ev} (CR-AIWS-2026-08-045)")
    if INSTANCES.is_dir():
        for inst in sorted(p for p in INSTANCES.iterdir() if p.is_dir()):
            mt = re.search(r"(?m)^[ \t]*tiers_supported:[ \t]*\{([^}]*)\}", _desk_run_policy_raw(inst))
            if not mt:
                continue
            for pair in mt.group(1).split(","):
                if ":" not in pair:
                    continue
                k, _, v = pair.partition(":")
                k, v = k.strip().strip('"').strip("'"), v.strip().strip('"').strip("'")
                if tiers and k not in tiers:
                    warnings.append(
                        f"tiers_supported_invalid: task_desks/{inst.name} declares tier '{k}' not in "
                        f"the registry tiers {tiers} (CR-AIWS-2026-08-045)")
                if v.lower() not in ("low", "medium", "high"):
                    warnings.append(
                        f"tiers_supported_invalid: task_desks/{inst.name} tier '{k}' ceiling '{v}' "
                        "outside low|medium|high (CR-AIWS-2026-08-045)")


# --- CR-AIWS-2026-08-048: pack md-link integrity + dead in-repo path refs ---------------------
_DEAD_REF_ALLOWLIST = ("source:", "precedent", "provenance", "changelog", "formerly",
                       "retired", "deleted", "lịch sử", "đã xóa", "da xoa")
_INREPO_PATH_RE = re.compile(r"(?:development|product|\.ai-work)/[A-Za-z0-9_.\-/]+")


def _pack_md_surfaces():
    for base in (ROOT / "commands", ROOT / "docs"):
        if base.is_dir():
            for f in sorted(base.rglob("*.md"), key=lambda p: p.as_posix()):
                yield f


def _check_pack_md_links(warnings: list) -> None:
    """CR-AIWS-2026-08-048 C2 — WARN `pack_md_link_broken`.

    Every RELATIVE markdown link ending in .md inside the pack's commands/*.md + docs/**/*.md must
    resolve on disk. Before this rule, deleting a linked tree left the links silently broken (6 links
    survived the AIP-1040 audit with whole-tree lint at 0 errors)."""
    for f in _pack_md_surfaces():
        for i, line in enumerate(_read(f).splitlines(), 1):
            for m in re.finditer(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)", line):
                rel = m.group(1)
                if rel.startswith(("http://", "https://", "/")):
                    continue
                if not (f.parent / rel).exists():
                    warnings.append(
                        f"pack_md_link_broken: {f.relative_to(ROOT).as_posix()}:{i} link '{rel}' "
                        "does not resolve on disk (CR-AIWS-2026-08-048 C2)")


def _check_dead_path_refs(warnings: list) -> None:
    """CR-AIWS-2026-08-048 C3 — WARN `dead_path_ref` (allowlist provenance).

    In-repo path tokens (development/... · product/... · .ai-work/...) appearing in pack .md surfaces
    must exist on disk. Lines carrying provenance markers (_DEAD_REF_ALLOWLIST) and Revision History
    blocks are exempt; tokens containing placeholder characters (<>*{}$) are skipped. Goal: any future
    retire/delete of a tree surfaces every surviving ref at lint time (74 refs needed a MANUAL sweep
    after CR-039 — PO ruling OP-1041-02)."""
    proj = ROOT.parents[1]
    for f in _pack_md_surfaces():
        text = _read(f)
        # CR-AIWS-2026-08-060 C1 — doc-level provenance: a doc whose head declares itself
        # HISTORICAL (point-in-time record) describes the PAST; its in-repo paths are correct
        # history and editing them would falsify the record (lesson C11, CR-036 / F-07 AIP-1041).
        # Same principle as the line-level _DEAD_REF_ALLOWLIST, lifted to file scope.
        head = "\n".join(text.splitlines()[:10]).lower()
        if "status: historical" in head:
            continue
        in_rev = False
        for i, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            if low.startswith("## revision history"):
                in_rev = True
            if in_rev or any(k in low for k in _DEAD_REF_ALLOWLIST):
                continue
            # CR-AIWS-2026-08-071 C4 — anchor-mapping lines are EXPLANATIONS, not pointers.
            # The pack documents its own root anchor-agnostically ("`product/agents/` canonical ·
            # `.ai-work/agents/` when installed"). Such a line names BOTH anchors on purpose: it
            # teaches the reader which root applies where. Rewriting it to a single anchor would
            # DELETE the information. Exempt any line that carries a canonical-tree token and an
            # installed-tree token together.
            toks = [m.group(0) for m in _INREPO_PATH_RE.finditer(line)]
            if any(t.startswith((".ai-work/",)) for t in toks) and                any(t.startswith(("product/", "development/")) for t in toks):
                continue
            for m in _INREPO_PATH_RE.finditer(line):
                tok = m.group(0).rstrip(".,;:)]}\"'`")
                if any(ch in tok for ch in "<>*{}$") or "//" in tok:
                    continue  # placeholders/globs + '//' shorthand lists are not path tokens
                if not (proj / tok).exists():
                    warnings.append(
                        f"dead_path_ref: {f.relative_to(ROOT).as_posix()}:{i} in-repo path "
                        f"'{tok}' does not exist on disk (CR-AIWS-2026-08-048 C3; provenance "
                        "lines are allowlisted)")


# --- CR-AIWS-2026-08-035: active-surface dev-path guard ---------------------------------------
# Operational path prefixes into the retired dev tree that ACTIVE surfaces must not carry. The dev
# tree (development/ai_agents/) was RETIRED + DELETED (CR-AIWS-2026-08-039; git history =
# provenance), so ANY operational path into it is a broken reference by construction — a
# skill/command line that "runs" its tooling or follows its verb specs points at nothing.
# Historical citations to development/ai_agents/docs/ (design-source provenance in prose) stay
# allowed. (Comment refreshed by CR-AIWS-2026-08-043 C3; the guard VALUE is unchanged — CR-035.)
_DEV_OPERATIONAL = ("development/ai_agents/tooling/", "development/ai_agents/commands/")


def _check_active_surface_dev_paths(errors: list) -> None:
    """CR-AIWS-2026-08-035 — ERROR `active_surface_dev_operational_path`.

    Scans the pack's active surfaces (skills/**.md + commands/**.md, plus the project-level
    .claude/skills/aiws-agent/SKILL.md copy when resolvable) for operational paths into
    development/ai_agents/{tooling,commands}/ — a tree that no longer exists (deleted by
    CR-AIWS-2026-08-039), so every hit is a broken operational reference. docs/ provenance
    citations in prose stay allowed. (Docstring refreshed by CR-AIWS-2026-08-043 C3.)
    """
    surfaces = []
    for base in (ROOT / "skills", ROOT / "commands"):
        if base.is_dir():
            surfaces.extend(sorted(base.rglob("*.md"), key=lambda p: p.as_posix()))
    claude_copy = ROOT.parents[1] / ".claude" / "skills" / "aiws-agent" / "SKILL.md"
    if claude_copy.is_file():
        surfaces.append(claude_copy)
    for f in surfaces:
        try:
            rel = f.relative_to(ROOT.parents[1]).as_posix()
        except ValueError:
            rel = f.as_posix()
        for i, line in enumerate(_read(f).splitlines(), 1):
            if any(tok in line for tok in _DEV_OPERATIONAL):
                errors.append(
                    f"active_surface_dev_operational_path: {rel}:{i} carries an operational "
                    "development/ai_agents/{tooling,commands}/ path — the dev tree is provenance-only "
                    "(CR-AIWS-2026-08-035); point at the installed pack root instead")


def main() -> int:
    errors, warnings = [], []
    if not INSTANCES.is_dir():
        print("lint_agents: no instances dir — nothing to check")
        return 0
    # AP-CR-40 broad structural checks (errors fail the gate)
    _check_yaml(errors)
    _check_jsonl(errors)
    _check_blueprints(errors)
    _check_instances(errors, warnings)
    _check_blueprint_profiles(warnings)  # CR-AIWS-2026-08-013
    _check_blueprint_version_changelog(warnings)  # CR-AIWS-2026-08-074 C5
    _check_shim_desk_binding(warnings)   # CR-AIWS-2026-08-044 C3
    _check_tier_config(warnings)         # CR-AIWS-2026-08-045
    _check_pack_md_links(warnings)       # CR-AIWS-2026-08-048 C2
    _check_dead_path_refs(warnings)      # CR-AIWS-2026-08-048 C3
    _check_run_close(warnings)
    _check_post_mvp(errors)
    _check_active_surface_dev_paths(errors)  # CR-AIWS-2026-08-035
    # AP-CR-31 governance-invariant floor (advisory)
    gi_checked = _check_gi_floor(warnings)
    for e in errors:
        print(f"  [error] {e}")
    for w in warnings:
        print(f"  [warning] {w}")
    print(f"lint_agents: broad structural checks + governance-invariant floor "
          f"(GI checked {gi_checked} forked instance(s)) — errors={len(errors)} warnings={len(warnings)} "
          f"(GI floor + soft gaps advisory per AP-CR-31/OP-148-03; structural defects fail the gate per AP-CR-40)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
