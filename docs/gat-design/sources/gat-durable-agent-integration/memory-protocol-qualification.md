# Recoverable memory protocol qualification

## 1. Binding, scope, and protocol choice

This corrected conclusion is bound to WBS revision 2 at plan SHA-256 `ddabe11b55fe9a012f25bdffb3109952d1a8b057da158a14ebea9631a6467457`, task `memory_protocol_qualification`, contract SHA-256 `885c6eec52c77fddea722bd0850112104afebbc739d8369c5ef07046a47c1195`, and final attempt `memory_protocol_qualification-a02`. Attempt a01 remains archived evidence and is not rewritten.

**Chosen protocol: immutable generations with one immutable bootstrap anchor and one atomically replaced current-generation pointer.** A journal protocol is not used. The bootstrap anchor is published exactly once to distinguish forever between “legacy is still eligible” and “generation authority has been established”; subsequent confirmed mutations publish only by current-pointer replacement. This is preferable to an in-place journal because recovery never infers replay/rollback intent from a partially applied item/index pair, and absence of an established pointer can never silently reauthorize legacy bytes.

The protocol is private provider persistence. None of the names or paths below become public API, appear in task-context values, or change `DurableAgentService`, `DurableAgentRef`, error codes, or the GAT boundary.

## 2. Private vocabulary and layout

Terms:

- **member storage identity** — the canonical private storage owner, effective scope, and member name. This, not caller workspace text or reference token, keys serialization.
- **candidate** — bounded review material with permanent semantic status `unconfirmed`; it is never reachable from the confirmed-generation pointer.
- **content object** — immutable UTF-8 item bytes named by SHA-256 digest.
- **generation manifest** — immutable complete catalog for one confirmed state. It contains schema version, generation id, parent id or `null`, monotonic persistent sequence, and every item's id, title, retrieval condition, object digest, and UTF-8 byte count.
- **bootstrap anchor** — immutable bounded JSON containing schema version, a storage-identity digest, the bootstrap generation id, and its manifest digest. Its exclusive atomic publication permanently disables legacy authority and anchors the only generation recoverable when the first current pointer has not yet become durable.
- **current pointer** — bounded JSON containing schema version, generation id, sequence, and manifest digest. After bootstrap, its atomic replacement is the confirmed-mutation publication boundary.
- **mutation lease** — private `mutation.lock` acquired with exclusive creation for every bootstrap, commit, and retained pre-bootstrap write. It supplements the process-local FIFO queue and makes participating cross-process overlap fail closed.
- **staging transaction** — attempt-local temporary files for one bootstrap or commit. It has no confirmed authority.
- **legacy flat store** — the existing `memory/index.json` plus item files and the already-supported `MEMORY.md` migration input.
- **journal** — deliberately absent. No journal file is created, replayed, or treated as authority; a stray journal-like file is non-authoritative.

Conceptual private layout (exact names may remain module-private constants):

```text
<member-private-root>/memory/
  generation-mode.json          # immutable bootstrap anchor
  current.json
  mutation.lock                 # participating-writer lease, never authority
  objects/<sha256>.md
  generations/<generation-id>.json
  staging/<transaction-id>/...
  candidates/<candidate-id>.json
  index.json                    # legacy compatibility input, retained
  <legacy-item>.md              # legacy compatibility input, retained
```

Creation modes remain restrictive: private directories `0700`, regular files `0600`. Every component is checked with `lstat`; symlinks, non-regular files, unknown schema versions, traversal names, NUL, invalid UTF-8, and oversized values fail closed. Public diagnostics remain path-free.

## 3. Invariants

1. Authority mode is explicit and monotonic. Only when both `generation-mode.json` and `current.json` are absent may the exact validated legacy store be a bootstrap source. Atomic publication and directory sync of the immutable bootstrap anchor permanently disables legacy authority. With an anchor present, missing/corrupt current state is recovered only by the exact anchor rule below or fails closed; legacy bytes are never reauthorized. Directory enumeration, timestamps, lexicographic ids, staging data, candidates, and caller labels never select authority.
2. A valid current pointer names exactly one immutable generation manifest whose digest matches the pointer; every manifest item names one present regular bounded object whose filesystem byte count matches the manifest. The body digest and strict UTF-8/NUL rules are verified when that item is selectively read, never eagerly while constructing a task-context catalog.
3. A generation manifest is complete. There is no authoritative state in which an index entry names missing content.
4. Bootstrap objects/manifests are non-authoritative until the immutable anchor names generation zero; later objects/manifests are non-authoritative until the current pointer names them. Unreferenced staged objects or generations never become confirmed by recovery.
5. Candidate content, candidate metadata, confidence, provenance, strings such as “approved,” and an optional candidate id grant no authority.
6. Only a structurally valid `DurableAgentApprovedMemoryInput` with `authorization.kind` equal to `human` or `authorized-host-workflow` and a bounded, nonempty, NUL-free `authorizationRef` may enter confirmed publication.
7. If `candidateId` is present, the corresponding intact unconfirmed candidate must exist and its title, retrieval condition, and content must exactly match those fields in the approved item; the item id is assigned by the approval because candidate input has no id. An edited approval omits `candidateId` and authorizes the complete explicit `item` instead. In neither case is authority inferred from candidate data.
8. Bootstrap, approved commits, candidate writes, and retained pre-bootstrap writes serialize by member storage identity through the same process-local FIFO queue and participating-writer lease. Different identities have independent queues. Every public read call independently captures one complete authority selection and observes either the complete old generation or complete new generation.
9. Release first closes admission, then waits for all admitted reads, candidate submissions, and commits. It never deletes persistent profile, candidate, confirmed generation, object, legacy input, or working data.
10. Recovery never deletes or rewrites valid persistent user data. Automatic cleanup is limited to the current process's known temporary staging entries after their bytes exist durably in published objects/manifests; old generations, objects, candidates, and legacy data are retained.

## 4. Input validation and authorization boundary

Private implementation ceilings are exact: item/candidate body `1 MiB`; each title and retrieval condition `16 KiB`; provenance `64 KiB`; authorization reference `16 KiB`; at most `64` limitations of at most `16 KiB` each; complete serialized candidate record `2 MiB`; complete generation manifest `256 KiB`; bootstrap anchor and current pointer `8 KiB` each; and at most `1024` confirmed items. Aggregate ceilings apply in addition to field ceilings. All sizes are UTF-8 byte counts, not JavaScript character counts. Decoding is strict/fatal; replacement characters are not accepted as proof of valid UTF-8.

### 4.1 Candidate submission

`submitMemoryCandidate(ref, input)` performs reference admission first, then validates a closed input shape. Title, retrieval condition, content, provenance, confidence, and every limitation are bounded UTF-8 strings with NUL rejection; aggregate serialized candidate size is bounded before storage creation. Invalid shape or bounds return `REJECTED_CANDIDATE`.

A successful submission atomically publishes one candidate record and returns only the public candidate value with `status: 'unconfirmed'`. Candidate persistence never touches objects, generations, legacy index, or `current.json`. Approval-like words and extra runtime fields cannot change the returned status.

### 4.2 Approved commit

`commitMemoryItem(ref, approvedInput)` performs, in order:

1. reference admission and release-state check;
2. closed-shape validation of approved input, item, and authorization;
3. bounded UTF-8/NUL validation of item id, metadata, content, and authorization reference;
4. authorization-kind validation against the two public enum values;
5. optional candidate lookup and exact proposed-item equality check;
6. per-member mutation-lock acquisition;
7. recovery/current-generation validation;
8. generation publication described below.

Steps 2–5 reject with `REJECTED_CANDIDATE`; no durable confirmed-memory effect occurs. A foreign, forged, stale, mismatched, or released reference still fails first with `UNAUTHORIZED_REFERENCE`. Storage corruption discovered in steps 7–8 is `INVALID_CONTEXT_DATA`; unexpected filesystem failure is mapped to `PROVIDER_UNAVAILABLE`. The existing error vocabulary is sufficient.

## 5. State machines and exact publication order

### 5.1 Candidate state machine

```text
C0 absent
  -- validate bounded unconfirmed input --> C1 candidate-temp-written
  -- fsync candidate temp -------------> C2 candidate-temp-durable
  -- atomic rename --------------------> C3 unconfirmed-candidate-visible
  -- fsync candidates directory -------> C4 unconfirmed-candidate-durable
```

No candidate state transitions to confirmed. A commit creates a separate generation using authorization-bearing input.

### 5.2 Bootstrap discriminator state machine

```text
B0 no anchor, no current: validated legacy is eligible bootstrap input
  -> BO1 each bootstrap object temp written
  -> BO2 each bootstrap object temp synced
  -> BO3 each immutable object renamed and objects directory synced
  -> BM1 complete generation-zero manifest temp written
  -> BM2 generation-zero manifest temp synced
  -> B1 generation-zero manifest renamed and generations directory synced,
        still non-authoritative
  -> B2 bootstrap-anchor temp written and synced
  -> B3 bootstrap anchor atomically renamed and memory directory synced
        [LEGACY PERMANENTLY DISABLED; EXACT ANCHORED GENERATION AUTHORITATIVE]
  -> B4 current-pointer temp for the anchored generation written and synced
  -> B5 current pointer atomically renamed and memory directory synced
```

The anchor is created with exclusive publication and never overwritten. It names only generation zero. A failure before B3 leaves legacy authoritative and a retry may reuse or ignore unreferenced bootstrap artifacts. A failure after B3 can never return to legacy: if `current.json` is absent and no non-bootstrap generation exists, recovery validates the exact anchored manifest/objects and recreates the pointer to that generation; if any later generation exists or the anchor target is invalid, recovery fails `INVALID_CONTEXT_DATA` without choosing legacy or directory order.

### 5.3 Confirmed generation state machine

```text
G0 exact anchored/current generation
  -> G1 admitted, validated, serialized, recovered
  -> G2 content object temp written and synced
  -> G3 immutable object published and objects directory synced
  -> G4 complete generation-manifest temp written and synced
  -> G5 immutable generation manifest published and generations directory synced
  -> G6 current-pointer temp written and synced
  -> G7 current pointer atomically replaced       [SOLE LATER-COMMIT AUTHORITY BOUNDARY]
  -> G8 memory directory synced; response may be returned
  -> G9 attempt-owned staging cleanup (non-authoritative)
```

State projection by required persistence subject:

| Subject | Non-authoritative states | Authoritative state |
|---|---|---|
| item/body | absent → staging temp → synced temp → immutable object | only when selected by the bootstrap anchor during B3–B5 or by the current generation afterward |
| index/catalog | in-memory complete catalog → manifest temp → synced temp → immutable generation manifest | only when named by the bootstrap anchor during B3–B5 or by `current.json` afterward |
| staging | transaction open → partial → complete → cleanup residue | never authoritative |
| generation | immutable complete manifest, possibly unreferenced/stale | generation zero through the durable anchor during B3–B5; otherwise only through the exact current pointer |
| journal | absent; stray journal-like bytes ignored | no authoritative journal state exists |

Exact effect order for a commit:

1. Read and validate the selected old generation. If its selected item already has exactly the approved id, metadata, object digest, and byte count, treat the operation as an idempotent no-op after authorization validation and return that confirmed item without advancing the persistent sequence. Otherwise build the next complete manifest in memory by replacing or adding exactly one item while preserving every other item entry. The manifest records a private commit-key digest over the authorization kind/reference, optional candidate id, and complete approved item so a retry after an ambiguous response can recognize the already-published operation without trusting caller prose.
2. Compute the approved content's SHA-256 and UTF-8 byte count. Create a transaction staging directory without following symlinks.
3. Write the content object temporary file with exclusive creation, sync it, close it, then atomically rename it to `objects/<digest>.md`. If that object already exists, validate its type, bound, byte count, and digest instead of rewriting it. Sync the objects directory.
4. Write the complete next manifest temporary file, sync it, close it, then atomically rename it to `generations/<new-generation>.json`. Sync the generations directory. The manifest is still non-authoritative.
5. Write and sync a temporary current pointer containing the new generation id, sequence, and manifest digest.
6. Atomically rename that temporary pointer over `current.json`. **Only this step publishes a later approved-memory generation; bootstrap authority was established separately at B3.**
7. Sync the memory directory. Re-read the current pointer and selected manifest/object through the production reader before constructing the committed result.
8. Advance process-local content revisions from actual model-visible metadata/body. Return `status: 'confirmed'` and the revision derived from the published item.
9. Best-effort cleanup may remove only the transaction's own temporary staging directory after all corresponding content is durably reachable. Cleanup failure cannot roll back or change authority.

There is no journal transition. An unexpected `journal`, `journal.json`, or replay marker is ignored as non-authoritative input and must not alter selection.

### 5.4 Snapshot and selective read

Consistency is **per public call**, not affinity across calls. Each admitted `openTaskContext` captures the current authority once, validates that selected complete manifest, and derives one internally consistent metadata-only catalog. Each later `readMemoryItem` independently captures authority again, then verifies the selected object's digest and byte count before returning content. A commit between those calls may therefore make the later selective read observe a newer generation; the API does not bind it to the earlier snapshot. Within either call, a racing commit yields one complete old or new generation and never a mixed manifest/object view.

Process-local revisions remain monotonic within the opaque reference generation. Snapshot revision covers the complete model-visible snapshot; item revision covers id, title, retrieval condition, and body. The first read before a snapshot is positive, unchanged rereads are stable, a successful commit changes relevant revisions, and reprovision/restart is distinguished by the opaque provenance generation.

## 6. Deterministic recovery selection

Mutation recovery is run under the shared storage-identity queue and exclusive mutation lease before bootstrap or commit; reads use the same strict authority selector without mutating storage.

1. **No anchor and no current pointer:** only this state permits legacy bootstrap. Validate the entire legacy index and every referenced body, publish immutable objects and generation zero, then execute B2–B5. Stray staging, objects, or generations remain non-authoritative; they never prove that generation mode was established.
2. **No anchor and no legacy data:** create an empty generation zero and execute B2–B5.
3. **No anchor with incomplete/corrupt legacy:** fail `INVALID_CONTEXT_DATA`; publish no anchor and delete nothing.
4. **No anchor but a current pointer exists:** fail `INVALID_CONTEXT_DATA`. A current pointer without the durable discriminator is not accepted and legacy is not merged with it.
5. **Valid anchor and valid current pointer:** select exactly the current pointer's generation after validating the anchor identity, pointer/manifest integrity, parent/sequence chain, and every referenced object's existence, regular-file type, symlink rejection, and declared byte count. Never scan for a “newer” generation.
6. **Valid anchor, current absent, and no generation manifest except the exact anchored generation zero:** validate the anchor target and recreate `current.json` for generation zero through a synced temporary plus atomic rename. Legacy is not read for authority. This is the only automatic missing-pointer repair.
7. **Valid anchor, current absent, with any non-bootstrap generation manifest present:** fail `INVALID_CONTEXT_DATA`. This state may represent loss of an established later head or an interrupted later commit; choosing generation zero, a later manifest, or legacy would guess and is forbidden.
8. **Valid anchor with malformed/corrupt current pointer:** fail `INVALID_CONTEXT_DATA`; do not fall back to the anchor or legacy because an established pointer is observable but untrustworthy.
9. **Missing/malformed/oversized/NUL/digest-mismatched/wrong-sequence/wrong-parent selected manifest, or missing/symlink/non-regular/stat-size-mismatched object:** `openTaskContext` fails `INVALID_CONTEXT_DATA`. Invalid UTF-8, NUL, or body-digest mismatch fails the selective `readMemoryItem` call. No fallback, rewrite, or deletion occurs.
10. **Temporary anchor or current files:** a temp anchor with no durable anchor is ignored and legacy remains eligible; a temp current with a valid anchor is ignored and rules 5–8 apply to the durable current path.
11. **Unreferenced later generation/object with a valid current:** retain but ignore it. It is stale/uncommitted even when its sequence is higher.
12. **Incomplete/corrupt staging or stray journal:** retain/ignore it; neither can select authority.
13. **Corrupt candidate:** confirmed reads remain unchanged. A commit naming it fails `REJECTED_CANDIDATE`; a commit without that candidate id is independent.

Exact power-loss outcomes during first bootstrap are monotonic:

- before anchor rename: only legacy is authoritative; generation artifacts are ignored and bootstrap may retry;
- after anchor rename but before its directory sync: reboot may expose either no anchor (legacy remains authoritative) or the complete anchor (anchored generation zero is authoritative); both name the same validated legacy snapshot and never combine states;
- after anchor directory sync but before current rename: generation zero is authoritative through the anchor and recovery recreates only its pointer;
- after current rename but before directory sync: reboot may expose anchor-only or anchor-plus-current; both select the same generation zero;
- after current directory sync: the current pointer selects generation zero normally.

For later commits, atomic pointer replacement still permits only the previous or new complete pointer after power loss. If the durable current pointer is absent after any later generation was created, rule 7 fails closed and never reauthorizes legacy.

## 7. Concurrency and lifecycle

- Maintain one FIFO promise/mutex queue per private member storage identity in a process-wide `globalThis[Symbol.for('@deepseek-ai/dsh-durable-agent.memory-lock.v1')]` registry. Local-provider instances and retained compatibility calls in the same JavaScript isolate use the same key and queue; different identities use different queues.
- Global members provisioned from different workspaces but sharing one canonical global storage identity use the same queue.
- After reaching the queue front, every bootstrap, approved commit, candidate persistence, and retained pre-bootstrap write acquires the same private `mutation.lock` with exclusive creation. `EEXIST` returns `CONCURRENT_MUTATION`; a stale/ambiguous lease is never auto-deleted. This contract guarantees ordering within one process and fail-closed overlap for participating processes. Writers from older/foreign processes that ignore the lease are unsupported; detected anchor/current/legacy drift returns `INVALID_CONTEXT_DATA` and is never merged or silently repaired.
- A retained compatibility writer must enter that same queue/lease, validate its bounded input, then **re-read both `generation-mode.json` and `current.json` immediately before the atomic flat-file publication**. It may publish only when both remain absent. If either appears, it releases without writing and returns `DURABLE_MEMBERS_APPROVAL_REQUIRED`. Thus a write acknowledged before bootstrap is included in the later validated snapshot, while bootstrap cannot overtake an acknowledged flat write.
- Reads need no mutation lock after atomically capturing one authority selection for that call, but remain admitted operations so release drains them.
- Release changes the entry to closing before waiting. New reads, candidate submissions, commits, and working-location calls fail as released. Already admitted mutation completes or fails, releases its queue slot, and decrements the active-operation count. Only then does release discard process-local entries/revision maps and retain its bounded minimal reference tombstone.
- Different members remain usable while one member is paused at a fault boundary or draining release.

## 8. Compatibility and migration

1. Existing public service types and API version remain unchanged. Implementation enables the already-declared `memoryCandidateSubmission` and `approvedMemoryCommit` feature flags only when the protocol is active.
2. `src/local-provider.ts` owns the only authority-selection behavior, generation parsers, bootstrap anchor, current-pointer recovery, and mutation implementation. After bootstrap, `members.ts` compatibility reads delegate through existing public `LocalDurableAgentProvider` behavior (`provision`, `openTaskContext`, and `readMemoryItem`) using the already-normalized declaration; they do not parse generations or select authority themselves. The retained index DTO may synthesize its legacy `file: <id>.md` field from the validated public item id, but that compatibility label is never opened as an authority path.
3. First service provisioning/use of a valid flat store performs the non-destructive bootstrap in section 6. Existing `MEMORY.md` migration is validated and represented as the `legacy-memory` item before bootstrap. Valid source data is copied, never implicitly moved across workspace/global scope and never deleted by this task.
4. A valid legacy profile, guidance, memory index, item body, and working directory retain their existing meaning. Unknown future versions, symlinks, oversized data, NUL, digest mismatch, and profile conflict fail loud.
5. Before both anchor and current pointer exist, retained compatibility writers may continue producing the bounded legacy store only through the serialized/rechecked rule in §7. Once either durable discriminator exists, those authorization-free writer functions fail `DURABLE_MEMBERS_APPROVAL_REQUIRED`; they never update flat files or publish a generation. Confirmed mutations then use authorization-bearing `commitMemoryItem`.
6. No storage path or generation id is added to public results. The public provenance generation remains the opaque provider/reference generation, not a filesystem generation name.
7. The only deliberately repeated implementation detail across `local-provider.ts` and `members.ts` is the mechanical process-wide queue/lease identity needed before a legacy write; authority selection remains in `local-provider.ts`. Black-box fixtures pause a retained writer between its first observation and final recheck while production bootstrap runs, and mix retained reads with provider commits. Any key/name drift, missed recheck, or duplicated selector causes an acknowledged-write loss, cross-view mismatch, or forbidden flat publication and fails the fixture. No reviewer-suggested source file is made a requirement.

## 9. Fault-injection matrix

All fixtures call production provider methods. The filesystem proxy is executable with Vitest ESM mechanics:

1. `vi.hoisted()` creates one controller before module evaluation: armed fault id, exact operation/path-class key, remaining one-shot count, observed count, enabled flag, and a slot for the real fs module.
2. A top-level hoisted `vi.mock('node:fs/promises', async importOriginal => ...)` captures `await importOriginal()` in the controller and returns a proxy for the real module. The proxy delegates by default and wraps only the named functions used by production (`open`, `rename`, `mkdir`, `unlink`, `lstat`, `readFile`, and any directory-open call).
3. The wrapped `open` returns a `Proxy` around the real `FileHandle`. `writeFile`, `sync`, and `close` are intercepted as separate named boundaries; every other method is bound to the real handle with `Reflect.apply` so `this` remains valid. A fault after `sync` or `close` is therefore distinguishable from a fault before it.
4. Every arm is one-shot. The wrapper matches operation plus normalized private path class, decrements exactly once, records the hit, and throws the fixture error. The test asserts observed count `1` and remaining count `0`; an unconsumed or multiply consumed arm fails qualification.
5. `vi.resetModules()` runs before each dynamically imported provider scenario so production imports resolve through the already-registered hoisted mock with fresh module-local provider state. Each scenario uses a unique temporary member root so the process-wide lock registry cannot leak identity between cases.
6. Immediately after the production call settles, the controller is disabled before any raw-oracle read. The oracle uses the captured real fs module, never the mocked namespace, and imports no production parser, selector, builder, path helper, lock helper, or bounds constant.

This provides import isolation, real `FileHandle` sync/close coverage, exact one-shot fault proof, and an unmodified raw oracle without adding a public or product fault hook.

| ID | Injected point | Expected call result | Restart/raw-oracle outcome |
|---|---|---|---|
| C-01 | before candidate temp write | `PROVIDER_UNAVAILABLE` | no candidate; confirmed pointer unchanged |
| C-02 | after candidate temp sync, before rename | `PROVIDER_UNAVAILABLE` | temp may exist; no visible candidate; confirmed pointer unchanged |
| C-03 | after candidate rename, before directory sync | injected process failure; no confirmed result | complete candidate may exist but is `unconfirmed`; confirmed pointer unchanged |
| C-04 | after candidate directory sync | returned candidate is `unconfirmed` | candidate intact; confirmed pointer unchanged |
| B-O00 | before the first bootstrap object temp write | `PROVIDER_UNAVAILABLE`; no confirmed result | anchor absent; validated legacy remains authoritative; no bootstrap artifact is selected |
| B-O01 | after a bootstrap object temp write, before its sync | `PROVIDER_UNAVAILABLE`; no confirmed result | anchor absent; incomplete temp ignored; validated legacy remains authoritative |
| B-O02 | after a bootstrap object sync, before its rename | `PROVIDER_UNAVAILABLE`; no confirmed result | anchor absent; durable temp ignored; validated legacy remains authoritative |
| B-O03 | after a bootstrap object rename, before objects-directory sync | simulated power loss; no confirmed result | renamed object may be present or absent, but remains unreferenced and ignored; validated legacy remains authoritative |
| B-O04 | after each bootstrap object rename and objects-directory sync, before manifest temp write | `PROVIDER_UNAVAILABLE`; no confirmed result | complete unreferenced objects are ignored; anchor absent and validated legacy remains authoritative |
| B-M00 | before generation-zero manifest temp write | `PROVIDER_UNAVAILABLE`; no confirmed result | anchor absent; unreferenced objects ignored; validated legacy remains authoritative |
| B-M01 | after generation-zero manifest temp write, before its sync | `PROVIDER_UNAVAILABLE`; no confirmed result | anchor absent; incomplete manifest temp ignored; validated legacy remains authoritative |
| B-M02 | after generation-zero manifest sync, before its rename | `PROVIDER_UNAVAILABLE`; no confirmed result | anchor absent; durable manifest temp ignored; validated legacy remains authoritative |
| B-M03 | after generation-zero manifest rename, before generations-directory sync | simulated power loss; no confirmed result | manifest may be present or absent but is unanchored and ignored; validated legacy remains authoritative |
| B-M04 | after generation-zero manifest rename and generations-directory sync, before anchor temp write | `PROVIDER_UNAVAILABLE`; no confirmed result | complete unanchored generation ignored; anchor absent and validated legacy remains authoritative |
| B-00 | before anchor temp write | `PROVIDER_UNAVAILABLE` | no anchor; validated legacy remains authoritative |
| B-01 | after anchor temp sync, before rename | `PROVIDER_UNAVAILABLE` | anchor temp ignored; validated legacy remains authoritative |
| B-02a | after anchor rename, before directory sync; crash image retains rename | simulated power loss | complete anchor is visible; exact generation zero is authoritative |
| B-02b | after anchor rename, before directory sync; crash image loses unsynced rename | simulated power loss | no anchor is visible; original validated legacy remains authoritative and generation artifacts are ignored |
| B-03 | after anchor directory sync, before current temp | simulated interruption | anchor generation zero authoritative; recovery recreates only its pointer |
| B-04 | after current temp sync, before rename | `PROVIDER_UNAVAILABLE` | current temp ignored; anchor generation zero remains authoritative |
| B-05 | after current rename, before directory sync | simulated power loss | anchor-only or anchor-plus-current both select generation zero |
| B-06 | remove an established current after generation one exists | `INVALID_CONTEXT_DATA` | anchor present; neither generation zero, later manifest, nor legacy is guessed |
| G-00 | before object temp write | `PROVIDER_UNAVAILABLE` | old current generation and old selective read |
| G-01 | after object temp write, before object sync | `PROVIDER_UNAVAILABLE` | old current; incomplete staging ignored |
| G-02 | after object sync, before object rename | `PROVIDER_UNAVAILABLE` | old current; durable temp ignored |
| G-03 | after object rename/directory sync | `PROVIDER_UNAVAILABLE` | old current; unreferenced immutable object ignored |
| G-04 | after manifest temp write, before manifest sync | `PROVIDER_UNAVAILABLE` | old current; manifest temp ignored |
| G-05 | after manifest sync, before manifest rename | `PROVIDER_UNAVAILABLE` | old current; durable manifest temp ignored |
| G-06 | after manifest rename/directory sync | `PROVIDER_UNAVAILABLE` | old current; complete higher-sequence generation ignored |
| G-07 | after pointer temp write, before pointer sync | `PROVIDER_UNAVAILABLE` | old current; pointer temp ignored |
| G-08 | after pointer sync, before pointer rename | `PROVIDER_UNAVAILABLE` | old current; durable pointer temp ignored |
| G-09 | immediately after pointer rename, before directory sync | simulated process interruption | new complete generation is selected when new pointer is present; never a mixed state |
| G-10 | after memory-directory sync, before response | call may surface injected `PROVIDER_UNAVAILABLE` | new generation remains authoritative; retry is idempotent by content and yields confirmed state |
| G-11 | during staging cleanup | commit remains successful | new generation authoritative; cleanup residue ignored |
| R-01 | valid pointer names missing/corrupt manifest | `INVALID_CONTEXT_DATA` | no fallback, rewrite, or deletion |
| R-02 | valid manifest names missing/corrupt/NUL/oversized object | `INVALID_CONTEXT_DATA` | no fallback, rewrite, or deletion |
| R-03 | higher-sequence unreferenced complete generation exists | normal read succeeds | exact pointer generation wins |
| R-04 | corrupt/incomplete staging and stray journal exist | normal read succeeds | both ignored; exact pointer generation wins |
| L-01 | release begins while commit is paused before pointer rename | new admission fails released; release waits | after unpause, old or newly published complete generation is preserved before release resolves |
| M-01 | member A commit paused before pointer rename; member B commits | A remains pending | B completes independently; no cross-member object/catalog leakage |
| W-01 | retained writer paused before final anchor/current recheck while bootstrap queues | bootstrap waits | writer publishes and acknowledges first; bootstrap snapshot includes it |
| W-02 | bootstrap publishes anchor before queued retained writer reaches final recheck | writer returns `DURABLE_MEMBERS_APPROVAL_REQUIRED` | no flat write occurs; generation state remains authoritative |
| W-03 | participating second process holds `mutation.lock` | `CONCURRENT_MUTATION` | no partial publication or auto-removal of lease |

B-O00 through B-O04 and B-M00 through B-M04 cover the distinct bootstrap production path at every object and generation-zero-manifest write, sync, rename, and directory-sync boundary before authority exists. Every such failure returns no confirmed result, leaves the anchor absent, preserves the independently validated legacy authority, and ignores all partial or complete-but-unreferenced generation artifacts. B-00 through B-06 then cover the first-bootstrap discriminator; B-02a/B-02b are two explicit crash images made from the real pre-sync tree (rename retained versus unsynced rename absent), not two outcomes guessed by production. G-00 through G-11 separately cover an ordinary approved commit. A normal no-fault bootstrap/commit is run beside every injected case as the unmodified passing control.

## 10. Asymmetric fixture and oracle contract

### 10.1 Authorization asymmetry

- Submit candidate content containing `"status":"confirmed"`, `"approved":true`, and an approval-like provenance string through `submitMemoryCandidate`. Exact outcome: returned status is `unconfirmed`, feature result contains no confirmed revision, and raw current-pointer bytes are unchanged.
- Pass an extra top-level approval/status field in a runtime-cast candidate. Exact outcome: `REJECTED_CANDIDATE`; no candidate or confirmed mutation.
- Call `commitMemoryItem` with missing, NUL, oversized, or unknown authorization kind. Exact outcome: `REJECTED_CANDIDATE`; old item/catalog/revisions remain.
- Supply a valid authorization with matching candidate and item. Exact passing outcome: returned status `confirmed`, committed item is selectively readable, and the next snapshot exposes its metadata with an advanced revision.

### 10.2 Publication asymmetry

Every B/G fixture proves that its exact one-shot operation/path counter was consumed; cases after a write additionally prove the intended temporary or durable specimen changed before interruption. B-O00–B-O04 and B-M00–B-M04 invoke the real bootstrap path, require no confirmed result, require the anchor to remain absent, require unchanged independently validated legacy reads, and prove partial/unreferenced generation artifacts are ignored; each runs beside a no-fault bootstrap passing control. B-00–B-02 require either legacy or the exact anchored copy of that same validated legacy snapshot according to the discriminator actually visible after restart. B-03–B-05 require generation zero and forbid legacy reauthorization. B-06 requires fail-closed refusal.

Every G-00 through G-08 case then restarts a fresh provider through `provision`, `openTaskContext`, and `readMemoryItem`. Exact outcome: old item/catalog remains authoritative and the proposed new/updated item is `UNKNOWN_MEMORY_ITEM` or retains old content. G-09 through G-11 require the new complete item/catalog. W-01/W-02 prove the final under-lock recheck controls acknowledgement order; W-03 proves unsupported participating cross-process overlap fails closed.

The passing controls run the same legacy snapshot and approved input without a fault and require bootstrap preservation, new item/catalog metadata, confirmed status, and revision advancement.

### 10.3 Independent raw oracle

The test oracle is deliberately smaller than and independent from production selection:

1. read `generation-mode.json` and `current.json` using raw filesystem calls after disabling the injector;
2. parse their fixed closed shapes and apply only the fixture's expected discriminator case: no anchor permits the pre-captured legacy control, anchor-plus-no-current permits only the exact anchored generation zero when no later manifest exists, and a valid current selects exactly its manifest;
3. read exactly the selected manifest and independently recompute its SHA-256;
4. read every named object and independently recompute byte count and SHA-256;
5. assert no catalog entry lacks valid content, no unreferenced staging/generation appears in the selected catalog, and legacy bytes are never selected when the anchor is present;
6. compare the selected raw values with results obtained by public `openTaskContext` and `readMemoryItem`.

It may use standard JSON parsing, byte length, and cryptographic hashing, but must not import production parsers, recovery selectors, manifest builders, path builders, mutation helpers, or constants that decide authority. Test-local expected bounds are literal contract values so a shared wrong constant cannot make both producer and oracle pass.

### 10.4 Concurrency and release fixtures

- Two same-member commits are released from a barrier in known enqueue order. Exact outcome: both complete serially, final pointer sequence advances twice, final catalog contains both results, and neither manifest loses the other item.
- Two different-member commits use separate barriers. Exact outcome: member B completes while A remains paused; each snapshot contains only its member's metadata and body.
- Pause an admitted commit at G-06, call release, and attempt another mutation. Exact outcome: the new mutation fails released, release remains pending, the admitted commit resolves after unpause, then release resolves. Reprovision reads the durable complete result.
- Capture an `openTaskContext` for old metadata, commit a replacement, then call `readMemoryItem` using the same ref. Exact outcome: the later call returns the new complete metadata/body/revision. A second fixture pauses pointer replacement during each individual call and requires each result to be wholly old or wholly new, proving per-call consistency without cross-call affinity.
- W-01/W-02 execute retained writes and provider bootstrap through their production entry points with a barrier immediately before the retained writer's final discriminator recheck; acknowledgement and bootstrap contents must follow queue order exactly.

## 11. Bounded implementation handoff

The successor `memory_lifecycle` task can implement this conclusion entirely inside its already approved r2 files. The a01 review suggestion of a new `memory-store.ts` is nonbinding and is not promoted into a task requirement.

- `src/local-provider.ts` owns the sole authority-selection behavior: private layout constants, strict parsers, bootstrap anchor/current recovery, hashing, process-wide queue registry, mutation lease, candidate submission, approved commit, admission/drain integration, and feature flags. This file remains the only code that interprets generation authority.
- `src/members.ts` keeps bounded legacy parsing/writing before bootstrap. Its mechanical queue/lease key and final discriminator recheck conform to §7. After bootstrap, a private nonexported compatibility adapter in this existing file constructs/reuses `LocalDurableAgentProvider` with the already-normalized declaration and delegates reads through public `provision`, `openTaskContext`, and `readMemoryItem`; it does not parse anchor/current/manifest authority. Authorization-free retained writes reject after the discriminator appears.
- `src/errors.ts` uses existing public service codes only. The retained TypeError string `DURABLE_MEMBERS_APPROVAL_REQUIRED` does not add or alter a service error code.
- `tests/memory-lifecycle.spec.ts` implements authorization, B/C/G/R/W fault cases, hoisted proxy, raw oracle, process-local/cross-process-contract fixtures, concurrency, migration, per-call reads, and release.
- `tests/local-provider.spec.ts` retains provider/security regressions and adds only feature/revision cross-checks.

No new required source file, task, dependency, command, effect, public export, service method, API version, storage path, or GAT authority is introduced. Duplication/drift is prevented observably: black-box W-01/W-02 fixtures fail if the two existing files use different lock identity, marker names, or acknowledgement ordering, while provider-versus-compatibility read comparisons fail if `members.ts` reimplements selector semantics. This meets the approved output DoD without changing WBS r2.

## 12. Acceptance mapping

A01 review closure:

| Finding | Corrected contract |
|---|---|
| MPQ-PTR-001 | §§2–6; immutable anchor, B-00–B-06, exact retained/lost pre-sync crash images, and fail-closed established-pointer loss |
| MPQ-SHARED-002 | §§8, 11; suggestion adjudicated as nonbinding, selector owned by existing `local-provider.ts`, compatibility reads delegate through public provider behavior, no required new file/export |
| MPQ-COMPAT-003 | §§7–10; one storage-identity queue/lease, immediate final discriminator recheck, W-01/W-02 acknowledgement oracle |
| MPQ-READ-006 | §5.4 and §10.4; per-call capture and explicit no cross-call affinity fixture |
| MPQ-FS-PROXY-004 | §9; hoisted ESM proxy, real FileHandle wrapping, module reset/dynamic import, one-shot counters, disable-before-raw-oracle |

| Task acceptance criterion | Protocol sections | Required fixtures/evidence |
|---|---|---|
| One deterministic recovery rule and explicitly ordered authoritative effects | §§3, 5, 6 | B-00–B-06, G-00–G-11, R-01–R-04, immutable anchor plus raw pointer/manifest/object oracle |
| Every publication boundary and concurrency/release interaction maps to a fault or asymmetric fixture with exact outcome | §§7, 9, 10 | B/C/G/R/W cases, L-01, M-01, same-member FIFO, per-call read race, and passing controls |
| Bounded existing-package handoff; no GAT authority or public service change | §§1, 2, 8, 11 | unchanged `service.ts`, existing successor files only, no required reviewer-suggested module/export |
| No unresolved high-severity durability, authorization, oracle, or compatibility ambiguity | §§3–11 | reviewer traces discriminator power-loss outcomes, final compatibility recheck, fs proxy mechanics, negative precedence, and independent oracle |

## 13. Self-review checklist for independent review

- Exactly one protocol is selected; no journal replay alternative competes with the pointer rule.
- Bootstrap has an immutable durable discriminator: before anchor publication legacy is eligible; after it, legacy can never regain authority. Exact pre/post power-loss outcomes are stated.
- Bootstrap-anchor and subsequent pointer authority boundaries are ordered only after durable objects and a complete manifest.
- Old state remains authoritative before a later pointer replacement; new complete state is authoritative afterward.
- Corrupt authoritative bytes fail closed rather than selecting by directory order.
- Candidates cannot grant approval, and authorization covers the explicit committed item.
- Same-member serialization covers bootstrap, commits, candidates, and final-rechecked retained writes under one process-wide identity/lease; different members remain independent and unsupported cross-process overlap fails closed.
- Read consistency is explicitly per public call, with no cross-call snapshot affinity.
- The hoisted Vitest proxy specifies import isolation, real FileHandle binding, sync/close boundaries, one-shot counters, and disable-before-raw-oracle.
- Release closes admission and drains admitted mutations without deleting persistent data.
- Bounds, UTF-8/NUL, symlink, version, scope, and legacy behavior are explicit.
- Every durable boundary has an injected fault and exact old/new oracle result.
- The raw oracle invokes production public paths but shares no authority-selection semantic helper.
- The handoff stays within existing r2 package/test files, treats the suggested new module as nonbinding, and requires no WBS, public service, or GAT change.
