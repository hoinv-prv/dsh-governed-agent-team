#!/usr/bin/env python3
"""Agent Runtime orchestrator (AI Agents Pack, staging) — thin wrapper.

Prepares state so the AI can ACT AS the agent at a task desk for one task:
materialize an Active Run Context (ARC), scaffold a run-folder (Phase C schema
+ additive run_state.yaml), track status, list/show runs, stop runs.

It does NOT call an LLM, does NOT act as the agent, does NOT auto-run/chain,
and NEVER writes confirmed_memory or anything outside the pack root.
Mirrors the thin-orchestrator shape of .ai-work/tooling/run_aip.py.

Subcommands (AP-CR-19 surface B; +AP-CR-22 list/memory; +AP-CR-25 --aip; +AP-CR-27 upgrade; +AP-CR-28 clone; +AP-CR-30 rename; +AP-CR-41 template conformance):
  start  <desk> [--task TEXT] [--slug SLUG] [--aip AIP-ID] [--strict-template]   create run + ARC (status=active)
  start  ... --plan-first          phase-1: draft run_plan.md, stop at awaiting_plan_confirm (CR-016)
  confirm-plan <desk> <run>    HUMAN confirms the plan -> active (records plan_confirmed_by/at)
  start  ... [--executor E] [--tier T]  CR-AIWS-2026-08-044/045: plan-time executor + execution tier for THIS dispatch
  resume <desk> <run_id>                      refresh ARC + show run_state
  extend <desk> <run_id> --step STEP-NN       CR-AIWS-2026-08-046: multi-step span — gate + step-brief for the NEXT consecutive step (state-prep only)
  status <desk> [run_id]                      show one run, or list runs (reconciles closed)
  stop   <desk> <run_id> [--reason TEXT]      mark stopped + move to completed_runs
  list                                            list task desks (id · blueprint · display_name · status · drift)
  memory <desk> [--full]                          show a task desk's confirmed memory (+ lessons/candidate counts)
  upgrade <desk> [--reconcile --to-version V --decisions "..."]   present blueprint drift; record HUMAN reconcile (AP-CR-27)
  clone  <source> --as "<display_name>" [--id NEWID] [--why "..."]    new task desk from an existing one (AP-CR-28)
  rename <source> --to NEWID [--name "N"] [--as "D"] [--why "..."]    rename task desk id (+folder) + previous_ids alias (AP-CR-30)

Desk args accept a FUZZY token (partial id / role word / display_name / a prior id via `previous_ids` after a
rename) — a unique match is required (AP-CR-22/23/30). Task desks declaring `policies.run_policy.aip_driven: true`
require `start --aip <id>` (AP-CR-25).

Run with `py run_agent.py ...` (bare `python` is broken on this machine).
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import shutil
import sys
from pathlib import Path

# UTF-8 stdout (cp932-safe), like AIWS tooling.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

# DEV_ROOT = the pack root  (this script lives in <pack_root>/tooling/, so parent.parent = the pack
#   root — product/agents/ (canonical) or .ai-work/agents/ (installed, single-track). The old
#   development/ai_agents/ tree was RETIRED + DELETED — CR-AIWS-2026-08-039; comment refreshed by
#   CR-AIWS-2026-08-043 C3.)
DEV_ROOT = Path(__file__).resolve().parent.parent
# CR-AIWS-2026-08-006 P2: desks live under agents/task_desks/ (formerly agents/instances/).
# Dual-read for the transition: prefer the new root; fall back to a legacy install.
_DESKS_NEW = DEV_ROOT / "agents" / "task_desks"
_DESKS_OLD = DEV_ROOT / "agents" / "instances"
TASK_DESKS = _DESKS_NEW if _DESKS_NEW.is_dir() else _DESKS_OLD
INSTANCES = TASK_DESKS  # legacy alias (P2 dual-read)


# --- CR-AIWS-2026-08-074 C7/C12: desk-root resolution is ALL-OR-NOTHING — diagnose it out loud ---
#
# `TASK_DESKS` above picks ONE root and `_all_instances()` iterates that one — there is no union,
# and the switch is on `task_desks/` EXISTING, not on it holding desks. So on a pre-P2 tree,
# creating a single desk under `task_desks/` (what INSTANCE_INITIALIZATION_GUIDE.md tells you to
# do) makes every desk under `instances/` unreachable at once. Nothing is deleted; `list` simply
# returns fewer desks, with no error. Silently answering with the wrong desk set is worse than
# stopping — hence REFUSE, not WARN, for the ambiguous cases (DP-074-F = a).
#
# Diagnosis is a pure function so probes can build fixture trees; enforcement happens once, at the
# CLI entry, covering every verb.

class DeskRootAmbiguous(RuntimeError):
    """CR-AIWS-2026-08-074 C12 — the desk root cannot be resolved unambiguously; a HUMAN decides."""


def _desks_in(d: Path) -> "list[Path]":
    """Desk directories under `d` — same criterion as `_all_instances()` (a desk is a directory
    holding desk.yaml, or legacy instance.yaml)."""
    if not d.is_dir():
        return []
    return [x for x in sorted(d.iterdir())
            if x.is_dir() and ((x / "desk.yaml").exists() or (x / "instance.yaml").exists())]


def desk_root_diagnosis(new=None, old=None) -> "tuple[str, str]":
    """CR-AIWS-2026-08-074 C12 — classify the desk-root situation BEFORE anything reads desks.

    Returns `(code, message)`:
      `"ok"`         — resolved to task_desks/ (migrated, or a tree with no desks yet). No message.
      `"legacy"`     — resolved to the legacy instances/ root. Message = the one-line C7 warning.
      `"both"`       — REFUSE: both roots hold desks. Never merged automatically (ids can collide).
      `"empty-new"`  — REFUSE: task_desks/ exists but is EMPTY while instances/ holds desks. This is
                       the trap already sprung — resolution has flipped to the empty root and every
                       real desk is invisible.

    Args default to the module constants; pass explicit roots to diagnose a fixture tree.
    """
    new = _DESKS_NEW if new is None else Path(new)
    old = _DESKS_OLD if old is None else Path(old)
    in_new, in_old = _desks_in(new), _desks_in(old)

    if in_new and in_old:
        return ("both", (
            "desk root is AMBIGUOUS — refusing rather than guessing." "\n"
            "  " + str(new) + "  holds " + str(len(in_new)) + " desk(s): "
            + ", ".join(d.name for d in in_new) + "\n"
            "  " + str(old) + "  holds " + str(len(in_old)) + " desk(s): "
            + ", ".join(d.name for d in in_old) + "\n"
            "  Only ONE root is ever read (task_desks/ wins when it exists), so continuing would" "\n"
            "  silently hide the legacy set. Two desks may also share an id." "\n"
            "  → A HUMAN must reconcile: `aiws-pkg upgrade` step 7c-bis, or move the desks by hand."))

    if in_old and new.is_dir() and not in_new:
        return ("empty-new", (
            "desk root resolves to an EMPTY directory while your desks live elsewhere." "\n"
            "  " + str(new) + "  exists but holds NO desk → this is the root that gets read" "\n"
            "  " + str(old) + "  holds " + str(len(in_old)) + " desk(s): "
            + ", ".join(d.name for d in in_old) + " → currently UNREACHABLE" "\n"
            "  Nothing has been deleted. Run the desk-dir migration (`aiws-pkg upgrade` step 7c-bis)" "\n"
            "  after removing the empty directory, and the desks come back."))

    if in_old:
        return ("legacy", (
            "legacy desk root in use: " + str(old) + " — the P2 name is agents/task_desks/ "
            "(CR-AIWS-2026-08-006). Run `aiws-pkg upgrade` step 7c-bis to migrate; until then, do "
            "NOT create a desk under task_desks/ — it would hide this whole set (CR-AIWS-2026-08-074)."))

    return ("ok", "")


def enforce_desk_root(stream=None) -> str:
    """CR-AIWS-2026-08-074 C7/C12 — REFUSE the ambiguous cases, WARN on the legacy branch.

    Called once per CLI invocation, before the verb runs (DP-074-F = a: every verb reads desks, so
    every verb is covered). Returns the diagnosis code for callers that want it.
    """
    code, msg = desk_root_diagnosis()
    if code in ("both", "empty-new"):
        raise DeskRootAmbiguous(msg)
    if code == "legacy":
        print("warning: " + msg, file=stream or sys.stderr)
    return code
BLUEPRINTS = DEV_ROOT / "agents" / "blueprints"
RUN_TEMPLATES = DEV_ROOT / "agents" / "templates" / "run"

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


def _baseline_dir(inst_dir):
    """CR-AIWS-2026-08-074 C9 (DP-074-E' = a) — the desk's BIRTH baseline, kept apart from the
    reconcile pointer above. New in this CR, so there is no legacy name to dual-read."""
    return inst_dir / ".atdb_baseline"


# CR-AIWS-2026-06-057 — project root (DEV_ROOT = the installed/canonical pack root, see above;
#   parent.parent = the project root that holds .ai-work/). Used to resolve an AIP's Task Workspace.
#   (Comment refreshed by CR-AIWS-2026-08-043 C3 — dev tree deleted per CR-039.)
_PROJECT_ROOT = DEV_ROOT.parent.parent

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-]{0,79}$")

# CR-AIWS-2026-06-057 — roots allowed for writes IN ADDITION to the pack root. An aip_driven run that
# reuses its driving AIP's Task Workspace allow-lists that TW here so the boundary guard permits writes
# into it (the TW lives under <project>/.ai-work/workspaces/, outside the pack root).
_EXTRA_ALLOWED_ROOTS: "list[Path]" = []


def _allow_root(p: Path) -> None:
    """CR-AIWS-2026-06-057 — register an additional root the boundary guard will permit writes into
    (e.g. an AIP Task Workspace). Idempotent-ish; resolves before storing."""
    r = p.resolve()
    if r not in _EXTRA_ALLOWED_ROOTS:
        _EXTRA_ALLOWED_ROOTS.append(r)


# --- boundary guard (refuse writes outside the pack root) --------------------
def _ensure_inside(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(DEV_ROOT.resolve())
        return resolved
    except ValueError:
        pass
    # CR-AIWS-2026-06-057 — also allow paths inside any explicitly registered extra root.
    for root in _EXTRA_ALLOWED_ROOTS:
        try:
            resolved.relative_to(root)
            return resolved
        except ValueError:
            continue
    raise SystemExit(
        f"error: {label} path escapes the pack-root boundary\n"
        f"  path: {resolved}\n  must be inside: {DEV_ROOT.resolve()}"
        + (f"\n  or one of: {', '.join(str(r) for r in _EXTRA_ALLOWED_ROOTS)}" if _EXTRA_ALLOWED_ROOTS else "")
    )


def _die(msg: str) -> "None":
    raise SystemExit(f"error: {msg}")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _write(p: Path, text: str) -> None:
    _ensure_inside(p, "write")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _now_id() -> str:
    return datetime.datetime.now().strftime("%Y%m%d-%H%M")


def _today() -> str:
    return datetime.date.today().isoformat()


def _slug(text: str) -> str:
    s = _SLUG_RE.sub("-", (text or "run").lower()).strip("-")
    return (s[:32] or "run")


def _all_instances() -> "list[Path]":
    if not INSTANCES.is_dir():
        return []
    return [d for d in sorted(INSTANCES.iterdir())
            if d.is_dir() and (_desk_yaml(d)).exists()]


def _instance_field(inst_dir: Path, key: str) -> str:
    return _yaml_get(_read(_desk_yaml(inst_dir)), key)


def _instance_display(inst_dir: Path) -> str:
    # AP-CR-23: person-name display_name is the HUMAN-facing label; fall back to the long
    # instance_name, then the id. instance_id stays the stable machine key.
    return (_instance_field(inst_dir, "display_name")
            or _instance_field(inst_dir, "instance_name")
            or inst_dir.name)


def _previous_ids_from_text(txt: str) -> "list[str]":
    """AP-CR-30 — parse instance.yaml `previous_ids` (rename aliases). Handles the inline-flow form the
    tool writes (`previous_ids: [a, b]`) and a defensive block form (`previous_ids:\\n  - a`). Stdlib-only."""
    m = re.search(r"(?m)^previous_ids:[ \t]*\[([^\]]*)\][ \t]*$", txt)
    if m:
        return [s.strip().strip('"').strip("'") for s in m.group(1).split(",") if s.strip()]
    m = re.search(r"(?m)^previous_ids:[ \t]*$\n((?:[ \t]+-[ \t]*\S.*\n?)+)", txt)
    if m:
        return [re.sub(r"^[ \t]+-[ \t]*", "", ln).strip().strip('"').strip("'")
                for ln in m.group(1).splitlines() if ln.strip()]
    return []


def _instance_previous_ids(inst_dir: Path) -> "list[str]":
    """AP-CR-30 — the instance's prior ids (alias). [] when never renamed."""
    return _previous_ids_from_text(_read(_desk_yaml(inst_dir)))


def _resolve_instance(token: str) -> str:
    """AP-CR-22/23/30 — resolve a fuzzy token (exact id, partial id, role word, display_name, or a prior
    id recorded in `previous_ids` after a rename) to a UNIQUE instance id, so HUMAN need not type the full
    compound id and old references still resolve. Ambiguous/none → _die."""
    token = (token or "").strip()
    if (INSTANCES / token).is_dir():
        return token
    t = token.lower()
    hits = []
    for d in _all_instances():
        disp = _instance_display(d).lower()
        prev = [p.lower() for p in _instance_previous_ids(d)]  # AP-CR-30: exact-match a renamed instance's old id
        if t in d.name.lower() or t == disp or t in disp or t in prev:
            hits.append(d.name)
    if len(hits) == 1:
        return hits[0]
    if not hits:
        _die(f"no task desk matches '{token}'. Try `list`.")
    _die(f"ambiguous task desk '{token}' → {', '.join(hits)}. Use the full id.")


def _instance_dir(instance: str) -> Path:
    resolved = _resolve_instance(instance)
    if not _ID_RE.match(resolved):
        _die(f"invalid instance id '{resolved}'")
    d = INSTANCES / resolved
    if not d.is_dir():
        _die(f"task desk not found: {d}")
    return d


def _instance_run_policy(inst_dir: Path) -> dict:
    """AP-CR-25 — indentation-tolerant read of nested policies.run_policy.{aip_driven,aip_template}
    (_yaml_get is flat/top-level only). Returns {} when not declared."""
    txt = _read(_desk_yaml(inst_dir))
    out: dict = {}
    # plan_first: CR-AIWS-2026-07-016; executor: CR-AIWS-2026-08-007 (main_session | claude_subagent);
    # executors_allowed: CR-AIWS-2026-08-044 C1 (inline list — absent → [executor]).
    for key in ("aip_driven", "aip_template", "plan_first", "executor", "executors_allowed"):
        m = re.search(rf"(?m)^[ \t]+{key}:[ \t]*([^#\n]*?)[ \t]*(?:#.*)?$", txt)
        if m:
            out[key] = m.group(1).strip().strip('"').strip("'")
    return out


# --- CR-AIWS-2026-08-044: dispatch activation (C0) + executor selection (C1/C2) --------------
PACK_CONFIG = DEV_ROOT / "pack_config.yaml"
_EXECUTOR_VOCAB = ("main_session", "claude_subagent")


def _dispatch_enabled() -> bool:
    """CR-AIWS-2026-08-044 C0 — project-level dispatch toggle. OPTIONAL file
    <pack-root>/pack_config.yaml, key `dispatch_enabled`. ABSENT file/key = ON (installing the
    pack IS the project's opt-in — DP-044-3); only an explicit false/no/off turns dispatch off.
    Gates `start`/`extend` ONLY — desk lifecycle verbs and read-only list/memory stay available."""
    val = _yaml_get(_read(PACK_CONFIG), "dispatch_enabled")
    return val.strip().lower() not in ("false", "no", "off")


def _die_dispatch_disabled(verb: str) -> None:
    _die(
        f"dispatch toggle (CR-AIWS-2026-08-044 C0): pack_config.yaml declares dispatch_enabled: false "
        f"— agent dispatch is OFF for this project, `{verb}` refused.\n"
        "  Desk lifecycle verbs (create/clone/upgrade/rename) and read-only list/memory stay available.\n"
        "  Re-enable: flip the key to true or delete pack_config.yaml. (no run-folder was created.)"
    )


def _executors_allowed(pol: dict) -> "list[str]":
    """CR-AIWS-2026-08-044 C1 — run_policy.executors_allowed (additive). Absent → [declared
    executor]; desk with no executor declared at all → [main_session] (backward-compatible)."""
    raw = (pol.get("executors_allowed") or "").strip()
    if raw:
        vals = [v.strip().strip('"').strip("'") for v in raw.strip("[]").split(",")]
        vals = [v for v in vals if v]
        if vals:
            return vals
    return [((pol.get("executor") or "").strip().lower() or "main_session")]


def _requested_executor(pol: dict, flag: str) -> str:
    """CR-AIWS-2026-08-044 C2 — the executor THIS dispatch runs under: the --executor flag (a
    plan-time choice the operator carries — AIP `Executor:` step field or HUMAN-stated; the tool
    never chooses) else the desk default `run_policy.executor` (absent → main_session)."""
    return ((flag or "").strip().lower()
            or (pol.get("executor") or "").strip().lower()
            or "main_session")


# --- AP-CR-26: relevance-scoped confirmed-memory loading --------------------
def _tok(text: str) -> set:
    # len>=2: drop single chars (e.g. the "f" in "F-02"/"F-05") that would spuriously overlap.
    return {t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if len(t) >= 2}


def _mem_entries(inst_dir: Path) -> "list[dict]":
    out: list[dict] = []
    for line in _read(inst_dir / "memory" / "confirmed_memory.jsonl").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            out.append({"_raw": line})  # malformed → keep + treat as always-load (never hide)
    return out


def _mem_relevant(entry: dict, task: str) -> bool:
    """AP-CR-26 — load an entry in full if: malformed/legacy-untagged (never hide), `always`-tagged,
    or its scope_tags/applies_when overlap the task (token overlap OR separator-stripped substring,
    so `function:f02` matches "F-02"). Default = load (index-all + AI judgment is the safety net)."""
    if "_raw" in entry:
        return True
    tags = entry.get("scope_tags") or []
    cond = entry.get("applies_when") or ""
    if not tags and not cond:
        return True  # legacy untagged = always-load (backward-compat)
    if any(str(t).lower() == "always" for t in tags):
        return True
    task_tokens = _tok(task)
    if task_tokens & _tok(" ".join(str(t) for t in tags) + " " + cond):
        return True
    task_compact = re.sub(r"[^a-z0-9]+", "", (task or "").lower())
    for t in tags:
        for seg in re.split(r"[^a-z0-9]+", str(t).lower()):
            if len(seg) >= 2 and seg in task_compact:
                return True
    return False


def _yaml_get(text: str, key: str) -> str:
    """Minimal flat 'key: value' reader (stdlib; no YAML lib). Top-level only.
    Strips an inline ' # comment' so 'status: active   # ...' returns 'active'."""
    m = re.search(rf"(?m)^{re.escape(key)}:[ \t]*([^#\n]*?)[ \t]*(?:#.*)?$", text)
    if not m:
        return ""
    return m.group(1).strip().strip('"').strip("'")


def _yq(value: str) -> str:
    """Emit a YAML-safe scalar for run_state free-text fields (AP-CR-35; stdlib, no YAML lib).
    The literal "null" sentinel stays a bareword (so `stopped_reason: null` keeps its YAML-null
    semantics); any other value becomes a double-quoted scalar with backslash + double-quote
    escaped, so values containing ':', '-', etc. emit as VALID YAML. The reader `_yaml_get`
    strips the outer quotes, so quoted values round-trip."""
    if value == "null":
        return "null"
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


_BP_SURFACE_CANDIDATES = (
    "skills/skill_index.yaml", "profile.md", "output_templates/", "checklists/",
    "process/", "docs/reference_content/",
)


def _bp_surfaces(bp: "Path | None") -> str:
    """DF-B-01 (AIP-EXEC-995) — ARC §3 companion-surface list derived from what EXISTS on disk.

    The list used to be hardcoded (`… · output_templates/ · checklists/`), so it started lying the
    moment CR-AIWS-2026-08-008 moved domain checklists to `docs/reference_content/` — a Phase-B run
    hit the dead pointer (RG-1). Fixed candidate order = stable ARC diffs across runs.
    """
    if bp is None or not bp.is_dir():
        return "(no blueprint — see `agent_design_snapshot.yaml`)"
    found = [f"`{c}`" for c in _BP_SURFACE_CANDIDATES if (bp / c.rstrip("/")).exists()]
    return " · ".join(found) if found else "(no companion surfaces on disk)"


def _resolve_blueprint_by_id(root: Path, bid: str) -> "Path | None":
    """Resolve an ATDB dir by id, falling back to a blueprint's `previous_ids` alias.

    CR-AIWS-2026-08-017 renamed the shipped ATDB to `aiws_*`; a desk pinned to the OLD id (here or
    downstream) must keep resolving, otherwise the rename orphans it. Underscore dirs (`_shared`) are
    never alias donors — they are not ATDB.
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
        prev = [x.strip().strip('"').strip("'") for x in inline.group(1).split(",")] if inline else _yaml_list(text, "previous_ids")
        if bid in [p for p in prev if p]:
            return d
    return None


def _blueprint_dir(inst_dir: Path) -> "Path | None":
    ref = _read(inst_dir / "blueprint_ref.yaml")
    return _resolve_blueprint_by_id(BLUEPRINTS, _yaml_get(ref, "blueprint_id"))


def _yaml_list(text: str, key: str) -> "list":
    """Read a simple 'key:\n  - item\n  - item' block (stdlib; no YAML lib). Returns the item strings."""
    m = re.search(rf"(?ms)^[ \t]*{re.escape(key)}:[ \t]*\n(.*?)(?=^\S|\Z)", text)
    if not m:
        return []
    return [x.strip().strip('"').strip("'") for x in re.findall(r"(?m)^[ \t]*-[ \t]*(\S.*?)[ \t]*$", m.group(1))]


def _memory_profile_files(inst_dir: Path) -> "list":
    """AP-CR-36 — basenames in the instance's blueprint memory_profile.required_files; [] if no blueprint/profile."""
    bp = _blueprint_dir(inst_dir)
    if bp is None:
        return []
    return [Path(x).name for x in _yaml_list(_read(bp / "blueprint.yaml"), "required_files")]


def _rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(DEV_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(p)


# --- CR-AIWS-2026-06-057: AIP Task Workspace resolution + instance-local back-pointer ----
def _resolve_task_workspace(aip: str) -> "Path | None":
    """CR-AIWS-2026-06-057 — resolve the driving AIP's Task Workspace dir via its `runtime_workspace`
    front-matter. Uniquely resolve the AIP file (via _resolve_aip_path); read `runtime_workspace`;
    substitute a leading `__PROJECT_ROOT__` token with the real project root; return the Path if it
    `.is_dir()`, else None. None on any miss/ambiguity (caller falls back to the in-instance scaffold)."""
    path, n = _resolve_aip_path(aip)
    if path is None or n != 1:
        return None
    rw = _yaml_get(_read(path), "runtime_workspace")
    if not rw:
        return None
    rw = rw.replace("\\", "/")
    if rw.startswith("__PROJECT_ROOT__"):
        rw = str(_PROJECT_ROOT).replace("\\", "/") + rw[len("__PROJECT_ROOT__"):]
    tw = Path(rw)
    return tw if tw.is_dir() else None


def _run_index_path(inst_dir: Path) -> Path:
    return inst_dir / "run_index.jsonl"


def _read_run_index(inst_dir: Path) -> "list[dict]":
    """CR-AIWS-2026-06-057 — read the instance-local run_index.jsonl back-pointer (tolerant of
    missing file / malformed lines). Each entry maps a run_id to its (project-relative) Task Workspace."""
    out: list[dict] = []
    for line in _read(_run_index_path(inst_dir)).splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            if isinstance(d, dict):
                out.append(d)
        except Exception:
            continue  # malformed → skip (best-effort back-pointer)
    return out


def _upsert_run_index(inst_dir: Path, run_id: str, task_workspace_rel: str,
                      related_aip: str, status: str) -> None:
    """CR-AIWS-2026-06-057 — append or update the run_index.jsonl line for run_id. `task_workspace_rel`
    is a project-root-relative POSIX path. Boundary-guarded write (run_index lives inside the pack root)."""
    rows = _read_run_index(inst_dir)
    found = False
    for r in rows:
        if r.get("run_id") == run_id:
            r["task_workspace"] = task_workspace_rel
            r["related_aip"] = related_aip
            r["status"] = status
            found = True
            break
    if not found:
        rows.append({
            "run_id": run_id,
            "task_workspace": task_workspace_rel,
            "related_aip": related_aip,
            "status": status,
            "created_at": _today(),
        })
    body = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    _write(_run_index_path(inst_dir), body)


def _tw_rel(tw: Path) -> str:
    """Project-root-relative POSIX path for a Task Workspace (for run_index storage)."""
    try:
        return str(tw.resolve().relative_to(_PROJECT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(tw.resolve()).replace("\\", "/")


# --- run_state.yaml (additive; status source of truth) ----------------------
def _run_state_path(run_dir: Path) -> Path:
    return run_dir / "run_state.yaml"


def _read_status(run_dir: Path) -> str:
    txt = _read(_run_state_path(run_dir))
    if not txt:
        return "completed"  # backward-compat: pre-run_state runs = completed (R-6)
    return _yaml_get(txt, "status") or "active"


def _write_run_state(run_dir: Path, run_id: str, instance: str, status: str,
                     task: str, stopped_reason: str = "null",
                     executor: str = "", tier: str = "", tier_meta: "dict | None" = None) -> None:
    # CR-AIWS-2026-08-044/045 — additive dispatch stamps: the executor this run was dispatched
    # under, plus tier AND its RESOLVED {provider, model, effort} (the mapping changes over time,
    # so measurements must record the resolved values, not just the tier name).
    _tr = ("{provider: %s, model: %s, effort: %s}" % (
        tier_meta.get("provider", ""), tier_meta.get("model", ""), tier_meta.get("effort", ""))
        if tier_meta else "null")
    body = (
        f"# run_state.yaml — runtime state of one agent run (additive to Phase C run-record)\n"
        f"run_id: {run_id}\n"
        f"agent_instance_id: {instance}\n"
        f"status: {status}            # awaiting_plan_confirm | active | incomplete | completed | stopped (CR-AIWS-2026-07-016)\n"
        f"created_at: \"{_today()}\"\n"
        f"updated_at: \"{_today()}\"\n"
        f"stopped_reason: {_yq(stopped_reason)}\n"
        f"executor: {executor or 'main_session'}   # CR-AIWS-2026-08-044 C2 (dispatch stamp)\n"
        f"tier: {tier or 'null'}                # CR-AIWS-2026-08-045 C5\n"
        f"tier_resolved: {_tr}\n"
        f"plan_confirmed_by: null\n"
        f"plan_confirmed_at: null\n"
        f"progress:                 # AI ticks these as it works; resume reads this\n"
        f"  - step: read ARC + task request\n"
        f"    done: false\n"
        f"  - step: produce output per blueprint output_templates\n"
        f"    done: false\n"
        f"  - step: capture >=1 learning candidate\n"
        f"    done: false\n"
        f"notes: {_yq(task[:120] if task else '<current-state note for HUMAN>')}\n"
    )
    _write(_run_state_path(run_dir), body)


def _set_status(run_dir: Path, status: str, reason: str = "null") -> None:
    p = _run_state_path(run_dir)
    txt = _read(p)
    if not txt:
        _die(f"run_state.yaml missing in {run_dir}")
    txt = re.sub(r"(?m)^status:.*$", f"status: {status}", txt)
    txt = re.sub(r"(?m)^updated_at:.*$", f'updated_at: "{_today()}"', txt)
    if reason != "null":
        txt = re.sub(r"(?m)^stopped_reason:.*$", f"stopped_reason: {_yq(reason)}", txt)
    _write(p, txt)


# --- ARC materialization ----------------------------------------------------
def _materialize_arc(run_dir: Path, instance: str, inst_dir: Path, run_id: str,
                     task: str, aip: str = "", task_workspace: "Path | None" = None) -> Path:
    bp = _blueprint_dir(inst_dir)
    bp_line = _rel(bp) if bp else "(custom / no blueprint — see agent_design_snapshot.yaml)"
    bp_surfaces = _bp_surfaces(bp)  # DF-B-01: derived from disk, never hardcoded

    # AP-CR-31: the agent follows its OWN process when forked; else the blueprint's (pre-fork fallback).
    inst_proc = inst_dir / "process"
    if inst_proc.is_dir() and any(inst_proc.glob("*.md")):
        proc_ptr = f"`{_rel(inst_proc)}` — instance-OWNED (AP-CR-31); improve ONLY via process_improvement_candidate (HUMAN-gated)"
    elif bp:
        proc_ptr = f"`{_rel(bp / 'process')}` — blueprint process (this instance has not forked its own process yet)"
    else:
        proc_ptr = "author/maintain your own `process/` (custom no-blueprint)"

    # AP-CR-26: relevance-scoped confirmed memory — load always-on + task-relevant in FULL; index ALL.
    entries = _mem_entries(inst_dir)

    def _mem_line(e: dict) -> str:
        return e["_raw"] if "_raw" in e else json.dumps(e, ensure_ascii=False)

    def _mem_idx(e: dict) -> str:
        if "_raw" in e:
            return f"- (raw) {e['_raw'][:80]}"
        eid = e.get("id") or e.get("cm_id") or "?"
        typ = e.get("type") or e.get("kind") or "memory"
        tags = ", ".join(str(t) for t in (e.get("scope_tags") or [])) or "-"
        cond = (e.get("applies_when") or "").strip()
        return f"- [{eid}] {typ} · tags: {tags}" + (f" · when: {cond}" if cond else "")

    loaded = [e for e in entries if _mem_relevant(e, task)]
    cm_path = _rel(inst_dir / "memory" / "confirmed_memory.jsonl")
    if entries:
        loaded_block = "\n".join(_mem_line(e) for e in loaded) if loaded else "(none task-relevant — see §5.2 index)"
        index_block = "\n".join(_mem_idx(e) for e in entries)
        mem_note = f"Loaded {len(loaded)} of {len(entries)} — open `{cm_path}` for any you judge relevant"
    else:
        loaded_block = "(empty — no confirmed memory yet)"
        index_block = "(none yet)"
        mem_note = "Loaded 0 of 0"

    # CR-AIWS-2026-07-017: surface retrieval_hints.jsonl in the ARC (§5.3) — the process mandates
    # reading hints (review process Step 3.4) and review-learning appends digest pointers here; the
    # ARC previously never loaded them. Hints without scope fields = always-shown (same back-compat
    # stance as _mem_relevant). Digest hints render label + reuse_when + path (pointer, not content).
    hint_lines: list[str] = []
    for _hline in _read(inst_dir / "memory" / "retrieval_hints.jsonl").splitlines():
        _hline = _hline.strip()
        if not _hline:
            continue
        try:
            _h = json.loads(_hline)
            _lbl = _h.get("digest_id") or _h.get("id") or "hint"
            _txt = (_h.get("reuse_when") or _h.get("hint") or _h.get("content") or "").strip()
            _pth = (_h.get("path") or "").strip()
            hint_lines.append(f"- [{_lbl}] {_txt}" + (f" → `{_pth}`" if _pth else ""))
        except Exception:
            hint_lines.append(f"- {_hline[:100]}")
    hints_block = "\n".join(hint_lines) if hint_lines else "(none yet)"

    # AP-CR-25 + AP-CR-41: run-policy + template-conformance on the AI's read surface (ARC §8).
    pol = _instance_run_policy(inst_dir)
    if pol.get("aip_driven", "").lower() in ("true", "yes"):
        _exp = (pol.get("aip_template") or "").strip()
        if _exp and (aip or "").strip():
            _p, _n = _resolve_aip_path(aip)
            if _n > 1:
                _conf = f"AMBIGUOUS (--aip matches {_n} files)"
            elif _p is None:
                _conf = "unverified (could not resolve --aip)"
            else:
                _act = _aip_template_source(_p)
                if not _act:
                    _conf = "unverified (no template_source stamp)"
                elif _norm_template(_act) == _norm_template(_exp):
                    _conf = f"OK (expected={_norm_template(_exp)} actual={_norm_template(_act)})"
                else:
                    _conf = f"MISMATCH (expected={_norm_template(_exp)} actual={_norm_template(_act)})"
        else:
            _conf = "(n/a — no aip_template or no driving AIP)"
        pol_block = (
            "- **aip_driven: true** — this agent runs ONLY under a driving AIP (`/aiws-aip create` → `/aiws-aip run`).\n"
            f"- driving AIP: {aip or '(none — the run should have been refused)'}\n"
            f"- aip_template: {pol.get('aip_template') or '(none)'}\n"
            f"- template_conformance: {_conf}\n"
            "- This run is ONE step of that AIP; record findings as AIP step evidence."
        )
    else:
        pol_block = "- aip_driven: false / unset — no AIP gate; standard single-shot run."
    # CR-AIWS-2026-08-007 (executor surface) + CR-AIWS-2026-08-002 (conduct) — both executors read this.
    _exec = (pol.get("executor") or "main_session").strip() or "main_session"
    pol_block += (
        f"\n- executor: {_exec} (CR-AIWS-2026-08-007 — claude_subagent: main session spawns the "
        "sub-agent AFTER the gates pass; return = hand-off contract, blocked → mailbox resume)"
        "\n- **stop-on-self-deviation:** detected self-deviation from a declared rule => STOP + report "
        "(see agents/blueprints/_shared/common/stop_on_deviation_rule.md); never self-adjudicate."
    )

    # CR-AIWS-2026-06-057 — when this run REUSES the driving AIP's Task Workspace, the run-folder IS that
    # TW (not an in-instance RUN folder). Reflect that in §1 and route captures to the project capture
    # channel (08_capture_inbox.jsonl per CR-042 C1), NOT a run-local learning_candidates.jsonl.
    if task_workspace is not None:
        tw_note = (f"\n- **task workspace (CR-AIWS-2026-06-057):** this run REUSES the driving AIP's Task "
                   f"Workspace at `{_rel(task_workspace)}` — outputs/state materialize THERE, not in a "
                   f"separate in-instance run-folder. The instance keeps a `run_index.jsonl` back-pointer.")
        capture_line = ("- Capture >=1 learning candidate to THIS Task Workspace's `08_capture_inbox.jsonl` "
                        "(the single project capture channel; applied CR-042 C1) — no auto-confirm.")
    else:
        tw_note = ""
        capture_line = ("- Capture >=1 learning candidate (status=candidate) to `learning_candidates.jsonl` "
                        "(no auto-confirm).")

    arc = f"""---
artifact_type: active_run_context
run_id: {run_id}
agent_instance_id: {instance}
status: active
created_at: "{_today()}"
---

# Active Run Context (ARC) — {instance}

> Read surface for the AI to **act as this agent** for one task. Materialized by `run_agent.py`.
> The tool prepared this; the AI does the task. No auto-run, no auto-promotion, HUMAN-gated.

## 1. Run identity
- run_id: {run_id}
- instance: {instance}  ·  status: active (see `run_state.yaml`){tw_note}

## 2. Task request (from HUMAN)
{task if task else "(no --task provided — HUMAN states the task in-session)"}

## 3. Agent definition
- blueprint: {bp_line}
  - `blueprint.yaml` (mission · responsibilities · **non_responsibilities** · input/output_contract · memory_policy · human_gate_policy)
  - {bp_surfaces}
- **process (AP-CR-31):** follow {proc_ptr}
- **Honor `non_responsibilities`**: this agent reviews/advises/plans only — it does NOT approve, edit, auto-update Wiki/memory, or run other agents.

## 4. Context (read from instance `context/`)
- `{_rel(inst_dir / 'context' / 'wiki_references.yaml')}` — Wiki/index entries (Wiki-first, NOT Wiki-only) + `lookup_intents` (process intent -> index/source binding; resolve via `.ai-work/tooling/lookup_wiki_source.py`, pointers first)
- `{_rel(inst_dir / 'context' / 'source_references.yaml')}` — source areas to verify against
- `{_rel(inst_dir / 'context' / 'source_priority.yaml')}` — which area to weigh first
- `{_rel(inst_dir / 'context' / 'working_inventory.yaml')}` — non-wiki / not-yet-indexed files (instance-owned)
- `{_rel(inst_dir / 'context' / 'ignored_paths.yaml')}` — exclusions

## 4A. Reference resolution & run rationale (AI fills as it works — CR-AIWS-AGENT-FRAMEWORK-002 D7; canonical §9)
> The tool prepared this scaffold; YOU (the agent) fill it as you select context and execute.
> Purpose: bounded context (no overflow), a traceable record of WHY each reference was used or excluded, and an audit trail.
> Resolve `wiki_references.yaml::lookup_intents` via `.ai-work/tooling/lookup_wiki_source.py` (pointers first; load full only when needed; suggested `--limit 5`; pass `--system <id>` when multi_system; default scope `project,aiws` — `local`/raw search are authorization-gated, CR-AIWS-2026-06-052; NO standing agent raw grant).
> Escalation chain (CR-AIWS-2026-07-007/015): lexical -> `--mode tokens` -> `--mode catalog` (read-and-choose, registered-only) -> raw (still gated: halt-and-ask).
> Search-plan budget (E4, CR-AIWS-2026-07-015): plan queries BEFORE searching (~1 call per input-group). TRIP-WIRE: calls > ~2x inputs, or any tokens/catalog escalation -> you MUST append a `retrieval_improvement` capture (intent, query chain, call count, winning query, cheaper-path suggestion; classify with the MP1-MP7 taxonomy — `.ai-work/procedural/lookup_miss_patterns.md`). AIP-driven runs tier the capture up to the Task Workspace `08_capture_inbox.jsonl` (AP-CR-13).
> GENERATED pages guardrail (CR-AIWS-2026-07-010/015): `SRC-OVERVIEW-*` overview pages are generated projections — NEVER hand-edit them (lint `overview_hand_edit` = ERROR); to change content, fix source metas/index or raise a capture candidate.

### Process Interpretation
(how you read the instance process for THIS task; which `lookup_intents` apply; what you will and will not do)

### Selected References
| Intent | Selected source (id/path) | Reason | Load mode (pointer/full) |
|---|---|---|---|
| (fill) | | | |

### Excluded References
| Candidate | Reason excluded |
|---|---|
| (fill) | |

### Reference Gaps
- (intents/needs with no resolvable source — apply the intent `fallback`: report_reference_gap / ask_human_if_required / continue_with_limitation)

### Assumptions
- (assumptions made for this run)

### Limitations
- (what this run did NOT cover; confidence caveats)

## 5. Confirmed memory (HUMAN-approved; relevance-scoped — AP-CR-26)

### 5.1 Loaded (always-on + task-relevant; load confirmed-only)
```jsonl
{loaded_block}
```

### 5.2 Index — ALL confirmed memory ({mem_note})
{index_block}

- also: `{_rel(inst_dir / 'memory' / 'lessons_learned.md')}` · `{_rel(inst_dir / 'memory' / 'local_guidelines.md')}`

### 5.3 Retrieval hints & knowledge digests (CR-AIWS-2026-07-017)
{hints_block}
- digests live under `memory/knowledge_digests/` — when a hint's reuse_when matches this task, OPEN the digest file it points at (pointer-first; do not assume content).

## 6. Output contract
- Write outputs to `output/` in this run-folder (use the blueprint's `output_templates/`).
{capture_line}
- Update `run_state.yaml` `progress` as you work; set `status: completed` when done (or leave `incomplete` if you stop).

## 7. Guardrails
- Wiki-first NOT Wiki-only · no auto-promotion (output=evidence, learning=candidate) · HUMAN-gated · honor non_responsibilities.

## 8. Run policy (AP-CR-25)
{pol_block}
"""
    p = run_dir / "00_active_run_context.md"
    _write(p, arc)
    return p


def _scaffold_run(inst_dir: Path, run_id: str) -> Path:
    run_dir = inst_dir / "workspace" / "active_runs" / run_id
    _ensure_inside(run_dir, "run-folder")
    (run_dir / "output").mkdir(parents=True, exist_ok=True)
    # copy Phase C run templates if present
    if RUN_TEMPLATES.is_dir():
        for f in sorted(RUN_TEMPLATES.glob("*")):
            if f.is_file() and f.name != "README.md" and ".example." not in f.name:  # skip docs + *.example.* (AP-CR-39)
                dst = run_dir / f.name
                if not dst.exists():
                    shutil.copyfile(f, dst)
    # ensure the core evidence files exist even if templates missing
    for name in ("run_log.jsonl", "learning_candidates.jsonl", "human_feedback.md"):
        p = run_dir / name
        if not p.exists():
            _write(p, "")
    return run_dir


def _iter_runs(inst_dir: Path):
    for sub in ("active_runs", "completed_runs"):
        base = inst_dir / "workspace" / sub
        if base.is_dir():
            for d in sorted(base.iterdir()):
                if d.is_dir() and d.name.startswith("RUN-"):
                    yield sub, d


def _find_run(inst_dir: Path, run_id: str) -> Path:
    for _sub, d in _iter_runs(inst_dir):
        if d.name == run_id:
            return d
    # CR-AIWS-2026-06-057 — not an in-instance run-folder; consult the run_index back-pointer
    # (aip_driven runs that materialize INTO the driving AIP's Task Workspace).
    for r in _read_run_index(inst_dir):
        if r.get("run_id") == run_id:
            rel = (r.get("task_workspace") or "").replace("\\", "/")
            if not rel:
                _die(f"run_index entry for {run_id} has no task_workspace path")
            tw = (_PROJECT_ROOT / rel).resolve()
            if tw.is_dir():
                _allow_root(tw)
                # CR-AIWS-2026-07-018 B2 — namespaced first (<TW>/runs/<run_id>/); fall back to the
                # TW root for pre-018 legacy runs (their run_state lives at the root — R-6 style).
                ns = tw / "runs" / run_id
                if ns.is_dir():
                    return ns
                return tw
            _die(f"run {run_id} maps to a missing Task Workspace: {tw}")
    _die(f"run not found in task desk: {run_id}")


def _ledger(tw: Path, run_id: str, instance: str, event: str) -> None:
    """CR-AIWS-2026-07-018 B4 — chain ledger: one JSONL line per run event at the TW ROOT
    run_log.jsonl (run_index is per-instance; a multi-agent chain needs ONE audit surface)."""
    line = json.dumps({"ts": _today(), "run_id": run_id, "instance": instance, "event": event},
                      ensure_ascii=False)
    p = tw / "run_log.jsonl"
    _write(p, (_read(p) + line + "\n") if _read(p) else line + "\n")


def _ledger_soft(tw: Path, run_id: str, instance: str, event: str) -> str:
    """DF-B-03 (AIP-EXEC-995) — ledger append for an OBSERVATION path (`status` reconcile).

    Two defects are closed here: (1) the TW lives outside the pack root and was never allow-listed on
    the status path (only `start` calls `_allow_root`), so the boundary guard killed the whole command;
    (2) an audit-log append must never abort a READ verb — per-item degrade, never abort the run
    (tooling_authoring_conventions Rule 9). Returns "" on success, else a short reason to surface.
    """
    try:
        _allow_root(tw)          # the TW is this run's own recorded write-target (run_index)
        _ledger(tw, run_id, instance, event)
        return ""
    except Exception as e:       # noqa: BLE001 — observation must survive a broken ledger
        return f"{type(e).__name__}: {e}"


def _mailbox(tw: Path) -> Path:
    """CR-AIWS-2026-07-060 — TW-root sub↔main mailbox (append-only JSONL). Optional; created on first write."""
    return tw / "messages.jsonl"


def _merge_messages(tw: Path) -> int:
    """CR-AIWS-2026-07-060 — fold each run-private <TW>/runs/<run_id>/messages_out.jsonl into the TW-root
    messages.jsonl (run-private staging + main merge; no live bus, no shared-file race). Idempotent on
    msg_id. Returns the count of newly merged lines. Pure state-prep — never calls an LLM."""
    mbox = _mailbox(tw)
    existing = _read(mbox)
    seen = set()
    for ln in existing.splitlines():
        try:
            seen.add(json.loads(ln).get("msg_id"))
        except Exception:
            pass
    added = []
    runs = tw / "runs"
    if runs.is_dir():
        for rd in sorted(runs.iterdir()):
            out = rd / "messages_out.jsonl"
            if not (rd.is_dir() and out.exists()):
                continue
            for ln in _read(out).splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    mid = json.loads(ln).get("msg_id")
                except Exception:
                    continue
                if mid and mid in seen:
                    continue
                if mid:
                    seen.add(mid)
                added.append(ln)
    if added:
        base = existing if (not existing or existing.endswith("\n")) else existing + "\n"
        _write(mbox, base + "\n".join(added) + "\n")
    return len(added)


def _mailbox_answer(tw: Path, run_id: str, answer: dict) -> None:
    """CR-AIWS-2026-07-060 — record the main agent's answer to a blocked run: append to the TW-root mailbox
    AND to runs/<run_id>/messages_in.jsonl so resume-from-inbox (CR-061) surfaces it in the rebuilt ARC.
    decision_class business_rule/sot_conflict is HUMAN-only — the tool only records the relayed decision."""
    line = json.dumps(answer, ensure_ascii=False)
    mbox = _mailbox(tw)
    _write(mbox, (_read(mbox) + line + "\n") if _read(mbox) else line + "\n")
    inbox = tw / "runs" / run_id / "messages_in.jsonl"
    _write(inbox, (_read(inbox) + line + "\n") if _read(inbox) else line + "\n")


def _read_inbox(run_dir: Path) -> "list[dict]":
    """CR-AIWS-2026-07-060 — the primitive CR-061 resume-from-inbox reads: parsed messages_in.jsonl lines."""
    out: "list[dict]" = []
    p = run_dir / "messages_in.jsonl"
    if p.exists():
        for ln in _read(p).splitlines():
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except Exception:
                    pass
    return out


def _reconcile(inst_dir: Path) -> "list[str]":
    """Move active_runs whose status is completed/stopped → completed_runs."""
    moved = []
    base = inst_dir / "workspace" / "active_runs"
    done_dir = inst_dir / "workspace" / "completed_runs"
    if not base.is_dir():
        return moved
    for d in sorted(base.iterdir()):
        if d.is_dir() and d.name.startswith("RUN-") and _read_status(d) in ("completed", "stopped"):
            done_dir.mkdir(parents=True, exist_ok=True)
            dst = done_dir / d.name
            if not dst.exists():
                shutil.move(str(d), str(dst))
                moved.append(d.name)
    return moved


# --- AP-CR-27/28: instance lifecycle (upgrade-reconcile + clone) ------------
def _derive_id(display: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "_", (display or "").lower()).strip("_")
    return base[:79] or "agent_clone"


def _copy_tree_guarded(src: Path, dst: Path, exclude_dirs: set) -> int:
    """Recursive copy src→dst, skipping any directory whose name is in exclude_dirs (e.g. run-history).
    Every destination is boundary-checked (_ensure_inside). Stdlib-only. Returns files copied."""
    n = 0
    for child in sorted(src.iterdir()):
        if child.name in exclude_dirs:
            continue
        target = dst / child.name
        if child.is_dir():
            n += _copy_tree_guarded(child, target, exclude_dirs)
        elif child.is_file():
            _ensure_inside(target, "clone-copy")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(child, target)
            n += 1
    return n


def _resolve_process_files(bp: "Path | None") -> "list[Path]":
    """AP-CR-31 — the blueprint's EFFECTIVE process file set: the `process_docs` targets declared in
    blueprint.yaml (resolved relative to the blueprint) + any *.md directly under `bp/process/`
    (excluding a pointer README). Stdlib-only; returns existing files, de-duped, sorted by basename."""
    if bp is None:
        return []
    found = {}
    m = re.search(r"(?ms)^process_docs:\s*\n(.*?)(?=^\S|\Z)", _read(bp / "blueprint.yaml"))
    if m:
        for rel in re.findall(r":\s*(\S+\.md)\s*$", m.group(1), re.M):
            p = (bp / rel).resolve()
            if p.is_file():
                found[p.name] = p
    pdir = bp / "process"
    if pdir.is_dir():
        for child in sorted(pdir.iterdir()):
            if (child.is_file() and child.suffix == ".md"
                    and not child.name.lower().startswith("readme")
                    and child.name not in found):
                found[child.name] = child
    return [found[k] for k in sorted(found)]


def _process_changed(inst_dir: Path, bp: Path) -> bool:
    """AP-CR-31 — True when the base process changed since the instance's process snapshot.
    Compares `.atdb_snapshot/process/*.md` content to the current resolved base process
    (legacy `.blueprint_snapshot/` still read via the dual-read in `_snapshot_dir`).
    No snapshot yet → not flagged (like [no-baseline]); captured on first upgrade."""
    snap = _snapshot_dir(inst_dir) / "process"
    if not snap.is_dir():
        return False
    cur = {p.name: _read(p) for p in _resolve_process_files(bp)}
    snp = {p.name: _read(p) for p in sorted(snap.iterdir())
           if p.is_file() and p.suffix == ".md"}
    return cur != snp


_SNAPSHOT_FILES = ("blueprint.yaml", "default_tools/tool_index.yaml", "skills/skill_index.yaml")


def _capture_into(dest: Path, bp: Path, label: str, note: str = "") -> int:
    """Copy the light snapshot set (blueprint.yaml + index files + resolved process) into `dest`.

    CR-AIWS-2026-08-074 C9 — factored out so the reconcile pointer and the birth baseline capture
    THE SAME file set from ONE code path. Two hand-kept copies of a file list drift, and a baseline
    that captures a different set than the pointer it is compared against is worse than no baseline.
    """
    n = 0
    for rel in _SNAPSHOT_FILES:
        s = bp / rel
        if s.is_file():
            d = dest / rel
            _ensure_inside(d, label)
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(s, d)
            n += 1
    for src in _resolve_process_files(bp):
        d = dest / "process" / src.name
        _ensure_inside(d, label)
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, d)
        n += 1
    _write(dest / "SNAPSHOT_INFO.txt",
           f"blueprint {label} of {_rel(bp)}\n"
           f"captured_at: {_today()}\n"
           f"blueprint_version: {_yaml_get(_read(bp / 'blueprint.yaml'), 'blueprint_version')}\n"
           + note)
    return n


def _snapshot_blueprint(inst_dir: Path, bp: Path) -> int:
    """AP-CR-27 — capture a light blueprint snapshot (blueprint.yaml + index files) into
    task_desks/<id>/.atdb_snapshot/ as the reconcile baseline (OQ-2 default: light).
    AP-CR-31 — also snapshot the resolved process set into `.atdb_snapshot/process/`.

    This is the MOVING pointer: `--reconcile` refreshes it, which is what makes drift go quiet after
    a reconcile. The immutable counterpart is `_capture_baseline` — CR-AIWS-2026-08-074 C9."""
    return _capture_into(_snapshot_dir(inst_dir), bp, "snapshot")


def _capture_baseline(inst_dir: Path, bp: Path) -> "tuple[int, str]":
    """CR-AIWS-2026-08-074 C9 (DP-074-E' = a) — write the desk's BIRTH baseline, once, and never again.

    Why a second copy exists. `.atdb_snapshot/` served two roles at the same time:
      (1) the mark drift is measured against, and
      (2) the mark that separates "this line in the desk's process/ is DEBT the desk still owes the
          blueprint" from "this line is a DELIBERATE customization of the desk".
    `--reconcile` refreshes the snapshot, which role (1) needs and role (2) cannot survive: once
    snapshot == blueprint, "what does this desk still owe?" answers "nothing" no matter what the
    HUMAN actually merged. A reconcile is a self-certification that erases the evidence it was
    about. With a fixed birth mark you can subtract instead of guess:
        deliberate customization = diff(desk/process, .atdb_baseline/process)
        current gap              = diff(desk/process, .atdb_snapshot/process)
        outstanding debt         = current gap MINUS deliberate customization
    and that stays answerable after any number of reconciles.

    Returns `(files_written, how)` where `how` is one of:
      `"exists"`               — already present; NOTHING is rewritten (this is the whole point)
      `"captured"`             — fresh capture from the blueprint
      `"seeded-from-snapshot"` — retro-fit for a desk that predates this CR. The existing snapshot is
                                 the closest thing to a birth mark that exists on disk, but it may
                                 already have been reconciled forward, so it is LABELLED as such in
                                 SNAPSHOT_INFO.txt rather than passed off as the real thing.
    """
    base = _baseline_dir(inst_dir)
    if (base / "blueprint.yaml").exists():
        return (0, "exists")
    snap = _snapshot_dir(inst_dir)
    if (snap / "blueprint.yaml").exists():
        n = 0
        for src in sorted(p for p in snap.rglob("*") if p.is_file()):
            if src.name == "SNAPSHOT_INFO.txt":
                continue
            d = base / src.relative_to(snap)
            _ensure_inside(d, "baseline")
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, d)
            n += 1
        _write(base / "SNAPSHOT_INFO.txt",
               f"blueprint BIRTH BASELINE (retro-fit) of {_rel(bp)}\n"
               f"captured_at: {_today()}\n"
               f"seeded_from: .atdb_snapshot/ — this desk predates CR-AIWS-2026-08-074 C9, so no true\n"
               f"  birth mark exists. The snapshot may already have been reconciled forward; treat this\n"
               f"  baseline as a LOWER BOUND on the desk's deliberate customization, not as its birth state.\n")
        return (n, "seeded-from-snapshot")
    return (_capture_into(base, bp, "BIRTH BASELINE",
                          "immutable: refreshed by NOTHING, including --reconcile "
                          "(CR-AIWS-2026-08-074 C9)\n"), "captured")


def _process_debt(inst_dir: Path, bp: Path) -> "tuple[list[str], list[str]]":
    """CR-AIWS-2026-08-074 C9/C11 — split the desk's process delta into (customized, debt).

    `customized` — files that differ from the BIRTH baseline: the desk changed them on purpose.
    `debt`       — files where the base process moved since the baseline but the desk's copy did
                   NOT follow: a change the desk still owes. Answerable AFTER a reconcile, which is
                   the whole reason the baseline exists.
    Returns two sorted name lists; empty when there is no baseline to reason from.
    """
    base = _baseline_dir(inst_dir) / "process"
    desk = inst_dir / "process"
    if not base.is_dir():
        return ([], [])
    b = {p.name: _read(p) for p in sorted(base.iterdir()) if p.is_file() and p.suffix == ".md"}
    d = {p.name: _read(p) for p in sorted(desk.iterdir())} if desk.is_dir() else {}
    cur = {p.name: _read(p) for p in _resolve_process_files(bp)}
    customized = sorted(n for n in d if n in b and d[n] != b[n])
    debt = sorted(n for n in cur
                  if n in b and cur[n] != b[n] and d.get(n, b[n]) == b[n])
    debt += sorted(n for n in cur if n not in b and n not in d)
    return (customized, sorted(set(debt)))


def _drift(inst_dir: Path, bp: Path) -> "tuple[bool, str]":
    """AP-CR-27 drift signal: version-pin mismatch [outdated], snapshot≠current [drift], or no baseline."""
    pinned = _yaml_get(_read(inst_dir / "blueprint_ref.yaml"), "blueprint_version")
    current = _yaml_get(_read(bp / "blueprint.yaml"), "blueprint_version")
    if pinned and current and pinned != current:
        return True, f"[outdated] pinned {pinned} != current {current}"
    snap_bp = _snapshot_dir(inst_dir) / "blueprint.yaml"
    if not snap_bp.exists():
        return True, "[no-baseline] no .atdb_snapshot yet — run upgrade once to capture"
    if _read(snap_bp) != _read(bp / "blueprint.yaml"):
        return True, "[drift] snapshot blueprint.yaml differs from current"
    if _process_changed(inst_dir, bp):
        return True, "[process-drift] base process changed since snapshot — reconcile instance process (§6D)"
    return False, ""


def _drift_marker(inst_dir: Path) -> str:
    """Short marker for `list` — only GENUINE drift ([outdated]/[drift]). Empty when in sync, custom
    (no blueprint), or merely not-yet-baselined ([no-baseline] is normal, not an alarm)."""
    bp = _blueprint_dir(inst_dir)
    if bp is None:
        return ""
    drift, reason = _drift(inst_dir, bp)
    if not drift or reason.startswith("[no-baseline]"):
        return ""
    return "  " + reason.split("]")[0].lstrip("[").join(("[", "]"))


def _rewrite_instance_identity(dst_dir: Path, new_id: str, display: str) -> None:
    p = _desk_yaml(dst_dir)
    txt = _read(p)
    disp_line = f'display_name: "{display}"'
    txt = re.sub(r"(?m)^instance_id:.*$", lambda m: f"instance_id: {new_id}", txt, count=1)
    if re.search(r"(?m)^display_name:", txt):
        txt = re.sub(r"(?m)^display_name:.*$", lambda m: disp_line, txt, count=1)
    else:
        txt = re.sub(r"(?m)^(instance_id:.*)$", lambda m: m.group(1) + "\n" + disp_line, txt, count=1)
    if re.search(r"(?m)^created_at:", txt):
        txt = re.sub(r"(?m)^created_at:.*$", lambda m: f'created_at: "{_today()}"', txt, count=1)
    if re.search(r"(?m)^last_reviewed_at:", txt):
        txt = re.sub(r"(?m)^last_reviewed_at:.*$", lambda m: "last_reviewed_at: null", txt, count=1)
    _write(p, txt)


def _flag_cloned_memory(dst_dir: Path, src_id: str) -> int:
    """AP-CR-28 — mark each copied confirmed-memory entry clone_review:pending + cloned_from
    (malformed lines kept verbatim, NOT flagged). HUMAN keeps/prunes via /aiws-agent-review-learning."""
    p = dst_dir / "memory" / "confirmed_memory.jsonl"
    if not p.exists():
        return 0
    out, n = [], 0
    for line in _read(p).splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            e = json.loads(s)
        except Exception:
            out.append(line)  # malformed → verbatim, not flagged
            continue
        e["clone_review"] = "pending"
        e["cloned_from"] = src_id
        out.append(json.dumps(e, ensure_ascii=False))
        n += 1
    _write(p, ("\n".join(out) + "\n") if out else "")
    return n


def _write_clone_lineage(dst_dir: Path, src_id: str, why: str) -> None:
    why = (why or f"cloned from {src_id}").replace("\n", " ")
    ref = dst_dir / "blueprint_ref.yaml"
    rtxt = _read(ref)
    for k in ("cloned_from", "cloned_at", "clone_why"):
        rtxt = re.sub(rf"(?m)^{k}:.*$\n?", "", rtxt)
    lineage = (f"cloned_from: {src_id}\n"
               f'cloned_at: "{_today()}"\n'
               f"clone_why: {why}\n")
    if rtxt.strip():
        _write(ref, rtxt.rstrip("\n") + "\n# clone lineage (AP-CR-28)\n" + lineage)
    else:
        _write(ref, "# blueprint_ref.yaml (clone — AP-CR-28)\n" + lineage)
    cl = dst_dir / "changelog.md"
    ctxt = _read(cl)
    entry = (f"## {_today()} — cloned from {src_id} (AIP-EXEC-146 / AP-CR-28)\n"
             f"- layer: override\n"
             f"- affects: instance identity + full instance-owned layer\n"
             f"- why: {why}\n"
             f"- source: HUMAN-feedback\n"
             f"- confirmed_memory entries flagged `clone_review: pending` for HUMAN keep/prune\n\n")
    if ctxt.strip().startswith("#"):
        nl = ctxt.find("\n")
        head, rest = (ctxt[:nl + 1], ctxt[nl + 1:]) if nl != -1 else (ctxt + "\n", "")
        _write(cl, head + "\n" + entry + rest.lstrip("\n"))
    else:
        _write(cl, f"# Changelog — clone of {src_id}\n\n" + entry + ctxt)


def _repin_version(inst_dir: Path, to_v: str) -> None:
    p = inst_dir / "blueprint_ref.yaml"
    txt = _read(p)
    if re.search(r"(?m)^blueprint_version:", txt):
        _write(p, re.sub(r"(?m)^blueprint_version:.*$", lambda m: f'blueprint_version: "{to_v}"', txt, count=1))


def _append_reconcile_log(inst_dir: Path, from_v: str, to_v: str, decisions: str) -> None:
    p = inst_dir / "blueprint_ref.yaml"
    txt = _read(p)
    entry = (f'  - reconciled_at: "{_today()}"\n'
             f'    from_version: "{from_v}"\n'
             f'    to_version: "{to_v}"\n'
             f"    decisions: {decisions}\n"
             f"    by: HUMAN")
    if re.search(r"(?m)^reconcile_log:[ \t]*\[\][ \t]*$", txt):
        _write(p, re.sub(r"(?m)^reconcile_log:[ \t]*\[\][ \t]*$", lambda m: "reconcile_log:\n" + entry, txt, count=1))
    elif re.search(r"(?m)^reconcile_log:[ \t]*$", txt):
        _write(p, re.sub(r"(?m)^(reconcile_log:[ \t]*)$", lambda m: m.group(1) + "\n" + entry, txt, count=1))
    else:
        _write(p, txt.rstrip("\n") + "\nreconcile_log:\n" + entry + "\n")


def _append_instance_changelog_reconcile(inst_dir: Path, from_v: str, to_v: str, decisions: str) -> None:
    cl = inst_dir / "changelog.md"
    ctxt = _read(cl)
    entry = (f"## {_today()} — reconcile blueprint {from_v}->{to_v} (AIP-EXEC-146 / AP-CR-27)\n"
             f"- layer: override\n"
             f"- affects: blueprint-derived fields (HUMAN-confirmed)\n"
             f"- why: {decisions}\n"
             f"- source: HUMAN-feedback\n\n")
    if ctxt.strip().startswith("#"):
        nl = ctxt.find("\n")
        head, rest = (ctxt[:nl + 1], ctxt[nl + 1:]) if nl != -1 else (ctxt + "\n", "")
        _write(cl, head + "\n" + entry + rest.lstrip("\n"))
    else:
        _write(cl, entry + ctxt)


# --- AP-CR-30: instance rename (in-place identity change + previous_ids alias) ----
def _accumulate_previous_ids(txt: str, old_id: str) -> str:
    """AP-CR-30 — append old_id to instance.yaml `previous_ids` (inline-flow), preserving prior aliases
    (no cap — OP-1). Replaces an existing inline/block form, else inserts the line after
    display_name / instance_name / instance_id."""
    existing = _previous_ids_from_text(txt)
    if old_id not in existing:
        existing.append(old_id)
    line = "previous_ids: [" + ", ".join(existing) + "]"
    if re.search(r"(?m)^previous_ids:[ \t]*\[[^\]]*\][ \t]*$", txt):
        return re.sub(r"(?m)^previous_ids:[ \t]*\[[^\]]*\][ \t]*$", lambda m: line, txt, count=1)
    block = re.search(r"(?m)^previous_ids:[ \t]*$\n(?:[ \t]+-[ \t]*\S.*\n?)+", txt)
    if block:
        return txt[:block.start()] + line + "\n" + txt[block.end():]
    for anchor in (r"(?m)^display_name:.*$", r"(?m)^instance_name:.*$", r"(?m)^instance_id:.*$"):
        if re.search(anchor, txt):
            return re.sub(anchor, lambda m: m.group(0) + "\n" + line, txt, count=1)
    return txt.rstrip("\n") + "\n" + line + "\n"


def _rewrite_rename_identity(dst_dir: Path, old_id: str, new_id: str,
                             new_name: str = "", new_display: str = "") -> None:
    """AP-CR-30 — rewrite instance.yaml identity for a rename: instance_id -> new_id, optional
    instance_name/display_name, and accumulate old_id into previous_ids. Unlike clone, this is the SAME
    instance — created_at / last_reviewed_at are left untouched (no reset)."""
    p = _desk_yaml(dst_dir)
    txt = _read(p)
    txt = re.sub(r"(?m)^instance_id:.*$", lambda m: f"instance_id: {new_id}", txt, count=1)
    if new_name:
        nm = f"instance_name: {new_name.replace(chr(10), ' ').strip()}"
        if re.search(r"(?m)^instance_name:", txt):
            txt = re.sub(r"(?m)^instance_name:.*$", lambda m: nm, txt, count=1)
        else:
            txt = re.sub(r"(?m)^(instance_id:.*)$", lambda m: m.group(1) + "\n" + nm, txt, count=1)
    if new_display:
        disp = f'display_name: "{new_display.replace(chr(34), "").strip()}"'
        if re.search(r"(?m)^display_name:", txt):
            txt = re.sub(r"(?m)^display_name:.*$", lambda m: disp, txt, count=1)
        else:
            anchor = r"(?m)^instance_name:.*$" if re.search(r"(?m)^instance_name:", txt) else r"(?m)^instance_id:.*$"
            txt = re.sub(anchor, lambda m: m.group(0) + "\n" + disp, txt, count=1)
    txt = _accumulate_previous_ids(txt, old_id)
    _write(p, txt)


def _rewrite_own_run_history(inst_dir: Path, new_id: str) -> int:
    """AP-CR-30 — repoint the renamed instance's OWN run-records to the new id: `agent_instance_id` in
    each run's run_state.yaml + run_request.yaml (active + completed). NO cross-instance rewrite.
    Returns the number of runs touched."""
    n = 0
    for _sub, run_dir in _iter_runs(inst_dir):
        touched = False
        for fname in ("run_state.yaml", "run_request.yaml"):
            p = run_dir / fname
            if not p.exists():
                continue
            txt = _read(p)
            new = re.sub(r"(?m)^(agent_instance_id:[ \t]*).*$", lambda m: m.group(1) + new_id, txt)
            if new != txt:
                _write(p, new)
                touched = True
        if touched:
            n += 1
    return n


def _append_rename_changelog(inst_dir: Path, old_id: str, new_id: str, why: str) -> None:
    why = (why or f"renamed {old_id} -> {new_id}").replace("\n", " ")
    cl = inst_dir / "changelog.md"
    ctxt = _read(cl)
    entry = (f"## {_today()} — renamed instance_id {old_id} -> {new_id} (AIP-EXEC-147 / AP-CR-30)\n"
             f"- layer: override\n"
             f"- affects: instance identity (instance_id + folder + own run-history; previous_ids alias)\n"
             f"- why: {why}\n"
             f"- source: HUMAN-feedback\n"
             f"- old id retained in `previous_ids` so prior references (cloned_from / run-history / typed old id) still resolve\n\n")
    if ctxt.strip().startswith("#"):
        nl = ctxt.find("\n")
        head, rest = (ctxt[:nl + 1], ctxt[nl + 1:]) if nl != -1 else (ctxt + "\n", "")
        _write(cl, head + "\n" + entry + rest.lstrip("\n"))
    else:
        _write(cl, f"# Changelog — {new_id}\n\n" + entry + ctxt)


# --- subcommands ------------------------------------------------------------
def cmd_start(a) -> None:
    inst_dir = _instance_dir(a.instance)
    instance = inst_dir.name  # canonical id (fuzzy token resolved)
    # AP-CR-25/41 + stage-3 + CR-AIWS-2026-08-044 (toggle C0 · executors_allowed/requested C1/C2 ·
    # profile guard re-keyed): ALL gates BEFORE scaffolding (no orphan run-folder).
    _check_run_policy(inst_dir, instance, a.aip, a.strict_template, getattr(a, "executor", ""))
    req_exec = _requested_executor(_instance_run_policy(inst_dir), getattr(a, "executor", ""))
    # CR-AIWS-2026-08-045 C3/C4 — optional --tier: validate vs the desk's tiers_supported, then
    # resolve tier → {provider, model, effort} via the registry (refuse BEFORE scaffolding).
    tier = (getattr(a, "tier", "") or "").strip().lower()
    tier_meta: dict = {}
    if tier:
        _ts = _desk_tiers(_instance_capability(inst_dir))
        if tier not in _ts:
            _die(f"--tier '{tier}' is not in desk '{instance}' tiers_supported {sorted(_ts)} "
                 "(CR-AIWS-2026-08-045 C3). (no run-folder was created.)")
        tier_meta = _resolve_tier(tier)
    run_id = f"RUN-{_now_id()}-{_slug(a.slug or a.task or 'run')}"

    # CR-AIWS-2026-06-057 — an aip_driven run whose driving AIP has a resolvable Task Workspace
    # materializes INTO that TW (single workspace), with an instance-local run_index back-pointer.
    pol = _instance_run_policy(inst_dir)

    # CR-AIWS-2026-07-016 — two-phase run (plan_first): phase 1 drafts run_plan.md and STOPS at
    # `awaiting_plan_confirm`; the HUMAN gates via `confirm-plan` (by/at evidence); execution then
    # proceeds with NO mid-run gate (OP log-and-continue). An aip_driven run WITH --aip skips
    # plan-first by default (the driving AIP already passed Gate U1 = the plan-level confirm).
    plan_first = getattr(a, "plan_first", False) or pol.get("plan_first", "").lower() in ("true", "yes")
    if plan_first and not (a.aip or "").strip():
        run_dir = _scaffold_run(inst_dir, run_id)
        tpl = RUN_TEMPLATES / "run_plan.md"
        if tpl.exists() and not (run_dir / "run_plan.md").exists():
            _write(run_dir / "run_plan.md", _read(tpl).replace("<task verbatim>", (a.task or "<task>")))
        _write_run_state(run_dir, run_id, instance, "awaiting_plan_confirm", a.task or "",
                         executor=req_exec, tier=tier, tier_meta=tier_meta)
        arc = _materialize_arc(run_dir, instance, inst_dir, run_id, a.task or "", a.aip)
        print(f"run started (PHASE 1 — plan): {run_id}")
        print(f"  run-folder: {_rel(run_dir)}")
        print(f"  run_plan:   {_rel(run_dir / 'run_plan.md')}   (AI drafts this — Working-AIP-Lite shape; task kept VERBATIM)")
        print(f"  status:     awaiting_plan_confirm  ({_rel(_run_state_path(run_dir))})")
        print("Next: AI drafts run_plan.md from the ARC; HUMAN reviews and runs:")
        print(f"      py tooling/run_agent.py confirm-plan {instance} {run_id}")
        print("      (plan grows beyond a run → promote via /create-aip and restart aip_driven — escape hatch.)")
        return

    tw = _resolve_task_workspace(a.aip) if (a.aip and pol.get("aip_driven", "").lower() in ("true", "yes")) else None
    if tw is not None:
        _allow_root(tw)
        # CR-AIWS-2026-07-018 B1 — PER-RUN NAMESPACING: N runs may reuse ONE Task Workspace
        # (multi-agent collaboration on one driving AIP). Each run materializes into
        # <TW>/runs/<run_id>/ — run 2 no longer overwrites run 1's run_state/ARC at the TW root.
        # Chain-shared surfaces stay at the TW root: run_log.jsonl (chain ledger, B4) +
        # 08_capture_inbox.jsonl (CR-042 C1). One ACTIVE run per TW at a time (sequential MVP).
        run_dir = tw / "runs" / run_id
        (run_dir / "output").mkdir(parents=True, exist_ok=True)
        rl = tw / "run_log.jsonl"
        if not rl.exists():
            _write(rl, "")  # NOTE: no learning_candidates.jsonl in the TW — captures go to 08_capture_inbox.jsonl (CR-042 C1)
        # CR-AIWS-2026-07-015 T3: TW-backed runs get the reference-trace + handoff surfaces too.
        for _tpl in ("used_references.md", "input_manifest.md"):
            _src = RUN_TEMPLATES / _tpl
            _dst = run_dir / _tpl
            if _src.exists() and not _dst.exists():
                _write(_dst, _read(_src))
        _seed_related_aip(run_dir, a.aip)
        _seed_step_id(run_dir, getattr(a, "step", ""))  # CR-AIWS-2026-07-061: record the AIP STEP id
        _seed_dispatch_meta(run_dir, req_exec, tier, tier_meta)  # CR-AIWS-2026-08-044/045
        _write_run_state(run_dir, run_id, instance, "active", a.task or "",
                         executor=req_exec, tier=tier, tier_meta=tier_meta)
        arc = _materialize_arc(run_dir, instance, inst_dir, run_id, a.task or "", a.aip, task_workspace=tw)
        _upsert_run_index(inst_dir, run_id, _tw_rel(tw), a.aip, "active")
        _ledger(tw, run_id, instance, "started")  # B4 — chain ledger (run_index is per-instance)
        print(f"run started: {run_id}")
        print(f"  dispatch:   executor={req_exec}"
              + (f" · tier={tier} → model={tier_meta.get('model')}, effort={tier_meta.get('effort')}"
                 f" (provider {tier_meta.get('provider')})" if tier_meta else ""))
        print(f"  REUSES AIP Task Workspace (CR-AIWS-2026-06-057 + per-run namespacing CR-2026-07-018): {_rel(tw)}")
        print(f"  run-dir:    {_rel(run_dir)}   (runs/<run_id>/ inside the TW)")
        print(f"  ARC:        {_rel(arc)}")
        print(f"  status:     active  ({_rel(_run_state_path(run_dir))})")
        print(f"  back-pointer: {_rel(_run_index_path(inst_dir))}  (run_index → {_tw_rel(tw)})")
        print("Next: AI reads 00_active_run_context.md and ACTS AS the agent (HUMAN-prompted).")
        print("      Captures go to the Task Workspace's 08_capture_inbox.jsonl (single project channel).")
        print("      Tool does NOT run the task. No auto-promotion; learning = candidate only.")
        return

    if a.aip and pol.get("aip_driven", "").lower() in ("true", "yes"):
        print(f"  [warn] AIP '{a.aip}' has no resolvable runtime_workspace (run /aiws-aip run start on it first) — run stays in-desk.")
    run_dir = _scaffold_run(inst_dir, run_id)
    if a.aip:
        _seed_related_aip(run_dir, a.aip)  # AP-CR-25: record driving AIP into run_request.yaml
        _seed_step_id(run_dir, getattr(a, "step", ""))  # CR-AIWS-2026-07-061: record the AIP STEP id
    _seed_dispatch_meta(run_dir, req_exec, tier, tier_meta)  # CR-AIWS-2026-08-044/045
    _write_run_state(run_dir, run_id, instance, "active", a.task or "",
                     executor=req_exec, tier=tier, tier_meta=tier_meta)
    arc = _materialize_arc(run_dir, instance, inst_dir, run_id, a.task or "", a.aip)
    print(f"run started: {run_id}")
    print(f"  dispatch:   executor={req_exec}"
          + (f" · tier={tier} → model={tier_meta.get('model')}, effort={tier_meta.get('effort')}"
             f" (provider {tier_meta.get('provider')})" if tier_meta else ""))
    print(f"  run-folder: {_rel(run_dir)}")
    print(f"  ARC:        {_rel(arc)}")
    print(f"  status:     active  ({_rel(_run_state_path(run_dir))})")
    print("Next: AI reads 00_active_run_context.md and ACTS AS the agent (HUMAN-prompted).")
    print("      Tool does NOT run the task. No auto-promotion; learning = candidate only.")


def cmd_confirm_plan(a) -> None:
    """CR-AIWS-2026-07-016 — HUMAN gate of the two-phase run: record by/at evidence (pattern:
    reconcile_log / clone lineage) and flip awaiting_plan_confirm → active. The tool records the
    HUMAN's decision; it never judges the plan."""
    inst_dir = _instance_dir(a.instance)
    run_dir = _find_run(inst_dir, a.run_id)
    st = _read_status(run_dir)
    if st != "awaiting_plan_confirm":
        _die(f"run {a.run_id} is '{st}' — confirm-plan applies only to awaiting_plan_confirm runs")
    if not (run_dir / "run_plan.md").exists():
        _die(f"run {a.run_id} has no run_plan.md — the AI must draft the plan before HUMAN confirm")
    p = _run_state_path(run_dir)
    txt = _read(p)
    txt = re.sub(r"(?m)^plan_confirmed_by:.*$", "plan_confirmed_by: HUMAN", txt)
    txt = re.sub(r"(?m)^plan_confirmed_at:.*$", f'plan_confirmed_at: "{_today()}"', txt)
    _write(p, txt)
    _set_status(run_dir, "active")
    print(f"plan confirmed: {a.run_id}  (plan_confirmed_by: HUMAN, {_today()})")
    print(f"  status: active  ({_rel(p)})")
    print("Next: AI executes per run_plan.md — no mid-run gate; OPs are log-and-continue (only a")
    print("      blocking OP stops the run). progress derives from the plan's Steps.")


def cmd_resume(a) -> None:
    inst_dir = _instance_dir(a.instance)
    run_dir = _find_run(inst_dir, a.run_id)
    st = _read_status(run_dir)
    if st in ("completed", "stopped"):
        _die(f"run {a.run_id} is {st} — cannot resume (start a new run)")
    if st == "awaiting_plan_confirm":
        # CR-AIWS-2026-07-016 — resume must not slip past the plan gate.
        _die(f"run {a.run_id} is awaiting_plan_confirm — HUMAN must run confirm-plan first (or stop the run)")
    aip = _yaml_get(_read(run_dir / "run_request.yaml"), "related_aip")  # AP-CR-25: keep driving AIP in ARC §8
    # CR-AIWS-2026-06-057 — if this run lives in an AIP Task Workspace (under <project>/.ai-work/workspaces/),
    # keep the capture target pointed at the TW (08_capture_inbox.jsonl), not a run-local learning file.
    _tw = None
    try:
        run_dir.resolve().relative_to((_PROJECT_ROOT / ".ai-work" / "workspaces").resolve())
        _tw = run_dir
    except ValueError:
        _tw = None
    arc = _materialize_arc(run_dir, inst_dir.name, inst_dir, a.run_id,
                           "(resume — see run-so-far in this folder)", aip, task_workspace=_tw)
    # CR-AIWS-2026-07-061 — resume-from-inbox: surface the main agent's answers (messages_in.jsonl, CR-060)
    # into the rebuilt ARC so a blocked→answered run finalizes with the relayed decision in view.
    _inbox = _read_inbox(run_dir)
    if _inbox:
        _lines = ["", "## Resume — main agent answers (mailbox inbox)", ""]
        for _msg in _inbox:
            _lines.append(f"- [{_msg.get('kind', 'answer')}] ({_msg.get('decision_class', '')}) "
                          f"re {_msg.get('related_item') or _msg.get('step_id') or ''}: {_msg.get('content', '')}")
        _write(arc, _read(arc).rstrip("\n") + "\n" + "\n".join(_lines) + "\n")
        print(f"  resume-from-inbox: surfaced {len(_inbox)} mailbox answer(s) into the ARC")
    print(f"run resumed: {a.run_id}  (status: {st})")
    print(f"  ARC refreshed: {_rel(arc)}")
    print(f"  run_state:     {_rel(_run_state_path(run_dir))}")
    print("Next: AI reloads ARC + run-so-far (output/, run_log.jsonl, progress) and continues.")


def _append_span_step(run_dir: Path, step_id: str) -> None:
    """CR-AIWS-2026-08-046 C2 — additive span fields on run_state.yaml: span_steps grows by one;
    updated_at refreshed. A 1-step run never gains these fields (old behavior untouched)."""
    p = _run_state_path(run_dir)
    txt = _read(p)
    if not txt:
        _die(f"run_state.yaml missing in {run_dir}")
    if re.search(r"(?m)^span_steps:", txt):
        txt = re.sub(r"(?m)^span_steps:\s*\[([^\]]*)\]",
                     lambda m: "span_steps: [" + (m.group(1).strip() + ", " if m.group(1).strip() else "") + step_id + "]",
                     txt)
    else:
        txt = txt.rstrip("\n") + f"\nspan_steps: [{step_id}]   # CR-AIWS-2026-08-046 (multi-step span)\n"
    txt = re.sub(r"(?m)^updated_at:.*$", f'updated_at: "{_today()}"', txt)
    _write(p, txt)


def _step_num(step_id: str) -> int:
    m = re.search(r"STEP-(\d+)", step_id or "")
    return int(m.group(1)) if m else -1


def cmd_extend(a) -> None:
    """CR-AIWS-2026-08-046 C2 — extend an ACTIVE TW-backed run to its NEXT CONSECUTIVE step of the
    SAME driving AIP (multi-step span). STATE-PREP ONLY (§8D invariant kept): the tool runs the FULL
    per-step gates BEFORE accepting, appends a step-brief to the run's inbox (messages_in.jsonl),
    refreshes the ARC, and updates run_state span fields. The MAIN SESSION then CONTINUES the same
    named desk subagent with the new brief — the tool never spawns, never sends, never calls an LLM.
    Span rules (C1): consecutive steps · same desk · same driving AIP · never across a HARD GATE /
    Review Note / HUMAN step (those steps fail stage-3/eligibility and close the span)."""
    if not _dispatch_enabled():
        _die_dispatch_disabled("extend")
    inst_dir = _instance_dir(a.instance)
    instance = inst_dir.name
    run_dir = _find_run(inst_dir, a.run_id)
    st = _read_status(run_dir)
    if st != "active":
        _die(f"run {a.run_id} is '{st}' — extend applies only to ACTIVE runs "
             "(blocked → resume; closed → start a new run)")
    req = _read(run_dir / "run_request.yaml")
    aip = _yaml_get(req, "related_aip")
    if not aip:
        _die("extend requires an aip_driven TW-backed run (this run has no related_aip) — "
             "a span exists only inside ONE driving AIP (CR-AIWS-2026-08-046 C1)")
    step_id = (a.step or "").strip()
    if not step_id:
        _die("--step STEP-NN is required (the NEXT consecutive step of the driving AIP)")
    # --- per-step gates (same family as start; run BEFORE any state is written) ---
    _check_assigned_set(instance, aip)  # stage-3 re-read: desk still in assigned set + AIP active
    cur = _yaml_get(req, "related_task_card")
    if _step_num(step_id) != _step_num(cur) + 1:
        _die(f"span rule (CR-AIWS-2026-08-046 C1): extend accepts only the NEXT consecutive step "
             f"(current: {cur or '(none)'} → requested: {step_id}). Non-consecutive work → close "
             "this run and start a new one.")
    # --- accept: brief to inbox + ARC refresh + span stamp (state-prep only) ---
    msg = {"msg_id": f"MSG-{_now_id()}", "ts": _today(), "from": "main", "to": instance,
           "step_id": step_id, "run_id": a.run_id, "kind": "info", "decision_class": "coordination",
           "content": (f"SPAN EXTEND (CR-AIWS-2026-08-046): continue with {step_id} of {aip}. "
                       f"Task: {a.task or '(see the step ASC / refreshed ARC)'} — hand-off contract "
                       "remains PER-STEP; return it before the next extend."),
           "status": "open"}
    pin = run_dir / "messages_in.jsonl"
    _write(pin, (_read(pin) + json.dumps(msg, ensure_ascii=False) + "\n")
           if _read(pin) else json.dumps(msg, ensure_ascii=False) + "\n")
    _seed_step_id(run_dir, step_id)
    _append_span_step(run_dir, step_id)
    arc = _materialize_arc(run_dir, instance, inst_dir, a.run_id,
                           f"(span extend → {step_id} — see messages_in.jsonl + the step ASC)",
                           aip, task_workspace=run_dir)
    print(f"run extended: {a.run_id} → {step_id}  (span — CR-AIWS-2026-08-046)")
    print(f"  step-brief: appended to {_rel(pin)}")
    print(f"  ARC refreshed: {_rel(arc)}")
    print("Next: the MAIN SESSION continues the SAME desk subagent with the new step-brief")
    print("      (named continuation — NOT fork; per-step hand-off + verify before the next extend).")
    print("      Tool does NOT send/spawn anything (§8D).")


def cmd_status(a) -> None:
    inst_dir = _instance_dir(a.instance)
    moved = _reconcile(inst_dir)
    if moved:
        print(f"(reconciled → completed_runs: {', '.join(moved)})")
    if a.run_id:
        run_dir = _find_run(inst_dir, a.run_id)
        print(f"run: {a.run_id}  status: {_read_status(run_dir)}  ({_rel(run_dir)})")
        print("--- run_state.yaml ---")
        print(_read(_run_state_path(run_dir)).rstrip() or "(no run_state.yaml — treated as completed)")
        return
    rows = [(sub, d.name, _read_status(d)) for sub, d in _iter_runs(inst_dir)]
    # CR-AIWS-2026-06-057 — also enumerate TW-backed runs recorded in the run_index back-pointer.
    idx_rows = []
    for r in _read_run_index(inst_dir):
        rid = r.get("run_id")
        rel = (r.get("task_workspace") or "").replace("\\", "/")
        if not rid or not rel:
            continue
        tw = (_PROJECT_ROOT / rel).resolve()
        # CR-AIWS-2026-07-018 B2 — status reads from the namespaced run-dir when present.
        rd = (tw / "runs" / rid) if (tw / "runs" / rid).is_dir() else tw
        st = _read_status(rd) if tw.is_dir() else (r.get("status") or "unknown")
        # CR-AIWS-2026-07-015 T4: reconcile run_index status with the TW run_state (the AI sets
        # `completed` directly in the TW; without this the index stays stale at 'active' and the
        # run-close lint cannot trust index membership).
        if tw.is_dir() and st != (r.get("status") or ""):
            _upsert_run_index(inst_dir, rid, rel, r.get("related_aip", ""), st)
            if st in ("completed", "stopped"):
                # B4 chain ledger — via the fail-soft observation path (DF-B-03): allow-list this
                # run's own TW, and never let a ledger problem abort a read verb.
                why = _ledger_soft(tw, rid, inst_dir.name, st)
                if why:
                    print(f"  [warn] chain-ledger append skipped for {rid}: {why}")
        idx_rows.append((rid, st, rel, tw.is_dir()))
    if not rows and not idx_rows:
        print(f"no runs for task desk {a.instance}")
        return
    print(f"runs for {a.instance}:")
    for sub, name, st in rows:
        print(f"  [{st:10}] {name}   ({sub})")
    for rid, st, rel, ok in idx_rows:
        print(f"  [{st:10}] {rid}   (task_workspace → {rel}{'' if ok else ' — MISSING'})")


def cmd_stop(a) -> None:
    inst_dir = _instance_dir(a.instance)
    run_dir = _find_run(inst_dir, a.run_id)
    reason = (a.reason or "stopped by HUMAN").replace("\n", " ")
    _set_status(run_dir, "stopped", reason=reason)
    # CR-AIWS-2026-06-057 — keep the run_index back-pointer in sync for TW-backed runs (they do not
    # move under completed_runs; _reconcile only relocates in-instance active_runs).
    idx = _read_run_index(inst_dir)
    rec = next((r for r in idx if r.get("run_id") == a.run_id), None)
    if rec is not None:
        _upsert_run_index(inst_dir, a.run_id, rec.get("task_workspace", ""), rec.get("related_aip", ""), "stopped")
        _twp = (_PROJECT_ROOT / (rec.get("task_workspace") or "").replace("\\", "/")).resolve()
        if _twp.is_dir():
            _ledger(_twp, a.run_id, inst_dir.name, "stopped")  # CR-018 B4
    moved = _reconcile(inst_dir)
    print(f"run stopped: {a.run_id}  reason: {reason}")
    if rec is not None:
        print(f"  run_index updated → stopped  ({_rel(_run_index_path(inst_dir))})")
    if moved:
        print(f"  moved → completed_runs: {', '.join(moved)}")


# --- AP-CR-41: template-conformance gate (consumes CR-AIWS-2026-06-050 `template_source`) -----
_AIP_TEMPLATE_ALIASES = {
    "exec": "aip_exec_template", "plan": "aip_plan_template", "local": "aip_local_template",
    # dd/bd_review: TOLERATED DEAD ALIASES (CR-AIWS-2026-07-033 T5, DP-033-2=b) — AIWS does NOT
    # ship these templates and `aiws-aip create` no longer advertises them; kept ONLY so a
    # project-local SELF-MADE review template with the same basename still normalizes for the
    # AP-CR-41 conformance compare. Do not read them as an AIWS-shipped surface.
    "dd_review": "aip_exec_dd_review_template", "dd-review": "aip_exec_dd_review_template",
    "bd_review": "aip_exec_bd_review_template", "bd-review": "aip_exec_bd_review_template",
    "apply_cr": "aip_exec_apply_cr_template",
}


def _norm_template(value: str) -> str:
    """AP-CR-41 — normalize a template reference (full ID, short alias, OR full path; `.md` optional)
    to one canonical key for conformance comparison. `run_policy.aip_template` may be specified any of
    these ways — this collapses them. Case-insensitive; alias-aware."""
    s = (value or "").strip().strip('"').strip("'").replace("\\", "/")
    s = s.rsplit("/", 1)[-1]                    # basename (drops dirs → handles a full path)
    if s.lower().endswith(".md"):
        s = s[:-3]                              # drop extension
    key = s.lower()
    return _AIP_TEMPLATE_ALIASES.get(key, key)  # short alias → canonical id; else the basename itself


def _resolve_aip_path(aip_id: str):
    """AP-CR-41 — resolve a driving --aip id to its file under <project>/.ai-work/aip/ (the run flow
    carries no account_id → glob across account/kind dirs). Returns (path, count): unique→(p,1);
    none→(None,0); >1→(None,n) ambiguous."""
    tok = (aip_id or "").strip()
    if not tok:
        return (None, 0)
    aip_root = DEV_ROOT.parent.parent / ".ai-work" / "aip"
    if not aip_root.is_dir():
        return (None, 0)
    matches = [p for p in aip_root.glob("**/*.md") if tok in p.stem]
    if len(matches) == 1:
        return (matches[0], 1)
    return (None, len(matches))


def _aip_template_source(aip_path: Path) -> str:
    """AP-CR-41 — read the AIP's write-once `template_source` front-matter (CR-AIWS-2026-06-050). '' if absent."""
    return _yaml_get(_read(aip_path), "template_source")


def _check_assigned_set(instance: str, aip: str) -> None:
    """CR-AIWS-2026-07-018 B3 — stage 3 (file-first enforcement of DP-913-D): when the driving AIP
    declares any `Assigned Agent:` step field — (a) refuse a start whose instance is NOT in the
    AIP's assigned set; (b) require AIP frontmatter `status: active` (the machine proxy for
    'plan confirmed by HUMAN' — a draft AIP must not drive runs). Revoke = HUMAN edits the AIP
    (this gate re-reads it on every start). AIPs with NO Assigned Agent fields are unaffected."""
    path, n = _resolve_aip_path(aip)
    if path is None or n > 1:
        return  # unresolvable/ambiguous handled by stage 2 messaging
    body = _read(path)
    assigned = {m.group(1).strip() for m in
                re.finditer(r"(?m)^Assigned Agent:\s*\n([^\n#]+)$", body)}
    assigned = {a_ for a_ in assigned if a_}
    if not assigned:
        return  # no assigned set declared → stage-3 not in play
    status = ""
    m = re.search(r"(?m)^status:\s*([a-z_]+)", body)
    if m:
        status = m.group(1)
    if status != "active":
        _die(
            f"CR-2026-07-018 stage-3: AIP '{aip}' declares Assigned Agent steps but its status is "
            f"'{status or 'unknown'}' — a driving AIP must be `status: active` (HUMAN-confirmed plan) "
            "before agent dispatch. (no run-folder created.)"
        )
    if instance not in assigned:
        _die(
            f"CR-2026-07-018 stage-3: desk '{instance}' is NOT in AIP '{aip}' assigned set "
            f"{sorted(assigned)} — dispatch refused. Add the desk to an `Assigned Agent:` step "
            "(Re-plan Log) or run without this AIP. (no run-folder created.)"
        )


def _check_run_policy(inst_dir: Path, instance: str, aip: str, strict_template: bool = False,
                      executor_flag: str = "") -> None:
    """AP-CR-25 — refuse an aip_driven start without a driving --aip (presence, stage 1).
    AP-CR-41 — then verify TEMPLATE CONFORMANCE: the driving AIP's `template_source` must match the
    instance's `run_policy.aip_template` (basename-normalized → handles id / alias / full path).
    CR-AIWS-2026-07-018 — stage 3: assigned-set membership + AIP status:active (see
    _check_assigned_set). CR-AIWS-2026-08-044 — stage 0: dispatch toggle (C0) + requested-executor
    validation vs executors_allowed (C1/C2); the CR-08-013 profile guard is RE-KEYED to the
    REQUESTED executor (flag → desk default), so the legacy desk-declared case stays a subcase.
    All stages run BEFORE scaffolding (no orphan run-folder)."""
    # --- stage 0: dispatch toggle (CR-AIWS-2026-08-044 C0) ---
    if not _dispatch_enabled():
        _die_dispatch_disabled("start")
    # --- stage 3 first when an AIP is named (CR-2026-07-018): applies to ANY dispatch with --aip,
    # aip_driven or not — an assigned-set AIP constrains who may run under it.
    if (aip or "").strip():
        _check_assigned_set(instance, (aip or "").strip())
    pol = _instance_run_policy(inst_dir)
    # --- requested-executor validation (CR-AIWS-2026-08-044 C2) — the flag carries a PLAN-TIME
    # choice (AIP `Executor:` step field / HUMAN-stated); the tool only validates, never chooses.
    req_exec = _requested_executor(pol, executor_flag)
    if req_exec not in _EXECUTOR_VOCAB:
        _die(f"--executor '{req_exec}' is not a valid executor ({' | '.join(_EXECUTOR_VOCAB)}). "
             "(no run-folder was created.)")
    allowed = _executors_allowed(pol)
    if req_exec not in allowed:
        _die(
            f"executor guard (CR-AIWS-2026-08-044 C2): desk '{instance}' allows executors "
            f"{allowed} — requested '{req_exec}' refused.\n"
            "  Fix: pick an allowed executor, or extend the desk's run_policy.executors_allowed "
            "(HUMAN-confirmed desk config). (no run-folder was created.)"
        )
    # --- executor-profile guard (CR-AIWS-2026-08-013 T-GUARD; re-keyed by CR-AIWS-2026-08-044 C2)
    # — runs for ANY dispatch whose REQUESTED executor is the sub-agent one, aip_driven or not.
    # A `claude_subagent` run whose blueprint declares no output-contract profile puts the agent in
    # front of an unsatisfiable contract, and it will improvise a fold — the exact drift
    # CR-AIWS-2026-08-012 exists to prevent. Refuse BEFORE scaffolding (AP-CR-25 invariant: no
    # orphan run-folder). Fix = declare the profile, not disable the guard (no escape-hatch flag).
    if req_exec == "claude_subagent":
        _bp = _blueprint_dir(inst_dir)
        if _bp is None:
            # Rule 9: a missing datum degrades this check only — it never aborts the run.
            print("  [warn] executor-profile guard: blueprint not resolvable — "
                  "output-contract profile UNVERIFIED. Proceeding.")
        elif not re.search(r"(?m)^\s*(required_core|required_core_policy)\s*:", _read(_bp / "blueprint.yaml")):
            _die(
                f"executor-profile guard (CR-AIWS-2026-08-013, re-keyed CR-AIWS-2026-08-044): dispatch "
                f"for desk '{instance}' requests executor claude_subagent, but its blueprint "
                f"'{_bp.name}' declares NO output-contract profile (`required_core` / "
                "`required_core_policy`).\n"
                "  The agent would meet a contract it cannot satisfy and improvise a fold.\n"
                "  Fix: declare the profile in the blueprint's `output_contract` (see "
                "agent_runtime_design.md §8E), or dispatch on executor `main_session`.\n"
                "  (no run-folder was created.)"
            )
    if pol.get("aip_driven", "").lower() not in ("true", "yes"):
        return  # not aip_driven → no other gate (backward-compatible)
    aip = (aip or "").strip()
    # --- stage 1: presence (AP-CR-25; unchanged) ---
    if not aip:
        _die(
            f"desk '{instance}' declares run_policy.aip_driven=true — a driving AIP is required.\n"
            "  Follow the flow:\n"
            "    1) /aiws-aip create                      (create the driving AIP for this task)\n"
            "    2) /aiws-aip run                         (work the AIP; agent runs are its steps)\n"
            f"    3) py run_agent.py start {instance} --aip <AIP-ID> --task \"...\"\n"
            "  (no run-folder was created.)"
        )
    # --- stage 2: template conformance (AP-CR-41) ---
    expected = (pol.get("aip_template") or "").strip()
    if not expected:
        return  # no declared template → nothing to conform to
    exp = _norm_template(expected)
    path, n = _resolve_aip_path(aip)
    if n > 1:
        _die(f"AP-CR-41: --aip '{aip}' is ambiguous ({n} AIP files match) — pass a fuller id. (no run-folder created.)")
    if path is None:
        print(f"  [warn] AP-CR-41: could not resolve --aip '{aip}' under .ai-work/aip/ — "
              f"template conformance UNVERIFIED (expected '{exp}'). Proceeding.")
        return
    actual_raw = _aip_template_source(path)
    if not actual_raw:
        msg = (f"AP-CR-41: AIP '{aip}' carries no `template_source` stamp (pre-CR-050 / hand-authored) — "
               f"conformance UNVERIFIED (expected '{exp}').")
        if strict_template:
            _die(msg + "\n  --strict-template set → refusing. (no run-folder created.)")
        print(f"  [warn] {msg} Proceeding (pass --strict-template to enforce).")
        return
    if _norm_template(actual_raw) != exp:
        _die(
            f"AP-CR-41: WRONG TEMPLATE. desk '{instance}' run_policy.aip_template expects '{exp}', "
            f"but AIP '{aip}' was instantiated from '{_norm_template(actual_raw)}' (template_source: {actual_raw}).\n"
            "  Re-create the driving AIP from the right template:\n"
            f"    /aiws-aip create --template {expected}\n"
            "  (no run-folder created.)"
        )
    # match → proceed (silent)


def _seed_related_aip(run_dir: Path, aip: str) -> None:
    """AP-CR-25 — record the driving AIP into run_request.yaml → related_aip."""
    p = run_dir / "run_request.yaml"
    txt = _read(p)
    line = f"related_aip: {aip}"
    if not txt.strip():
        _write(p, f"# run_request.yaml\n{line}\n")
    elif re.search(r"(?m)^related_aip:", txt):
        _write(p, re.sub(r"(?m)^related_aip:.*$", line, txt))
    else:
        _write(p, txt.rstrip("\n") + f"\n{line}\n")


def _seed_dispatch_meta(run_dir: Path, executor: str, tier: str, tier_meta: "dict | None") -> None:
    """CR-AIWS-2026-08-044/045 — record the dispatch's executor + tier + RESOLVED provider values
    into run_request.yaml (additive keys; ledger must read what actually ran, not just the names)."""
    p = run_dir / "run_request.yaml"
    txt = _read(p)
    lines = [f"executor: {executor or 'main_session'}"]
    if tier:
        lines.append(f"tier: {tier}")
        if tier_meta:
            lines.append(f"tier_provider: {tier_meta.get('provider', '')}")
            lines.append(f"tier_model: {tier_meta.get('model', '')}")
            lines.append(f"tier_effort: {tier_meta.get('effort', '')}")
    for line in lines:
        key = line.split(":", 1)[0]
        if re.search(rf"(?m)^{key}:", txt):
            txt = re.sub(rf"(?m)^{key}:.*$", line, txt)
        elif txt.strip():
            txt = txt.rstrip("\n") + f"\n{line}\n"
        else:
            txt = f"# run_request.yaml\n{line}\n"
    _write(p, txt)


def _seed_step_id(run_dir: Path, step_id: str) -> None:
    """CR-AIWS-2026-07-061 — record the driving AIP STEP id into run_request.yaml → related_task_card
    (the step's ASC IS the task card — no separate schema; agent_runtime_design §dispatch)."""
    if not (step_id or "").strip():
        return
    p = run_dir / "run_request.yaml"
    txt = _read(p)
    line = f"related_task_card: {step_id.strip()}"
    if not txt.strip():
        _write(p, f"# run_request.yaml\n{line}\n")
    elif re.search(r"(?m)^related_task_card:", txt):
        _write(p, re.sub(r"(?m)^related_task_card:.*$", line, txt))
    else:
        _write(p, txt.rstrip("\n") + f"\n{line}\n")


# --- CR-AIWS-2026-07-061: capability routing + step-dispatch eligibility (PURE helpers) ---------------
# run_agent.py stays a THIN orchestrator: these are state-prep/decision helpers the operator/main session
# calls to CHOOSE which `start` to invoke — the tool never spawns an agent and never calls an LLM.
_CEIL_ORDER = {"low": 1, "medium": 2, "high": 3}


def _cap_read(txt: str) -> dict:
    """Indentation-tolerant read of a `capability:` block (mirrors _instance_run_policy).
    CR-AIWS-2026-08-045 C2: also reads `tiers_supported: {tier: ceiling, ...}` (inline map)."""
    out: dict = {}
    m = re.search(r"(?m)^[ \t]*complexity_ceiling:[ \t]*([^#\n]*?)[ \t]*(?:#.*)?$", txt)
    if m:
        out["complexity_ceiling"] = m.group(1).strip().strip('"').strip("'")
    m = re.search(r"(?m)^[ \t]*task_kinds:[ \t]*\[([^\]]*)\]", txt)
    if m:
        out["task_kinds"] = [k.strip().strip('"').strip("'") for k in m.group(1).split(",") if k.strip()]
    m = re.search(r"(?m)^[ \t]*tiers_supported:[ \t]*\{([^}]*)\}", txt)
    if m:
        ts: dict = {}
        for pair in m.group(1).split(","):
            if ":" in pair:
                k, _, v = pair.partition(":")
                ts[k.strip().strip('"').strip("'")] = v.strip().strip('"').strip("'")
        if ts:
            out["tiers_supported"] = ts
    return out


# --- CR-AIWS-2026-08-045: execution tiers — 2-layer registry (tiers + provider profiles) ------
TIER_REGISTRY = DEV_ROOT / "agents" / "execution_tiers.yaml"


def _tier_registry() -> dict:
    """CR-AIWS-2026-08-045 C1 — read the 2-layer registry execution_tiers.yaml:
    layer 1 `tiers:` (abstract capability, provider-agnostic) · layer 2 `provider_profiles:`
    (per-provider map tier → {model, effort}; MVP ships only `claude`). Stdlib line parser over
    the registry's pinned shape (no YAML lib). Returns {'default_provider', 'tiers': {name: attrs},
    'providers': {name: {'effort_vocab': [...], 'map': {tier: {'model','effort'}}}}}."""
    txt = _read(TIER_REGISTRY)
    out: dict = {"default_provider": "", "tiers": {}, "providers": {}}
    if not txt:
        return out
    out["default_provider"] = _yaml_get(txt, "default_provider")
    sec = prov = cur_tier = ""
    for line in txt.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        s = line.split("#")[0].rstrip()
        body = s.strip()
        if indent == 0:
            sec = body[:-1] if body.endswith(":") else ""
            prov = cur_tier = ""
            continue
        if sec == "tiers":
            if indent == 2 and body.endswith(":"):
                cur_tier = body[:-1].strip()
                out["tiers"][cur_tier] = {}
            elif indent >= 4 and ":" in body and cur_tier:
                k, _, v = body.partition(":")
                out["tiers"][cur_tier][k.strip()] = v.strip()
        elif sec == "provider_profiles":
            if indent == 2 and body.endswith(":"):
                prov = body[:-1].strip()
                out["providers"][prov] = {"effort_vocab": [], "map": {}}
            elif prov and body.startswith("effort_vocab:"):
                m = re.search(r"\[([^\]]*)\]", body)
                if m:
                    out["providers"][prov]["effort_vocab"] = [
                        x.strip() for x in m.group(1).split(",") if x.strip()]
            elif prov and indent >= 6:
                m = re.match(r"^([A-Za-z0-9_\-]+):\s*\{\s*model:\s*([^,}]+),\s*effort:\s*([^,}]+)\s*\}\s*$", body)
                if m:
                    out["providers"][prov]["map"][m.group(1)] = {
                        "model": m.group(2).strip(), "effort": m.group(3).strip()}
    return out


def _desk_tiers(cap: dict) -> dict:
    """CR-AIWS-2026-08-045 C2 — a desk's tiers_supported map {tier: ceiling}. Absent → derive
    {standard: <complexity_ceiling>} from the legacy single-value ceiling (backward-compatible;
    desk with neither → {} and tier routing stays inert)."""
    ts = cap.get("tiers_supported") or {}
    if ts:
        return ts
    ceil = (cap.get("complexity_ceiling") or "").strip()
    return {"standard": ceil} if ceil else {}


def _route_tier(step: dict, cap: dict) -> dict:
    """CR-AIWS-2026-08-045 C3 — pick the CHEAPEST tier of ONE (already-chosen) desk whose ceiling
    covers the step's Difficulty; registry declaration order = cheap→expensive. PURE helper —
    activation-gated by the caller: only steps that opted in via `Assigned Agent:` are routed
    (CR-AIWS-2026-08-044 C0). Returns {'tier': name|None, 'reason': str}."""
    diff = (step.get("Difficulty") or "").strip().lower()
    need = _CEIL_ORDER.get(diff, 0)
    ts = _desk_tiers(cap)
    if not ts:
        return {"tier": None, "reason": "desk declares no tiers_supported / complexity_ceiling"}
    order = [t for t in _tier_registry().get("tiers", {}) if t in ts] or sorted(ts)
    for t in order:
        if _CEIL_ORDER.get((ts.get(t) or "").strip().lower(), 0) >= need:
            return {"tier": t, "reason": "cheapest tier with sufficient ceiling"}
    return {"tier": None, "reason": f"no supported tier ceiling covers Difficulty {diff!r} (refuse-under-capable)"}


def _resolve_tier(tier: str) -> dict:
    """CR-AIWS-2026-08-045 C4 — resolve tier → {provider, model, effort} via the registry's
    default_provider profile. Missing registry/provider/mapping → refuse (no guessing);
    runs BEFORE scaffolding, so no orphan run-folder."""
    reg = _tier_registry()
    prov = (reg.get("default_provider") or "").strip()
    if not prov or prov not in reg.get("providers", {}):
        _die(
            f"tier resolve (CR-AIWS-2026-08-045 C4): registry '{TIER_REGISTRY.name}' has no usable "
            "default_provider profile — declare provider_profiles.<default_provider> first. "
            "(no run-folder was created.)"
        )
    entry = reg["providers"][prov]["map"].get(tier)
    if not entry:
        _die(
            f"tier resolve (CR-AIWS-2026-08-045 C4): tier '{tier}' has no '{prov}' mapping in "
            f"'{TIER_REGISTRY.name}'. (no run-folder was created.)"
        )
    return {"provider": prov, "model": entry["model"], "effort": entry["effort"]}


def _instance_capability(inst_dir: Path) -> dict:
    """CR-AIWS-2026-07-061 — capability.{complexity_ceiling,task_kinds} from instance.yaml, else the
    referenced blueprint.yaml. {} when neither declares one (routing then falls back to Assigned Agent)."""
    cap = _cap_read(_read(_desk_yaml(inst_dir)))
    if not cap:
        mb = re.search(r"(?m)^[ \t]*blueprint_id:[ \t]*([^#\n]*?)[ \t]*(?:#.*)?$", _read(_desk_yaml(inst_dir)))
        bp_id = (mb.group(1).strip().strip('"').strip("'") if mb else "")
        if bp_id and bp_id != "null":
            _bpd = _resolve_blueprint_by_id(BLUEPRINTS, bp_id)  # alias-aware (CR-AIWS-2026-08-017)
            if _bpd is not None:
                cap = _cap_read(_read(_bpd / "blueprint.yaml"))
    return cap


def _route_step(step: dict, candidates: "list[dict]") -> dict:
    """CR-AIWS-2026-07-061 — capability routing (PURE). Match: complexity_ceiling >= step Difficulty AND
    task_kinds ∩ step Kind != empty. Tie-break: explicit `Assigned Agent` wins, else the lowest sufficient
    ceiling (cheapest capable agent). Returns {'matched': id|None, 'reason': str, 'rejected': {id: why}}.
    `candidates` = [{id, complexity_ceiling, task_kinds}]; the operator/main session builds it + acts on it."""
    # CR-AIWS-2026-08-044 C0 activation (CR-045 C3 r3): routing runs ONLY for steps that opted in
    # via `Assigned Agent:` — an explicit desk id, or `auto` (routing resolves the desk). A step
    # with no Assigned Agent is NOT dispatched (default = main session executes, no desk);
    # Difficulty/Kind alone are descriptive metadata, never dispatch intent.
    assigned = (step.get("Assigned Agent") or "").strip()
    if not assigned:
        return {"matched": None,
                "reason": "no dispatch: step carries no `Assigned Agent:` "
                          "(CR-AIWS-2026-08-044 C0 — default = main session, no desk)",
                "rejected": {}}
    if assigned.lower() == "auto":
        assigned = ""  # opt-in routing: the router resolves the desk (CR-AIWS-2026-08-045 C3)
    diff = (step.get("Difficulty") or "").strip().lower()
    need = _CEIL_ORDER.get(diff, 0)  # unspecified Difficulty → any ceiling qualifies
    kinds = {k.strip() for k in (step.get("Kind") or "").replace(";", ",").split(",") if k.strip()}
    ok: "list[tuple]" = []
    rejected: dict = {}
    for c in candidates:
        cid = c.get("id") or c.get("instance_id")
        ceil = _CEIL_ORDER.get((c.get("complexity_ceiling") or "").strip().lower(), 0)
        ck = {str(k).strip() for k in (c.get("task_kinds") or [])}
        if ceil < need:
            rejected[cid] = f"ceiling {c.get('complexity_ceiling')!r} < Difficulty {diff!r}"
            continue
        if kinds and not (kinds & ck):
            rejected[cid] = f"task_kinds {sorted(ck)} has no overlap with Kind {sorted(kinds)}"
            continue
        ok.append((ceil, cid))
    if assigned and any(cid == assigned for _, cid in ok):
        return {"matched": assigned, "reason": "explicit Assigned Agent", "rejected": rejected}
    if not ok:
        return {"matched": None, "reason": "no capable agent", "rejected": rejected}
    ok.sort()  # lowest sufficient ceiling first
    return {"matched": ok[0][1], "reason": "lowest sufficient ceiling", "rejected": rejected}


def _dispatch_eligible(aip_status: str, template_source: str, expected_outputs: "list[str]",
                       has_review_note: bool, multi_system: bool, inputs_resolvable: bool) -> "list[str]":
    """CR-AIWS-2026-07-061 §5 — machine-checkable step-dispatch eligibility (in-family; adapts the Hermes
    stage-4 predicate). Returns a list of failure reasons (empty = eligible). Difference from an external
    executor: an in-session sub-agent MAY use lookup_wiki_source.py at registered scope (raw stays CR-052-gated)."""
    reasons: "list[str]" = []
    if (aip_status or "").strip() != "active":
        reasons.append("AIP is not status: active")
    if "APPLY_CR" in (template_source or "").upper():
        reasons.append("APPLY_CR template — canonical apply, not delegable")
    for o in expected_outputs or []:
        ol = str(o).lower()
        if ("product/" in ol) or (".ai-work/truth/" in ol) or ("wiki" in ol):
            reasons.append(f"Expected Output escapes the Task Workspace (product//truth//wiki): {o}")
            break
    if has_review_note:
        reasons.append("step carries a Review Note / HARD GATE / HUMAN-interaction marker")
    if multi_system:
        reasons.append("multi_system project — v1 refuses (rule #12 never waived)")
    if not inputs_resolvable:
        reasons.append("inputs not fully resolvable (resolve Deferred lookups pre-dispatch)")
    return reasons


def cmd_list(a) -> None:
    """AP-CR-22 — list instances (id · display_name · blueprint · status) so HUMAN need not memorize ids."""
    insts = _all_instances()
    if not insts:
        print("no task desks")
        return
    print("task desks:")
    for d in insts:
        bp = _instance_field(d, "blueprint_id") or "(custom)"
        st = _instance_field(d, "status") or "?"
        pol = _instance_run_policy(d)
        gate = "  [aip_driven]" if pol.get("aip_driven", "").lower() in ("true", "yes") else ""
        drift = _drift_marker(d)  # AP-CR-27: [outdated]/[drift]/[no-baseline] vs the blueprint
        print(f"  {d.name}")
        print(f"      display: {_instance_display(d)}  ·  blueprint: {bp}  ·  status: {st}{gate}{drift}")


def cmd_memory(a) -> None:
    """AP-CR-22 — inspect an instance's confirmed memory (first CLI memory surface). Read-only."""
    inst_dir = _instance_dir(a.instance)
    mem = inst_dir / "memory"
    entries = _mem_entries(inst_dir)
    n_cand = len([ln for ln in _read(mem / "candidate_queue.jsonl").splitlines() if ln.strip()])
    print(f"memory — {_instance_display(inst_dir)}  ({inst_dir.name})")
    print(f"  confirmed_memory.jsonl: {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}")
    print(f"  candidate_queue.jsonl:  {n_cand} pending candidate(s)")
    prof = [f for f in _memory_profile_files(inst_dir) if f != "confirmed_memory.jsonl"]
    if not prof:  # custom no-Blueprint / no profile → enumerate whatever the instance materialized
        prof = sorted(p.name for p in mem.glob("*")
                      if p.is_file() and p.name not in ("confirmed_memory.jsonl", "candidate_queue.jsonl"))
    for f in prof:
        p = mem / f
        sz = len(_read(p).strip()) if p.exists() else None
        print(f"  {f}: {'MISSING' if sz is None else ('(empty)' if sz == 0 else str(sz) + ' chars')}")
    # CR-AIWS-2026-07-017: knowledge_digests/ is a memory SUBDIR — glob("*") above is files-only,
    # so list it explicitly (confirmed digests, HUMAN-gated via review-learning).
    dig = mem / "knowledge_digests"
    if dig.is_dir():
        digs = sorted(dig.glob("*.md"))
        print(f"  knowledge_digests/: {len(digs)} digest(s)")
        for d in digs:
            print(f"    - {d.name}")
    if a.full:
        print("--- confirmed_memory.jsonl (full) ---")
        for e in entries:
            print(e["_raw"] if "_raw" in e else json.dumps(e, ensure_ascii=False))
    elif entries:
        print("  index (id · type · tags) — use --full to dump:")
        for e in entries:
            if "_raw" in e:
                print(f"    (raw) {e['_raw'][:70]}")
                continue
            eid = e.get("id") or e.get("cm_id") or "?"
            typ = e.get("type") or e.get("kind") or "memory"
            tags = ", ".join(str(t) for t in (e.get("scope_tags") or [])) or "-"
            print(f"    [{eid}] {typ} · {tags}")


def cmd_upgrade(a) -> None:
    """AP-CR-27 — present blueprint↔instance drift for HUMAN per-change reconcile. Thin: it PRESENTS,
    never auto-applies, and NEVER writes the instance-learned layer (FR-AI-09). `--reconcile` records a
    HUMAN-confirmed decision (re-pin version + refresh snapshot + append reconcile_log + changelog)."""
    inst_dir = _instance_dir(a.instance)
    instance = inst_dir.name
    bp = _blueprint_dir(inst_dir)
    if bp is None:
        _die(f"desk '{instance}' is custom (no blueprint) — nothing to reconcile against.")
    pinned = _yaml_get(_read(inst_dir / "blueprint_ref.yaml"), "blueprint_version")
    current = _yaml_get(_read(bp / "blueprint.yaml"), "blueprint_version")
    print(f"upgrade — {instance}")
    print(f"  blueprint: {_rel(bp)}")
    print(f"  pinned blueprint_version: {pinned or '(none)'}   current: {current or '(none)'}")
    # establish the reconcile baseline if this instance was never snapshotted (setup, NOT a reconcile).
    if not (_snapshot_dir(inst_dir) / "blueprint.yaml").exists():
        print(f"  (no baseline snapshot — captured {_snapshot_blueprint(inst_dir, bp)} file(s) now)")
    # CR-AIWS-2026-08-074 C9 — write the BIRTH baseline once. Never rewritten, so this is safe to
    # call on every upgrade; a desk created before this CR gets a labelled retro-fit.
    _bn, _bhow = _capture_baseline(inst_dir, bp)
    if _bhow == "captured":
        print(f"  (birth baseline captured — {_bn} file(s) → {_rel(_baseline_dir(inst_dir))})")
    elif _bhow == "seeded-from-snapshot":
        print(f"  (birth baseline retro-fitted from the existing snapshot — {_bn} file(s); "
              "labelled a LOWER BOUND in SNAPSHOT_INFO.txt, not a true birth state)")
    drift, reason = _drift(inst_dir, bp)
    if not drift:
        print("  in sync — no drift. Nothing to reconcile.")
        return
    print(f"  DRIFT {reason}")
    if not a.reconcile:
        print("--- PRESENT for HUMAN per-change reconcile (tool does NOT auto-apply — FR-AI-09) ---")
        print(f"  blueprint changelog: {_rel(bp / 'changelog.md')}")
        bcl = _read(bp / "changelog.md").rstrip()
        print(bcl if bcl else "  (blueprint has no changelog.md)")
        print(f"  desk changelog:      {_rel(inst_dir / 'changelog.md')}")
        ref = _read(inst_dir / "blueprint_ref.yaml")
        m = re.search(r"(?ms)^customization_summary:.*?(?=^\S|\Z)", ref)
        print("  desk customization_summary (blueprint_ref.yaml):")
        print("    " + ((m.group(0).strip() if m else "(none)")).replace("\n", "\n    "))
        print("--- ownership invariant (FR-AI-09): desk-learned layer "
              "(memory/ training/ context/ local_guidelines) is NEVER auto-overwritten ---")
        # AP-CR-31: process is an instance-owned override asset — present the 3-way for HUMAN merge.
        inst_proc = inst_dir / "process"
        if inst_proc.is_dir():
            snap_proc = _snapshot_dir(inst_dir) / "process"
            print("--- process (AP-CR-31 §6D): desk OWNS its process — 4-way present, HUMAN merges per file ---")
            print(f"  base@birth:   {_rel(_baseline_dir(inst_dir) / 'process')}  "
                  "(immutable — CR-AIWS-2026-08-074 C9)")
            print(f"  base@pinned:  {_rel(snap_proc)}"
                  + ("" if snap_proc.is_dir() else "  (no process baseline yet — captured on confirm)"))
            print(f"  base@current: {_rel(bp / 'process')}  (resolved via process_docs)")
            print(f"  desk:         {_rel(inst_proc)}")
            _cust, _debt = _process_debt(inst_dir, bp)
            print(f"  → deliberate customization (desk vs base@birth): {', '.join(_cust) or '(none)'}")
            print(f"  → OUTSTANDING DEBT (base moved, desk did not): {', '.join(_debt) or '(none)'}")
            print("    Debt is computed against base@birth, so it survives a --reconcile; "
                  "base@pinned alone cannot tell debt from customization.")
            print("  Merge adopted base-process changes into the desk process yourself "
                  "(HUMAN-gated); keep governance_invariant steps.")
        print("  After deciding which blueprint changes to adopt, record the reconcile:")
        print(f'    py run_agent.py upgrade {instance} --reconcile --to-version "{current}" --decisions "adopted X, skipped Y"')
        return
    to_v = (a.to_version or current).strip()
    decisions = (a.decisions or "see instance changelog").replace("\n", " ")
    _append_reconcile_log(inst_dir, pinned or "?", to_v, decisions)
    _repin_version(inst_dir, to_v)
    # CR-AIWS-2026-08-074 C9 — this refreshes the POINTER only. `.atdb_baseline/` is deliberately
    # not touched here: recording a reconcile must not erase the mark that shows what the reconcile
    # actually left undone.
    cnt = _snapshot_blueprint(inst_dir, bp)
    _append_instance_changelog_reconcile(inst_dir, pinned or "?", to_v, decisions)
    _cust, _debt = _process_debt(inst_dir, bp)
    print(f"  reconcile recorded: re-pinned {pinned or '?'}->{to_v}; snapshot refreshed ({cnt} file(s)); "
          "reconcile_log + instance changelog appended.")
    print(f"  birth baseline UNCHANGED — outstanding process debt after this reconcile: "
          f"{', '.join(_debt) or '(none)'}")
    print("  NOTE: the desk-learned layer was NOT touched. Apply any adopted blueprint changes to the "
          "instance-override layer yourself (HUMAN-gated).")


def cmd_clone(a) -> None:
    """AP-CR-28 — create a NEW instance from an existing one: full-copy of the instance-owned layer
    EXCEPT run-history; new identity; copied confirmed memory auto-flagged clone_review:pending + cloned_from;
    candidate_queue reset; lineage recorded. Does NOT auto-run; does NOT modify the source."""
    src_dir = _instance_dir(a.source)
    src_id = src_dir.name
    display = (a.as_name or "").strip()
    if not display:
        _die('clone requires --as "<display_name>"')
    new_id = (a.new_id or "").strip() or _derive_id(display)
    if not _ID_RE.match(new_id):
        _die(f"invalid new instance id '{new_id}' (letters/digits/_/-, <=80 chars)")
    base, i = new_id, 2
    while (INSTANCES / new_id).exists():
        new_id = f"{base}_{i}"
        i += 1
        if not _ID_RE.match(new_id):
            _die(f"cannot derive a free id from '{base}'")
    dst_dir = INSTANCES / new_id
    _ensure_inside(dst_dir, "clone-target")
    # 1) full-copy instance-owned layer, EXCLUDING run-history + triage state
    copied = _copy_tree_guarded(src_dir, dst_dir, {"workspace", "training"})
    # 2) recreate EMPTY workspace + training skeleton (no run-history; candidate_queue reset)
    for sub in ("workspace/active_runs", "workspace/completed_runs",
                "workspace/handoff_artifacts", "workspace/step_outputs"):
        (dst_dir / sub).mkdir(parents=True, exist_ok=True)
    _write(dst_dir / "training" / "candidate_queue.jsonl", "")
    _write(dst_dir / "training" / "feedback_log.jsonl", "")
    _write(dst_dir / "training" / "periodic_review_log.md",
           f"# Periodic Improvement Review — {display}\n\n(cloned from {src_id} on {_today()}; no reviews yet)\n")
    # 3) new identity (instance_id + display_name + reset created_at/last_reviewed_at)
    _rewrite_instance_identity(dst_dir, new_id, display)
    # 4) auto-flag-review copied confirmed memory
    flagged = _flag_cloned_memory(dst_dir, src_id)
    # 5) lineage (blueprint_ref + changelog)
    _write_clone_lineage(dst_dir, src_id, a.why or "")
    print(f"cloned: {src_id} -> {new_id}  (display: {display})")
    print(f"  copied {copied} file(s) of the desk-owned layer (run-history NOT copied; candidate_queue reset)")
    print(f"  confirmed_memory: {flagged} entr{'y' if flagged == 1 else 'ies'} flagged clone_review:pending (+cloned_from)")
    print("  lineage recorded in blueprint_ref.yaml + changelog.md")
    print(f"  next: review carried-over memory for the new project →  py run_agent.py memory {new_id}   then  /aiws-agent-review-learning")
    print("  (clone does NOT run the agent; source desk unchanged.)")


def cmd_rename(a) -> None:
    """AP-CR-30 — controlled rename of an instance's machine identity. Validates the new id, hard-moves
    the folder, rewrites instance.yaml identity (+ optional names) and the instance's OWN run-history,
    and records the old id in `previous_ids` (accumulating alias) so old references still resolve via the
    alias-aware resolver. No cross-instance rewrite, no auto-run, no source duplication. Supersedes the
    AP-CR-23 id-immutability rule (rename only via this command)."""
    src_dir = _instance_dir(a.source)
    old_id = src_dir.name
    new_id = (a.to_id or "").strip()
    if not new_id:
        _die('rename requires --to <new_id>')
    if not _ID_RE.match(new_id):
        _die(f"invalid new instance id '{new_id}' (letters/digits/_/-, <=80 chars)")
    if new_id == old_id:
        _die(f"no-op: --to '{new_id}' equals the current id")
    if (INSTANCES / new_id).exists():
        _die(f"target id already exists: {new_id} (collision with a current instance id). Pick another --to.")
    for d in _all_instances():  # OQ-2 = refuse: keep alias resolution unambiguous
        if d.name == old_id:
            continue
        if new_id in _instance_previous_ids(d):
            _die(f"--to '{new_id}' is already an alias (previous_id) of task desk '{d.name}'. Pick another.")
    dst_dir = INSTANCES / new_id
    _ensure_inside(dst_dir, "rename-target")
    # validated → now hard-move + repoint identity (same instance, in place)
    shutil.move(str(src_dir), str(dst_dir))
    _rewrite_rename_identity(dst_dir, old_id, new_id, a.name, a.as_name)
    n_runs = _rewrite_own_run_history(dst_dir, new_id)
    _append_rename_changelog(dst_dir, old_id, new_id, a.why or "")
    print(f"renamed: {old_id} -> {new_id}")
    if a.name or a.as_name:
        bits = []
        if a.name:
            bits.append(f'instance_name="{a.name}"')
        if a.as_name:
            bits.append(f'display_name="{a.as_name}"')
        print(f"  names updated: {', '.join(bits)}")
    print(f"  folder moved; previous_ids += {old_id}  (old id still resolves via the alias-aware resolver)")
    print(f"  run-history repointed: {n_runs} run(s) updated (agent_instance_id)")
    print("  changelog.md entry appended (WHY).  (rename does NOT run the agent; no cross-desk rewrite.)")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="run_agent.py", description="Agent Runtime orchestrator (thin)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start", help="create run + ARC")
    s.add_argument("instance")
    s.add_argument("--task", default="", help="HUMAN task prompt (embedded in ARC)")
    s.add_argument("--slug", default="", help="short slug for the run id")
    s.add_argument("--aip", default="", help="driving AIP id (required when the desk declares run_policy.aip_driven=true)")
    s.add_argument("--step", default="", help="driving AIP STEP id (CR-AIWS-2026-07-061) — recorded as run_request.related_task_card")
    s.add_argument("--strict-template", action="store_true",
                   help="AP-CR-41: refuse if the driving AIP lacks a template_source stamp (default: warn)")
    s.add_argument("--plan-first", action="store_true", dest="plan_first",
                   help="CR-AIWS-2026-07-016: phase-1 only — draft run_plan.md, stop at awaiting_plan_confirm")
    s.add_argument("--executor", default="",
                   help="CR-AIWS-2026-08-044: executor for THIS dispatch (main_session | claude_subagent) — "
                        "a plan-time choice (AIP `Executor:` step field / HUMAN-stated); default = desk run_policy.executor")
    s.add_argument("--tier", default="",
                   help="CR-AIWS-2026-08-045: execution tier for this dispatch (must be in the desk's "
                        "tiers_supported; resolved to {model, effort} via execution_tiers.yaml)")
    s.set_defaults(fn=cmd_start)

    r = sub.add_parser("resume", help="refresh ARC + show run_state")
    r.add_argument("instance")
    r.add_argument("run_id")
    r.set_defaults(fn=cmd_resume)

    ex = sub.add_parser("extend", help="CR-AIWS-2026-08-046: extend an ACTIVE TW-backed run to the NEXT "
                                       "consecutive step (multi-step span; state-prep only)")
    ex.add_argument("instance")
    ex.add_argument("run_id")
    ex.add_argument("--step", default="", help="next consecutive AIP STEP id (required)")
    ex.add_argument("--task", default="", help="optional step task note for the step-brief")
    ex.set_defaults(fn=cmd_extend)

    cp = sub.add_parser("confirm-plan", help="CR-AIWS-2026-07-016: HUMAN confirms run_plan.md → status active (records by/at)")
    cp.add_argument("instance")
    cp.add_argument("run_id")
    cp.set_defaults(fn=cmd_confirm_plan)

    st = sub.add_parser("status", help="show one run or list runs")
    st.add_argument("instance")
    st.add_argument("run_id", nargs="?", default="")
    st.set_defaults(fn=cmd_status)

    sp = sub.add_parser("stop", help="mark stopped + move to completed_runs")
    sp.add_argument("instance")
    sp.add_argument("run_id")
    sp.add_argument("--reason", default="")
    sp.set_defaults(fn=cmd_stop)

    ls = sub.add_parser("list", help="list task desks (id · display_name · blueprint · status)")
    ls.set_defaults(fn=cmd_list)

    m = sub.add_parser("memory", help="show a task desk's confirmed memory (+ lessons/candidate counts)")
    m.add_argument("instance")
    m.add_argument("--full", action="store_true", help="dump all confirmed_memory entries")
    m.set_defaults(fn=cmd_memory)

    up = sub.add_parser("upgrade", help="present blueprint drift; record a HUMAN reconcile (AP-CR-27)")
    up.add_argument("instance")
    up.add_argument("--reconcile", action="store_true", help="record a HUMAN-confirmed reconcile (re-pin + snapshot + log)")
    up.add_argument("--to-version", default="", help="blueprint_version to re-pin to (default: current)")
    up.add_argument("--decisions", default="", help="one-line summary of which blueprint changes were adopted/skipped")
    up.set_defaults(fn=cmd_upgrade)

    cl = sub.add_parser("clone", help="create a new task desk from an existing one (AP-CR-28)")
    cl.add_argument("source", help="source desk (fuzzy id / role word / display_name)")
    cl.add_argument("--as", dest="as_name", default="", help="display_name for the new task desk (required)")
    cl.add_argument("--id", dest="new_id", default="", help="explicit new instance_id (default: derived from --as)")
    cl.add_argument("--why", default="", help="why this clone (recorded in lineage + changelog)")
    cl.set_defaults(fn=cmd_clone)

    rn = sub.add_parser("rename", help="rename a task desk's machine id — schema key `instance_id` — (+folder) with a previous_ids alias (AP-CR-30)")
    rn.add_argument("source", help="source desk (fuzzy id / role word / display_name / previous id)")
    rn.add_argument("--to", dest="to_id", default="", help="new instance_id (required; validated + collision-checked)")
    rn.add_argument("--name", dest="name", default="", help="new instance_name (optional)")
    rn.add_argument("--as", dest="as_name", default="", help="new display_name (optional)")
    rn.add_argument("--why", default="", help="why this rename (recorded in changelog)")
    rn.set_defaults(fn=cmd_rename)

    a = p.parse_args(argv)
    # CR-AIWS-2026-08-074 C7/C12 — every verb below reads desks, so the desk-root check runs here,
    # once, for all of them (DP-074-F = a). Ambiguous → refuse; legacy branch → one-line warning.
    try:
        enforce_desk_root()
    except DeskRootAmbiguous as e:
        raise SystemExit("error: " + str(e))
    a.fn(a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
