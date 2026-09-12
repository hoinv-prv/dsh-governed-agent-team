#!/usr/bin/env python3
"""Orchestrate AIP execution: start, resume, jump-to-step, status, list-steps.

This tool wires together init_workspace / set_current_step /
build_active_step_context so one command prepares the workspace to work on
a specific AIP step. It does NOT execute the step content — it just
guarantees workspace state is ready and points the LLM at the right place.

Subcommands:

  start   <aip>                  # create workspace + point STEP-01 + build ASC
  resume  <aip>                  # read existing workspace pointer + rebuild ASC
  step    <aip> --step STEP-XX   # jump to a specific step (creates/updates)
  status  <aip>                  # print current pointer + workspace summary
  list    <aip>                  # list all steps in the AIP with titles

In every mode `<aip>` accepts either an AIP id (e.g. AIP-EXEC-001) or a
file path. Task id defaults to `TASK-YYYYMMDD-<aip-slug>`; override with
`--task-id`.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import io
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (account_identity_state,   # CR-AIWS-2026-08-117 C2
    CAPTURE_BACKLOG_BUDGET, CAPTURE_BACKLOG_STALE_DAYS,  # CR-AIWS-2026-08-125 C2
                       # noqa: E402
    find_ai_work_root,
    locator_str,
    parse_aip_steps,
    read_account_id,
    parse_frontmatter,
    portable_locator,
    read_jsonl,
    read_text,
    resolve_locator,
    today,
    write_text,
)

TOOL = Path(__file__).resolve().parent

# CR-AIWS-2026-07-056 T2b: reuse the ONE inbox-writer (Rule 2 — no second one to drift).
from append_capture import (  # noqa: E402
    append_record as _append_capture_record,
    build_capture_record as _build_capture_record,
    inbox_has_id as _inbox_has_id,
)

_PENDING_KV_RE = re.compile(r'(\w+)="([^"]*)"')


def _capture_type_label(cap_type: str) -> str:
    """CR-AIWS-2026-08-075 C3 — a human label DERIVED from the capture type, not looked up.

    Deliberately mechanical (r2 §6). A hand-written 16-entry map would be a SECOND vocabulary surface
    that can drift from CAPTURE_TYPE_ENUM, and it would miss the 8 `type` values that already exist in
    the corpus outside that enum (15 records, one in an active workspace) — those would fall to a
    generic fallback and lose the only label they could have had. Deriving means an unknown type still
    gets a correct label for free.

      wiki_meta_update_candidate  -> "wiki meta update"
      tooling_opportunity_candidate -> "tooling opportunity"
      insight                     -> "insight"
    """
    base = cap_type[: -len("_candidate")] if cap_type.endswith("_candidate") else cap_type
    return (base.replace("_", " ").strip() or cap_type or "capture")


def _capture_title_content(kv: "dict", artifact: str) -> "tuple[str, str]":
    """CR-AIWS-2026-08-075 C3 — build (title, content) from the entry's OWN declared kind.

    Before this, both were hardcoded to the retrieval-gap wording, so every pre-flight capture was
    labelled a retrieval gap whatever its `type`. Measured on the corpus at apply time: 22 records
    carried that title and 7 of them were not retrieval at all (5 tooling_opportunity_candidate,
    2 guideline_improvement_candidate) — e.g. "retrieval gap: CR §2 target table".

    The discriminator is NOT `type == "retrieval_gap"` as CR §2 row 3 says: no such type exists, in the
    enum or in the corpus (`retrieval_gap` is the Capture-flag token printed by lookup_wiki_source.py).
    A literal reading would be a dead branch that regressed 100% of entries. What actually marks a
    retrieval entry is `candidate_kind=retrieval_improvement`, or the presence of a `lookup_query=` —
    either one means a lookup missed, which is what the old wording describes.

    INVARIANT: the title must END with the bare artifact token. test_pending_capture_sweep.py:143 keys
    its result dict on `title.split()[-1]`, so anything appended after the artifact silently turns that
    test's lookups into empty dicts rather than a clean failure.
    """
    query = kv.get("lookup_query", "").strip()
    if kv.get("candidate_kind", "").strip() == "retrieval_improvement" or query:
        return (f"retrieval gap: {artifact}",
                (f"lookup miss for '{artifact}' (query: {query}). {kv.get('reason', '')}").strip())

    label = _capture_type_label(kv.get("type", ""))
    reason = kv.get("reason", "").strip()
    if not reason:
        # `reason=` is optional in the line grammar but `content` is error-level required by
        # lint_workspace, so an empty string would import a record that cannot pass finalize lint.
        # A scaffold sentence is honest here — unlike suggested_target (DP-025-A) content is prose,
        # not a value triage routes on, so filling it invents no decision. Warn where the author is.
        print(f"warn: pending-capture entry for '{artifact}' has no reason=, content scaffolded: "
              f"type={kv.get('type', '')}", file=sys.stderr)
        reason = f"flagged during pre-flight; no reason= was given on the [PENDING] line."
    return (f"{label}: {artifact}", f"{label} for '{artifact}'. {reason}".strip())


_AIP_NUM_IN_NAME = re.compile(r"AIP-[A-Za-z]+-(\d+)")


def _names_truth_zone(artifact: str, ai_work: Path) -> bool:
    """Does this free-text `artifact=` token name something in the Truth zone?

    HEURISTIC BY CONSTRUCTION — and that is why its caller WARNS and never refuses. `artifact=`
    on a `[PENDING]` line is prose the author typed, not a resolved path: it can be a full path,
    a bare filename, or a description. So this can miss (a token that names Truth some other way)
    and it can over-match (a path with a `truth/` segment elsewhere). A gate built on a guess
    would refuse legitimate captures and teach people to route around the sweep; a warning that
    guesses wrong costs one stderr line.

    Expressed by ZONE, not by a filename list (CR-AIWS-2026-08-130 / OP-1129-01): a bare token is
    matched by globbing the Truth tree itself, so this keeps working when Truth grows a file.
    """
    tok = (artifact or "").strip().strip("`\"'" ).replace("\\", "/")
    if not tok:
        return False
    if "truth/" in tok.lower():
        return True
    name = tok.rsplit("/", 1)[-1].strip()
    if not name:
        return False
    cands = [name] if "." in name else [name, name + ".md"]
    truth = ai_work / "truth"
    for c in cands:
        try:
            if next(truth.rglob(c), None) is not None:
                return True
        except Exception:
            pass
    return False


def _sweep_pending_captures(aip_path: Path, ws: Path) -> None:
    """CR-AIWS-2026-07-056 T2b (R4-04). Import `## Pre-flight Pending Captures` `[PENDING]` entries
    into the workspace inbox and mark each `[IMPORTED YYYY-MM-DD]` in the AIP.

    Before this, create.md said `run start` did this automatically while run_aip.py did nothing —
    an agent trusting the authoring doc lost every pre-flight capture silently. Now the tool does it.
    Fail-soft per line (one malformed entry never aborts the sweep); idempotent (an already-IMPORTED
    line is skipped and the inbox dup-guard prevents re-adding); ALWAYS logs (even on 0 matches)."""
    text = read_text(aip_path)
    lines = text.splitlines(keepends=True)
    # locate the section body
    in_section = False
    imported = skipped = malformed = 0
    inbox = ws / "08_capture_inbox.jsonl"
    existing_ids = set()
    if inbox.exists():
        for ln in io.open(inbox, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try:
                    existing_ids.add(json.loads(ln).get("id"))
                except json.JSONDecodeError:
                    pass

    # CR-AIWS-2026-08-130 wave / AIP-EXEC-1132: id mang tien to so AIP.
    # Truoc day sweep mint `CAP-NNN` dem lai tu 1 trong TUNG workspace, nen `CAP-001` ton tai o
    # 104 workspace (do 2026-08-29 tren 923 record) va moi phep doi chieu cheo bang cap_id deu cho
    # duong tinh gia — chinh la ca CAP-1089-03 da do. Tang backlog da mien nhiem tu truoc nho
    # `backlog_id_for` SUY RA id tu (AIP, cap_id); day la cung nguyen ly, ap cho tang inbox.
    _aip_num = _AIP_NUM_IN_NAME.search(aip_path.name)
    _cap_prefix = "CAP-%s-" % _aip_num.group(1) if _aip_num else "CAP-"

    def _next_cap_id() -> str:
        # Fail-soft: khong suy duoc so AIP thi `_cap_prefix` la "CAP-" va dang id tro ve nhu cu.
        n = 1
        while f"{_cap_prefix}{n:02d}" in existing_ids or f"{_cap_prefix}{n:03d}" in existing_ids:
            n += 1
        cid = f"{_cap_prefix}{n:02d}" if _aip_num else f"{_cap_prefix}{n:03d}"
        existing_ids.add(cid)
        return cid

    # Truth-zone guard (CR-AIWS-2026-08-130 §5) resolves its root ONCE, fail-soft. A heuristic
    # warning must never be able to break the sweep: `find_ai_work_root` raises when there is no
    # `.ai-work/` ancestor, which is exactly the shape of a sandboxed fixture. No root -> no check.
    try:
        _truth_root = find_ai_work_root(ws) / ".ai-work"
    except BaseException:
        _truth_root = None

    changed = False
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped.startswith("## "):
            in_section = stripped.lower().startswith("## pre-flight pending captures")
            continue
        if not in_section:
            continue
        if not stripped.startswith("- [PENDING]"):
            continue
        kv = dict(_PENDING_KV_RE.findall(stripped))
        if not kv.get("type"):
            malformed += 1
            print(f"warn: pending-capture entry missing type=, skipped: {stripped[:70]}",
                  file=sys.stderr)
            continue
        artifact = kv.get("artifact", "(unnamed artifact)")
        if _truth_root is not None and _names_truth_zone(artifact, _truth_root):
            # CR-AIWS-2026-08-130 §5 (HUMAN ruled 2026-08-29): Truth input khong sinh
            # `[retrieval_gap]` — Truth dung TREN tang routing cua wiki (Wiki_Truth_History_Spec §2).
            # Canh bao, KHONG tu choi: "capture first, curate later" la nguyen tac goc, va phep do
            # nay la heuristic tren van xuoi. Cung khuon DP-025-A: bao o day vi tac gia con dang o
            # day; doi den triage la muon.
            print(f"warn: pending-capture entry names a Truth-zone artifact "
                  f"('{artifact}') — Truth khai o '## Required Truth Inputs' va KHONG mang "
                  f"[retrieval_gap] (CR-AIWS-2026-08-130). Row van duoc import; xoa dong "
                  f"[PENDING] neu day dung la Truth input.", file=sys.stderr)
        if not kv.get("suggested_target"):
            # DP-025-A: de TRONG + bao ngay, KHONG tu dien mac dinh theo `type`. Mot gia tri
            # do may doan khong phan biet duoc voi mot gia tri nguoi chon, va triage sau do
            # se route theo no. Bao o day vi tac gia con dang o day; doi den lint la muon.
            print(f"warn: pending-capture entry has no suggested_target=, left blank: "
                  f"{stripped[:70]}", file=sys.stderr)
        cid = _next_cap_id()
        _title, _content = _capture_title_content(kv, artifact)   # CR-AIWS-2026-08-075 C3
        try:
            rec = _build_capture_record(
                cid, kv["type"],
                title=_title,
                content=_content,
                candidate_kind=kv.get("candidate_kind", ""), reusable=True,
                suggested_target=kv.get("suggested_target", ""),
                source_refs=[aip_path.name])
        except ValueError as e:
            malformed += 1
            print(f"warn: could not build capture from entry, skipped: {e}", file=sys.stderr)
            continue
        if _inbox_has_id(inbox, cid):
            skipped += 1
            continue
        _append_capture_record(inbox, rec)
        imported += 1
        # surgical: mark the source line [IMPORTED YYYY-MM-DD] (sanctioned AIP write, CR-040 list)
        lines[i] = raw.replace("- [PENDING]", f"- [IMPORTED {today()}]", 1)
        changed = True
    if changed:
        write_text(aip_path, "".join(lines))
    if imported or skipped or malformed:
        print(f"pending captures: imported {imported}, skipped {skipped} (dup/already-imported), "
              f"malformed {malformed} -> {inbox}")
    else:
        print("No pending captures found in AIP")

# --- Project-boundary guardrails --------------------------------------------
# run_aip.py is allowed to auto-run without per-call approval, so it must
# refuse any operation that would read or write outside the project's
# `.ai-work/` tree. These helpers enforce that contract; every path the tool
# touches must resolve strictly inside `ai_work_root`.

_TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-]{0,63}$")


def _ensure_inside(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        raise SystemExit(
            f"error: {label} path escapes project boundary\n"
            f"  path: {resolved}\n"
            f"  must be inside: {root.resolve()}"
        )
    return resolved


def _safe_task_id(task_id: str) -> str:
    if not _TASK_ID_RE.match(task_id or ""):
        raise SystemExit(
            f"error: invalid --task-id '{task_id}'\n"
            f"  allowed: [A-Za-z0-9][A-Za-z0-9_-]{{0,63}} (no path separators, no '..')"
        )
    return task_id


def _aip_account_scope(f: Path, ai_work: Path) -> str:
    """Account namespace of an AIP path: '<account_id>' under aip/<account_id>/<kind>/,
    or '(legacy)' for flat aip/<kind>/ AIPs (CR-015 v2)."""
    try:
        parts = f.relative_to(ai_work / "aip").parts
    except ValueError:
        return "(unknown)"
    if not parts or parts[0] in ("exec", "plans", "local"):
        return "(legacy)"
    return parts[0]


def _resolve_aip(aip_ref: str, ai_work: Path) -> tuple[Path, dict]:
    """Return (path, frontmatter) for an AIP id or path.

    When `aip_ref` is an AIP id, walk the full AIP zone and collect every
    file whose frontmatter matches. If more than one file claims the same
    id, fail loudly instead of silently picking the first match — this
    is the FND-030 / FND-032 guardrail.

    Accepts a portable `__PROJECT_ROOT__/…` locator (CR-AIWS-2026-07-022), resolved
    against the project root (NOT the CWD), plus a plain/absolute path or a bare id.
    """
    p = resolve_locator(aip_ref, ai_work.parent)
    if p.is_file():
        path = _ensure_inside(p, ai_work, "AIP file")
    else:
        # CR-015 v2: AIPs live under per-account folders aip/<account_id>/<kind>/ AND legacy
        # flat aip/<kind>/ — scan the whole aip tree (recursive, incl. done/).
        aip_root = ai_work / "aip"
        matches: list[Path] = []
        if aip_root.is_dir():
            for f in sorted(aip_root.rglob("*.md")):
                try:
                    meta, _ = parse_frontmatter(read_text(f))
                except Exception:
                    continue
                if meta.get("artifact_id") == aip_ref:
                    matches.append(f)
        if not matches:
            raise SystemExit(f"error: cannot resolve AIP '{aip_ref}'")
        if len(matches) > 1:
            # A bare id may legitimately recur across account folders — prefer the CURRENT
            # account's match; only error if still ambiguous within one scope.
            acct = read_account_id(ai_work)
            pref = [m for m in matches if _aip_account_scope(m, ai_work) == acct] if acct else []
            if len(pref) == 1:
                matches = pref
            else:
                joined = "\n  ".join(str(m) for m in matches)
                raise SystemExit(
                    f"error: AIP id '{aip_ref}' resolves to {len(matches)} files:\n"
                    f"  {joined}\n"
                    f"refusing to pick silently — pass the AIP file path, or fix the collision "
                    f"(run 'python .ai-work/tooling/lint_all.py')."
                )
        path = matches[0].resolve()
    meta, _ = parse_frontmatter(read_text(path))
    return path, meta


def _default_task_id(aip_meta: dict) -> str:
    # CR-AIWS-2026-07-064 D1 (Rule 9): AIP frontmatter is DATA — a bare `artifact_id:` key parses
    # to [] and `.lower()` on it aborted the run (cmd_status has no lint gate, and lint_aip only
    # checks truthiness, so a non-string id reaches here on both paths).
    aid = (locator_str(aip_meta.get("artifact_id")) or "AIP").lower().replace("aip-", "")
    return f"TASK-{today().replace('-', '')}-{aid}"


def _run(cmd: list[str]) -> int:
    r = subprocess.run(cmd, encoding="utf-8")
    return r.returncode


def _lint_gate(aip_path: Path) -> bool:
    """Fail-fast lint gate before start/resume (CR-AIWS-2026-05-037 Option A).

    Runs lint_aip on the target AIP. lint_aip (non-strict) returns 2 when the
    AIP has ERRORS and 0 otherwise — so WARNINGS do NOT block, matching
    aiws-aip run SKILL.md §'Pre-start AIP validation'. Returns True to proceed,
    False if the AIP has lint errors (caller must refuse). If the lint tool is
    missing, do not hard-block aiws-aip run.
    """
    lint = TOOL / "lint_aip.py"
    if not lint.exists():
        return True
    print(f"lint-gate: checking {aip_path.name} (CR-037 Option A) ...")
    rc = _run([sys.executable, str(lint), "--path", str(aip_path)])
    if rc != 0:
        print(
            f"error: lint_aip reported errors on {aip_path.name} — refusing to "
            f"start/resume.\n"
            f"  fix the AIP to 0 errors, then retry (see lint output above).",
            file=sys.stderr,
        )
        return False
    return True


def _steps(aip_path: Path) -> list[dict]:
    _, body = parse_frontmatter(read_text(aip_path))
    return parse_aip_steps(body)


def _workspace_dir(ai_work: Path, task_id: str) -> Path:
    _safe_task_id(task_id)
    ws = ai_work / "workspaces" / task_id
    return _ensure_inside(ws, ai_work / "workspaces", "workspace")


def _new_workspace_dir(ai_work: Path, task_id: str, account_id: str) -> Path:
    """Target dir for a NEW workspace (CR-015 v2): a per-account folder when account_id is set,
    else legacy flat."""
    _safe_task_id(task_id)
    base = (ai_work / "workspaces" / account_id) if account_id else (ai_work / "workspaces")
    return _ensure_inside(base / task_id, ai_work / "workspaces", "workspace")


def _read_pointer(ws: Path) -> dict | None:
    p = ws / ".current_step.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _resolve_workspace(ai_work: Path, meta: dict, explicit_task_id: str | None,
                       *, allow_today_fallback: bool = True) -> Path:
    """Resolve an AIP's workspace (CR-AIWS-2026-06-015 Facet 5a).

    Order: explicit --task-id → reverse-scan each workspace's `.current_step.json`
    back-link (`aip_id`) → `runtime_workspace` frontmatter pointer (F5b) →
    today()-based fallback. This replaces blind `TASK-<today()>-<slug>` derivation so
    `resume`/`status` work across days (fixes the today() bug). If MORE THAN ONE live
    workspace maps to the AIP, STOP and ask the human (possible bug) — never silent-pick.
    """
    ws_root = ai_work / "workspaces"
    if explicit_task_id:
        tid = _safe_task_id(explicit_task_id)
        flat = ws_root / tid
        if flat.is_dir():
            return _ensure_inside(flat, ws_root, "workspace")
        if ws_root.is_dir():  # search per-account folders for the task dir
            for acct in sorted(d for d in ws_root.iterdir()
                               if d.is_dir() and not d.name.startswith(".")):
                cand = acct / tid
                if cand.is_dir():
                    return _ensure_inside(cand, ws_root, "workspace")
        acct_id = read_account_id(ai_work)  # not found → default to current account's folder
        base = (ws_root / acct_id) if acct_id else ws_root
        return _ensure_inside(base / tid, ws_root, "workspace")
    aip_id = meta.get("artifact_id", "")
    matches: list[Path] = []
    if aip_id and ws_root.is_dir():  # reverse-scan, RECURSIVE (per-account + legacy workspaces)
        for ptr_file in sorted(ws_root.rglob(".current_step.json")):
            ws = ptr_file.parent
            ptr = _read_pointer(ws)
            if ptr and ptr.get("aip_id") == aip_id:
                matches.append(ws)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        joined = "\n  ".join(str(m) for m in matches)
        raise SystemExit(
            f"error: {len(matches)} workspaces map to '{aip_id}' (possible bug):\n  {joined}\n"
            f"  pass --task-id <TASK-ID> to choose which workspace to use."
        )
    # 0 matches: try a frontmatter runtime_workspace pointer (F5b), else today() fallback
    rw = str(meta.get("runtime_workspace", "")).strip()
    if rw:
        cand = resolve_locator(rw, ai_work.parent)
        return _ensure_inside(cand, ws_root, "workspace")
    if allow_today_fallback:  # fallback now lands under the current account's folder
        acct_id = read_account_id(ai_work)
        base = (ws_root / acct_id) if acct_id else ws_root
        return _ensure_inside(base / _default_task_id(meta), ws_root, "workspace")
    raise SystemExit(
        f"error: no workspace found for '{aip_id}' — run 'start' first or pass --task-id")


def _write_runtime_workspace(aip_path: Path, ws: Path, ai_work: Path, force: bool) -> None:
    """F5b (CR-AIWS-2026-06-015): stamp a WRITE-ONCE `runtime_workspace` provenance
    pointer into the AIP frontmatter. Set only if absent (write-once); on --force,
    update to the new workspace. Surgical line-level edit — never reformats the rest of
    the frontmatter, never touches the body. NOT runtime state (AIP_Detail_Spec §2.3)."""
    text = read_text(aip_path)
    m = re.match(r"^(---\s*\n)(.*?\n)(---\s*\n)(.*)$", text, re.DOTALL)
    if not m:
        return
    head, fm, fence, body = m.group(1), m.group(2), m.group(3), m.group(4)
    loc = portable_locator(ws, ai_work.parent)
    line = f"runtime_workspace: {loc}\n"
    lines = fm.splitlines(keepends=True)
    has = any(l.startswith("runtime_workspace:") for l in lines)
    if has and not force:
        # CR-AIWS-2026-08-117 C3 — write-once GIỮ NGUYÊN; thứ đổi là nó thôi IM LẶNG.
        # Trước CR này đây là một `return` trần: nếu AIP đã trỏ workspace A mà ai đó chạy
        # `start --task-id B`, thì workspace B được tạo, pointer trỏ B, còn frontmatter vẫn khai A —
        # và không một dòng nào được in. Provenance của AIP nói một đằng, lượt chạy sống đi một nẻo.
        # Chỉ nói khi THẬT SỰ lệch (DP-117-E): con trỏ trùng là ca thường của mọi `start` lặp lại,
        # cảnh báo ở đó là nag chứ không phải tín hiệu.
        old = next((l.split(":", 1)[1].strip() for l in lines
                    if l.startswith("runtime_workspace:")), "")
        if old and old.replace("\\", "/").rstrip("/") != loc.replace("\\", "/").rstrip("/"):
            print(f"note: AIP đã trỏ workspace khác — frontmatter GIỮ NGUYÊN (write-once).\n"
                  f"  runtime_workspace (trong AIP): {old}\n"
                  f"  workspace lượt này:            {loc}\n"
                  f"  Muốn cập nhật con trỏ thì chạy lại với --force.")
        return  # write-once — leave the existing pointer untouched
    out: list[str] = []
    placed = False
    for l in lines:
        if l.startswith("runtime_workspace:"):
            out.append(line)  # force-update in place
            placed = True
            continue
        if l.startswith("updated_at:") and not has:
            out.append(line)  # insert just before updated_at (matches §5.4 schema order)
            placed = True
        out.append(l)
    if not placed:
        out.append(line)
    write_text(aip_path, head + "".join(out) + fence + body)


def _flip_status_active(aip_path: Path) -> None:
    """CR-AIWS-2026-07-040 T2 (R3-10): flip frontmatter `status: draft` → `status: active` at
    `start`. Surgical line-level edit (mirrors _write_runtime_workspace): never reformats the
    rest of the frontmatter, never touches the body; a status other than draft is left as-is."""
    text = read_text(aip_path)
    m = re.match(r"^(---\s*\n)(.*?\n)(---\s*\n)(.*)$", text, re.DOTALL)
    if not m:
        return
    head, fm, fence, body = m.group(1), m.group(2), m.group(3), m.group(4)
    lines = fm.splitlines(keepends=True)
    out: list[str] = []
    changed = False
    for l in lines:
        if l.startswith("status:") and l.split(":", 1)[1].strip() == "draft":
            eol = "\r\n" if l.endswith("\r\n") else "\n"
            out.append(f"status: active{eol}")
            changed = True
        else:
            out.append(l)
    if changed:
        write_text(aip_path, head + "".join(out) + fence + body)
        print("status: draft -> active (CR-040)")


def _triage():
    """`triage_capture`, imported LAZILY (CR-AIWS-2026-08-125 C2).

    `close` and the `status` backlog rollup need it; `start` / `resume` / `step` must not fail to run
    because a close-only sibling is absent. Found by a test fixture that copies ten named tooling files
    into a temp tree: a top-level import made every `start` in that fixture exit 1 with an ImportError,
    which is also what a partial checkout would do.
    """
    import triage_capture
    return triage_capture


# ---------- subcommands ----------

def cmd_start(ns) -> int:
    ai_work = find_ai_work_root(Path.cwd()) / ".ai-work"
    aip_path, meta = _resolve_aip(ns.aip, ai_work)
    if not _lint_gate(aip_path):
        return 2
    task_id = ns.task_id or _default_task_id(meta)
    account_id = read_account_id(ai_work)  # CR-015 v2: new workspaces under per-account folder
    ws = _new_workspace_dir(ai_work, task_id, account_id)
    if ws.exists() and not ns.force:
        print(
            f"error: workspace already exists: {ws}\n"
            f"  use 'resume' to continue, or pass --force to reinitialize",
            file=sys.stderr,
        )
        return 2

    init_cmd = [
        sys.executable, str(TOOL / "init_workspace.py"),
        "--task-id", task_id,
        "--aip", meta.get("artifact_id", ""),
        "--aip-path", str(aip_path),
        "--aip-type", meta.get("artifact_type", "").replace("aip_", ""),
    ]
    if account_id:
        init_cmd += ["--account", account_id]
    if ns.title:
        init_cmd += ["--title", ns.title]
    if ns.force:
        init_cmd.append("--force")
    rc = _run(init_cmd)
    if rc != 0:
        return rc

    # F5b: stamp the write-once runtime_workspace provenance pointer into the AIP.
    try:
        _write_runtime_workspace(aip_path, ws, ai_work, ns.force)
    except Exception as e:  # noqa: BLE001
        print(f"warn: could not write runtime_workspace pointer: {e}", file=sys.stderr)

    # CR-AIWS-2026-07-040 T2 (R3-10): `start` owns the draft → active lifecycle edge —
    # sanctioned AIP write #2 (same surgical mechanism as runtime_workspace; DP-040-2=A).
    # Only draft flips; any other status is left untouched (idempotent — retrospective
    # AIPs and resume/step never write status; close still flips → done by hand).
    #
    # CR-AIWS-2026-08-117 C2 — MỘT điều kiện, đặt ở ĐÂY chứ không trong `_flip_status_active`:
    # hàm đó là phép biến đổi văn bản thuần và đã có test pin hợp đồng của nó
    # (`test_run_aip_status_flip` case 1). Quyết định *"có được phép flip không"* thuộc về lượt chạy.
    #
    # Luật được thi hành: `CR-AIWS-2026-08-076` C4 — một AIP `active` là một AIP đang được thi hành
    # DƯỚI TÊN MỘT NGƯỜI; nếu tên đó do máy suy ra thì thứ hỏng là quy trách nhiệm, và nó hỏng im lặng.
    # Trước CR-117 luật này chỉ tồn tại bằng văn xuôi trong `create.md`/`run.md`, và CR-076 đã tự tiên
    # đoán *"điều kiện viết bằng văn xuôi là điều kiện sẽ bị quên"*. IR-2026-08-20 là lần kiểm nghiệm
    # đầu tiên và nó đúng.
    #
    # KHÔNG chặn `start` (DP-117-A): `create.md` chỉ đòi không-flip, và `account_id.py` đánh dấu
    # `provisional` cho CẢ nguồn `env` — chặn hẳn sẽ làm mọi CI dùng `AIWS_ACCOUNT_ID` vĩnh viễn không
    # chạy được AIP nào. Đo 2026-08-20: KHÔNG tool nào trong repo đòi `status: active`
    # (`council_tally._aip_ok` chỉ kiểm `.current_step.json` tồn tại), nên giữ `draft` không chặn gì.
    _acct_id, _acct_state = account_identity_state(ai_work)
    if _acct_state != "ratified":
        _why = ("chưa có `account_id` trong .ai-work/account_info.yaml"
                if _acct_state == "unset"
                else f"`account_id: {_acct_id}` là PROVISIONAL (nguồn: {_acct_state.split(':', 1)[1]})")
        print(f"status: giữ `draft` — danh tính account chưa được phê ({_why}).\n"
              f"  Một AIP `active` là một AIP đang được thi hành DƯỚI TÊN MỘT NGƯỜI (CR-AIWS-2026-08-076 C4).\n"
              f"  Phê bằng: py .ai-work/tooling/account_id.py set --account-id <id>\n"
              f"  Rồi chạy lại `start` (workspace đã tạo xong, không mất gì).")
    else:
        try:
            _flip_status_active(aip_path)
        except Exception as e:  # noqa: BLE001
            print(f"warn: could not flip status draft->active: {e}", file=sys.stderr)

    # CR-AIWS-2026-07-056 T2b (R4-04): sweep `## Pre-flight Pending Captures` into the inbox and
    # mark them [IMPORTED] — the tool now does what create.md always claimed it did. Fail-soft: a
    # broken sweep must never fail `start` (the workspace is already up).
    try:
        _sweep_pending_captures(aip_path, ws)
    except Exception as e:  # noqa: BLE001
        print(f"warn: pending-capture sweep failed (non-fatal): {e}", file=sys.stderr)

    steps = _steps(aip_path)
    if not steps:
        print(f"warn: AIP has no parseable steps; workspace initialized only")
        return 0
    first = steps[0]["step_id"]
    target = ns.step or first

    return _point_and_build(ai_work, aip_path, meta, ws, target)


def cmd_resume(ns) -> int:
    ai_work = find_ai_work_root(Path.cwd()) / ".ai-work"
    aip_path, meta = _resolve_aip(ns.aip, ai_work)
    if not _lint_gate(aip_path):
        return 2
    ws = _resolve_workspace(ai_work, meta, ns.task_id)
    if not ws.exists():
        print(
            f"error: workspace not found: {ws}\n"
            f"  run 'run_aip.py start {ns.aip}' first",
            file=sys.stderr,
        )
        return 2

    pointer = _read_pointer(ws)
    if pointer is None and not ns.step:
        print(
            "error: no current_step pointer and --step not provided",
            file=sys.stderr,
        )
        return 2

    target = ns.step or pointer.get("step_id", "STEP-01")
    return _point_and_build(ai_work, aip_path, meta, ws, target)


def cmd_step(ns) -> int:
    return cmd_resume(ns)  # step is resume with forced --step


def cmd_status(ns) -> int:
    ai_work = find_ai_work_root(Path.cwd()) / ".ai-work"
    aip_path, meta = _resolve_aip(ns.aip, ai_work)
    ws = _resolve_workspace(ai_work, meta, ns.task_id)
    task_id = ws.name

    print(f"AIP:       {meta.get('artifact_id', '?')}  ({aip_path})")
    print(f"Task ID:   {task_id}")
    print(f"Workspace: {ws} {'(exists)' if ws.exists() else '(missing)'}")

    steps = _steps(aip_path)
    print(f"Steps:     {len(steps)}")

    if not ws.exists():
        print("Status:    not started — run 'run_aip.py start <aip>'")
        return 0
    pointer = _read_pointer(ws)
    if pointer:
        print(f"Pointer:   {pointer.get('step_id')} ({pointer.get('status')})  "
              f"updated {pointer.get('updated_at')}")
    else:
        print("Pointer:   (none) — run 'run_aip.py resume <aip> --step STEP-01'")

    for f in ("00c_active_step_context.md", "04_findings.md",
              "07_output_draft.md", "11_output_final.md"):
        p = ws / f
        state = "✔" if p.exists() and p.stat().st_size > 0 else "·"
        print(f"  [{state}] {f}")
    # CR-015 F4: surface the capture-triage rollup (the playbook L16 promise, now real).
    inbox = ws / "08_capture_inbox.jsonl"
    if inbox.exists():
        try:
            rows = read_jsonl(inbox)
            captured = sum(1 for r in rows if r.get("status") == "captured")
            print(f"Captures:  {len(rows)} total, {captured} need triage (status=captured)")
            # CR-AIWS-2026-07-008 C4: kind breakdown + relation-candidate visibility.
            kinds: dict = {}
            for r in rows:
                k = r.get("candidate_kind") or "(no kind)"
                kinds[k] = kinds.get(k, 0) + 1
            if kinds:
                top = ", ".join(f"{k}={n}" for k, n in
                                sorted(kinds.items(), key=lambda kv: (-kv[1], kv[0])))
                print(f"           by kind: {top}")
            rel_pending = sum(1 for r in rows
                              if r.get("candidate_kind") == "artifact_relation_update"
                              and r.get("status") == "captured")
            if rel_pending:
                print(f"           relation candidates pending Relations Enrichment CR: {rel_pending}")
        except Exception:
            print("Captures:  (inbox unreadable)")
    # CR-AIWS-2026-08-054 (DP-1025-A) — Runtime Queue rollup, MIRROR of the capture block above.
    # The block shipped pre-753777a, was removed there WITHOUT a CR, while ~8 docs kept teaching it;
    # re-implemented against the CURRENT queue schema (02_runtime_queue.jsonl; `blocking` field per
    # lint_workspace NEW_QUEUE_HINT_FIELDS). An empty/missing queue prints an explicit line so
    # "nothing queued" is distinguishable from "rollup not running".
    queue = ws / "02_runtime_queue.jsonl"
    if not queue.exists():
        queue_legacy = ws / "02_investigation_queue.jsonl"
        queue = queue_legacy if queue_legacy.exists() else queue
    if queue.exists():
        try:
            qrows = read_jsonl(queue)
            open_st = {"pending", "queued", "in_progress", "open", "blocked"}
            n_open = sum(1 for r in qrows if str(r.get("status", "open")).lower() in open_st)
            n_blocking = 0
            for r in qrows:
                b = r.get("blocking")
                if isinstance(b, str):
                    b = b.lower() in {"true", "yes", "1"}
                if b and str(r.get("status", "open")).lower() in open_st:
                    n_blocking += 1
            print(f"Queue:     {len(qrows)} item(s), {n_open} open, {n_blocking} blocking"
                  + ("   [legacy filename]" if queue.name == "02_investigation_queue.jsonl" else ""))
            if n_open:
                types: dict = {}
                for r in qrows:
                    if str(r.get("status", "open")).lower() in open_st:
                        t = r.get("type") or r.get("kind") or "(no type)"
                        types[t] = types.get(t, 0) + 1
                top = ", ".join(f"{k}={n}" for k, n in
                                sorted(types.items(), key=lambda kv: (-kv[1], kv[0])))
                print(f"           open by type: {top}")
        except Exception:
            print("Queue:     (queue unreadable)")
    else:
        print("Queue:     (queue trống — chưa có 02_runtime_queue.jsonl)")
    # CR-AIWS-2026-08-125 C2 / DP-E — the Capture Backlog rollup. Deferring is only honest if the debt
    # stays visible afterwards; a backlog nobody is shown is the same "later" that never came.
    try:
        backlog = _triage().read_backlog(ai_work)
    except Exception:
        backlog = []
    if backlog:
        open_rows = [r for r in backlog if r.get("status") == "open"]
        line = f"Backlog:   {len(backlog)} row(s), {len(open_rows)} open"
        if len(open_rows) > CAPTURE_BACKLOG_BUDGET:
            line += f"   [over budget of {CAPTURE_BACKLOG_BUDGET} — triage a few before deferring more]"
        print(line)
        cutoff = (datetime.now() - timedelta(days=CAPTURE_BACKLOG_STALE_DAYS)).date().isoformat()
        stale = [r for r in open_rows if str(r.get("deferred_at", "")) and
                 str(r.get("deferred_at", "")) < cutoff]
        if stale:
            print(f"           {len(stale)} open >{CAPTURE_BACKLOG_STALE_DAYS}d: "
                  + ", ".join(str(r.get("backlog_id", "?")) for r in stale[:5])
                  + (" …" if len(stale) > 5 else ""))
    return 0


def cmd_list(ns) -> int:
    ai_work = find_ai_work_root(Path.cwd()) / ".ai-work"
    aip_path, meta = _resolve_aip(ns.aip, ai_work)
    print(f"{meta.get('artifact_id', '?')} — {meta.get('title', '')}")
    for s in _steps(aip_path):
        print(f"  {s['step_id']}  {s.get('title', '')}")
    return 0


def _extract_step_number(step_id: str) -> int:
    """Extract numeric step number from step_id like 'STEP-02' -> 2."""
    m = re.match(r'STEP-(\d+)', step_id)
    return int(m.group(1)) if m else 0


_LOCATOR_BACKTICK_RE = re.compile(r"`([^`]+)`")
_LOCATOR_TOKEN_RE = re.compile(r"(?<![\w`])((?:[\w.-]+/)*[\w.-]+\.(?:md|jsonl|py|yml|yaml|json)(?:#[\w-]+)?)")


def _locator_from_bullets(expected_outputs: str) -> "str | None":
    """First resolvable path in an Expected Outputs field (CR-AIWS-2026-08-127 C6).

    Per bullet (skipping `#` comment lines): prefer the first backtick span that looks like a path,
    else the first bare token with a `/` or a known extension. Returns None when no bullet carries a
    path — the caller falls back to `04_findings.md#STEP-NN`, exactly as before.
    """
    for line in (expected_outputs or "").splitlines():
        line = line.strip().lstrip("-*• ").strip()
        if not line or line.startswith("#"):
            continue
        for span in _LOCATOR_BACKTICK_RE.findall(line):
            span = span.strip()
            if "/" in span or _LOCATOR_TOKEN_RE.fullmatch(span):
                return span
        m = _LOCATOR_TOKEN_RE.search(line)
        if m:
            return m.group(1)
    return None


def _write_handoff_stub(ws: Path, aip_path: Path, meta: dict) -> None:
    """Create handoff stub for the PREVIOUS step when advancing.

    Idempotent: only writes if meta file doesn't exist. Called in _point_and_build
    after pointer is set but before ASC is built (Wave 2 Item 1).
    """
    pointer_file = ws / ".current_step.json"
    if not pointer_file.exists():
        return

    try:
        pointer = json.loads(pointer_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        return

    current_step_id = pointer.get("step_id", "")
    current_step_num = _extract_step_number(current_step_id)

    if current_step_num <= 1:
        return

    prev_step_num = current_step_num - 1
    prev_step_id = f"STEP-{prev_step_num:02d}"

    step_outputs_dir = ws / "step_outputs"
    step_outputs_dir.mkdir(parents=True, exist_ok=True)

    meta_file = step_outputs_dir / f"STEP-{prev_step_num:02d}.meta.yml"
    if meta_file.exists():
        return

    try:
        body = read_text(aip_path).split("---\n", 2)[-1]  # Extract body after frontmatter
        steps = parse_aip_steps(body)
    except Exception:
        return

    prev_step = next((s for s in steps if s.get("step_id") == prev_step_id), None)
    if not prev_step:
        return

    expected_outputs = prev_step.get("Expected Outputs", "").strip()

    # CR-AIWS-2026-08-127 C6: the locator is a PATH parsed out of the first Expected Outputs bullet, not the
    # bullet itself. The old code stored the whole line ("- `04_findings.md` — bảng baseline …"), which no
    # downstream reader could resolve (AIP-1120: 3 stubs, all hand-fixed).
    output_locator = _locator_from_bullets(expected_outputs) or f"04_findings.md#STEP-{prev_step_num:02d}"

    aip_id = meta.get("artifact_id", "")
    aip_num_match = re.search(r'-(\d+)$', aip_id)
    aip_num = aip_num_match.group(1) if aip_num_match else "0000"

    output_id = f"OUT-{aip_num}-{prev_step_num:02d}-01"
    created_at = datetime.now().replace(microsecond=0).isoformat()

    # CR-127 C6: the stub must satisfy lint_workspace on the day it is written. The required-field list is
    # READ from the lint (one source), and asserted here so a future lint change cannot silently re-open the gap.
    from lint_workspace import STEP_OUTPUT_META_REQUIRED  # noqa: E402 — local import: lint is not a runtime dep elsewhere
    meta_fields = [
        ("output_id", output_id),
        ("result_type", "output"),
        ("working_aip_ref", aip_id or "AIP-EXEC-0000"),
        ("step_id", prev_step_id),
        ("output_locator", output_locator),
        ("created_at", created_at),
        ("review_status", "draft"),
    ]
    missing = [k for k in STEP_OUTPUT_META_REQUIRED if k not in dict(meta_fields)]
    assert not missing, f"handoff stub would miss lint-required fields: {missing}"
    # `verification_level: unverified` — lint_workspace reads `source_refs: []` as "present" and then demands a
    # verification_level; a fresh stub has verified nothing, and saying so is truer than omitting the key.
    meta_yaml = ("".join(f"{k}: {v}\n" for k, v in meta_fields)
                 + "verification_level: unverified\n" + "source_refs: []\n" + 'notes: ""\n')
    write_text(meta_file, meta_yaml)

    index_file = step_outputs_dir / "index.jsonl"
    index_row = {
        "output_id": output_id,           # CR-127 C6: the key lint_workspace indexes on
        "source_id": output_id,           # kept for readers written against the Wave 2 shape
        "source_type": "step_output",
        "step_id": prev_step_id,
        "status": "draft",
        "target_path": output_locator,
        "created_at": created_at,
    }

    index_rows = []
    if index_file.exists():
        try:
            index_rows = read_jsonl(index_file)
        except Exception:
            pass

    index_rows.append(index_row)

    with index_file.open("w", encoding="utf-8", newline="\n") as f:
        for row in index_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"✓ Handoff stub written: {output_id}")
    print(f"  → {meta_file.relative_to(ws)}")


def _point_and_build(ai_work: Path, aip_path: Path, meta: dict,
                     ws: Path, step_id: str) -> int:
    set_cmd = [
        sys.executable, str(TOOL / "set_current_step.py"),
        "--workspace", str(ws),
        "--aip", meta.get("artifact_id", ""),
        "--aip-path", str(aip_path),
        "--step-id", step_id,
    ]
    rc = _run(set_cmd)
    if rc != 0:
        return rc

    _write_handoff_stub(ws, aip_path, meta)

    build_cmd = [
        sys.executable, str(TOOL / "build_active_step_context.py"),
        "--workspace", str(ws),
    ]
    rc = _run(build_cmd)
    if rc != 0:
        return rc
    print()
    print("READY:")
    print(f"  workspace: {ws}")
    print(f"  step:      {step_id}")
    print(f"  active step context: {ws / '00c_active_step_context.md'}")
    print(f"Next: open 00c_active_step_context.md and work the step.")
    print("Wiki candidate check: append candidates to 08_capture_inbox.jsonl IMMEDIATELY on discovery — do not batch to end of step or AIP.")
    print("Do not promote candidates into Wiki / Knowledge Hub without HUMAN review.")
    return 0


def _flip_status_done(aip_path: Path) -> bool:
    """`status: active` -> `status: done` at `close` (CR-AIWS-2026-08-125 C2).

    The FOURTH sanctioned write into an AIP file, and deliberately the same surgical line-level edit as
    `_flip_status_active`: never reformats the rest of the frontmatter, never touches the body. A status
    that is not `active` is left alone and reported, so `close` on an already-closed AIP is a no-op
    rather than a rewrite.
    """
    text = read_text(aip_path)
    m = re.match(r"^(---\s*\n)(.*?\n)(---\s*\n)(.*)$", text, re.DOTALL)
    if not m:
        return False
    head, fm, fence, body = m.group(1), m.group(2), m.group(3), m.group(4)
    out: list[str] = []
    changed = False
    for l in fm.splitlines(keepends=True):
        if l.startswith("status:") and l.split(":", 1)[1].strip() == "active":
            eol = "\r\n" if l.endswith("\r\n") else "\n"
            out.append(f"status: done{eol}")
            changed = True
        else:
            out.append(l)
    if changed:
        write_text(aip_path, head + "".join(out) + fence + body)
    return changed


def _final_output_is_template(ws: Path) -> bool:
    """True when `11_output_final.md` is still byte-identical to the shipped template, or empty.

    This is the check `final_missing` cannot make: the template is PRE-FILLED, so an untouched final
    output is a non-empty file and the existing predicate reads it as present. Measured: 228 of 372
    workspaces hold the template verbatim, which is why this is a close-time refusal and not a lint rule.
    """
    final = ws / "11_output_final.md"
    if not final.exists():
        return True
    try:
        body = final.read_text(encoding="utf-8")
    except Exception:
        return False
    if not body.strip():
        return True
    try:
        ai_work = find_ai_work_root(ws) / ".ai-work"
    except SystemExit:
        return False
    for tpl in (ai_work / "workspace_templates" / "task_workspace_template" / "11_output_final.md",):
        if tpl.exists():
            try:
                if tpl.read_text(encoding="utf-8").strip() == body.strip():
                    return True
            except Exception:
                pass
    return False


def _write_back_link(ws: Path, aip_path: Path, aip_id: str, ai_work: Path) -> bool:
    """Write `.current_step.json` when it is missing (CR-AIWS-2026-08-125 C4).

    Measured: 13 workspaces had no back-link and held 18 open captures between them. C4's fallback lets
    the linter SEE them; this closes the gap going forward instead of relying on the fallback forever.
    """
    ptr = ws / ".current_step.json"
    if ptr.exists():
        return False
    payload = {
        "aip_id": aip_id,
        "aip_path": portable_locator(aip_path, ai_work.parent),
        "step_id": "",
        "status": "done",
        "updated_at": today(),
    }
    line = json.dumps(payload, ensure_ascii=False, indent=1)
    json.loads(line)
    with io.open(ptr, "w", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")
    return True


def cmd_close(ns) -> int:
    """Close an AIP: sweep the Capture Inbox, disposition every open row, then flip to `done`."""
    ai_work = find_ai_work_root(Path.cwd()) / ".ai-work"
    aip_path, meta = _resolve_aip(ns.aip, ai_work)
    aip_id = str(meta.get("artifact_id", "") or "")
    ws = _resolve_workspace(ai_work, meta, ns.task_id)
    status = str(meta.get("status", "") or "").strip().lower()

    print(f"AIP:       {aip_id}  ({aip_path})")
    print(f"Workspace: {ws} {'(exists)' if ws.exists() else '(missing)'}")
    print(f"Status:    {status}")
    if status == "done":
        print("Already closed — nothing to do.")
        return 0
    if not ws.exists():
        print("error: no workspace — nothing to sweep; close by hand if this AIP never ran.",
              file=sys.stderr)
        return 2

    # ---- Final Capture Sweep (operations/run.md) -------------------------------------------------
    print("\nFinal Capture Sweep — anything noticed this session that is reusable and non-obvious")
    print("belongs in the inbox BEFORE it is dispositioned, not after.\n")
    open_rows = _triage().sweep(ws)

    if open_rows and not (ns.defer_all or ns.dispositions):
        # THE non-interactive contract: print and refuse. Never a silent defer-all.
        print(f"{len(open_rows)} capture(s) still `captured` — close is refused until each is "
              f"dispositioned:\n")
        for r in open_rows:
            print(f"  {str(r.get('id','?')):16s} {str(r.get('candidate_kind','')):24s} "
                  f"{str(r.get('title',''))[:64]}")
        print("\nThere is no stdin here, so nothing will be assumed on your behalf. Choose one:")
        print("  py .ai-work/tooling/triage_capture.py defer --workspace <ws> --cap <ID> "
              "--reason \"…\"        # one row")
        print(f"  py .ai-work/tooling/run_aip.py close {ns.aip} --defer-all --reason \"…\""
              f"                   # all of them, same reason")
        print("  … or triage them in place (promote / discard / retain_local) and re-run close.")
        return 1

    if open_rows and ns.defer_all:
        reason = (ns.reason or "").strip()
        if not reason:
            print("error: --defer-all requires --reason. A deferral with no reason is exactly what "
                  "the Capture Backlog exists to replace.", file=sys.stderr)
            return 2
        for r in open_rows:
            bl, wrote = _triage().defer(ws, str(r.get("id", "")), reason, ai_work=ai_work)
            print(f"  deferred {r.get('id')} -> {bl}" + ("" if wrote else "  (already)"))

    still = _triage().sweep(ws)
    if still:
        print(f"error: {len(still)} capture(s) still `captured` after dispositions — not closing.",
              file=sys.stderr)
        return 1

    # ---- C6: the final output must not still be the shipped template ----------------------------
    if _final_output_is_template(ws) and not ns.force_final:
        print("error: 11_output_final.md is still the shipped template (or empty). A closed AIP with "
              "no final output is the failure this check exists for.\n"
              "       Write it, or pass --force-final if this AIP genuinely has no output.",
              file=sys.stderr)
        return 1

    if _write_back_link(ws, aip_path, aip_id, ai_work):
        print("  wrote missing .current_step.json back-link (C4)")

    if _flip_status_done(aip_path):
        print("status: active -> done (CR-AIWS-2026-08-125)")
    else:
        print(f"warn: frontmatter status was {status!r}, not 'active' — left unchanged",
              file=sys.stderr)
    return 0

def main() -> int:
    p = argparse.ArgumentParser(description="Orchestrate AIP execution")
    sub = p.add_subparsers(dest="cmd", required=True)

    def _add_common(sp):
        sp.add_argument("aip", help="AIP id (e.g. AIP-EXEC-001) or file path")
        sp.add_argument("--task-id", help="Override task id (default: derived)")

    sp_start = sub.add_parser("start", help="Create workspace + start AIP")
    _add_common(sp_start)
    sp_start.add_argument("--title", help="Task title (goal)")
    sp_start.add_argument("--step", help="Start at step (default: first)")
    sp_start.add_argument("--force", action="store_true",
                          help="Overwrite existing workspace")
    sp_start.set_defaults(func=cmd_start)

    sp_resume = sub.add_parser("resume", help="Resume existing workspace")
    _add_common(sp_resume)
    sp_resume.add_argument("--step", help="Jump to step (default: pointer)")
    sp_resume.set_defaults(func=cmd_resume)

    sp_step = sub.add_parser("step", help="Jump to a specific step")
    _add_common(sp_step)
    sp_step.add_argument("--step", required=True, help="Target step id")
    sp_step.set_defaults(func=cmd_step)

    sp_status = sub.add_parser("status", help="Show workspace + pointer status")
    _add_common(sp_status)
    sp_status.set_defaults(func=cmd_status)

    # CR-AIWS-2026-08-125 C2 — `close` is symmetric with `start`: start flips draft->active, close
    # flips active->done, and each owns the ceremony that belongs at its end of the AIP.
    sp_close = sub.add_parser("close", help="Sweep captures, then flip the AIP active -> done")
    sp_close.add_argument("aip")
    sp_close.add_argument("--task-id", default="")
    sp_close.add_argument("--defer-all", action="store_true", default=False,
                          help="defer every still-captured row (requires --reason)")
    sp_close.add_argument("--reason", default="", help="why they are being deferred")
    sp_close.add_argument("--dispositions", default="",
                          help="path to a per-row disposition file (reserved)")
    sp_close.add_argument("--force-final", action="store_true", default=False,
                          help="close even though 11_output_final.md is still the template")
    sp_close.set_defaults(func=cmd_close)

    sp_list = sub.add_parser("list", help="List steps in the AIP")
    _add_common(sp_list)
    sp_list.set_defaults(func=cmd_list)

    ns = p.parse_args()
    return ns.func(ns)


if __name__ == "__main__":
    raise SystemExit(main())
