# Output Draft

## Current candidate

- `wbs-runs/multi-mission-web-ui/control-plane-stabilization-design.v2.md`
- SHA-256: `fd2e257cb84453c68700ab03b4f4980f415a871162993e98fe1c7105e1caba63`
- Lineage: v1 SHA-256 `5deeaba1e8210ca4a78eafa747a2e7eb5caca21ebbc55a8ed13a482118eb746f` → run-002 terminal failure with eight verified authority findings → corrected v2 → immutable run-003.

## Corrected design position

- Root cause is stated as the best-supported common control deficiency, not proven sole historical cause; a counterfactual table maps every observed control failure to a pre-charge predicate.
- AdmissionBundle is proof-only, time-bound and procedural. It cannot grant authority and does not claim non-bypassable DSH enforcement or elimination of the external-state TOCTOU race.
- Live predicates are re-observed at the charge boundary; drift expires the bundle. The first durable charge record binds bundle hash, boundary receipt and attempt allocation.
- Reviewer route availability is distinguished from provider-capacity reservation; only worst-case call budget is reserved.
- HUMAN exclusively owns approval, ceiling/reallocation, contingency selection and required acceptance. Coordinator may only record/project exact HUMAN decisions.
- Command authorization binds exact argv to a hashed allowed-command union. Quiescence is an expiring native snapshot rather than an absolute future-write claim.
- Ledger migration now names the operation owner and explicit restore/re-entry behavior after validator/review failure.
- Failure-model evidence is pinned by exact snapshot hash.

## Review state

- Run-002 did not produce a council verdict: required adversarial/outside envelopes failed schema and the separate Chairman invocation failed.
- All eight valid authority findings were parent-verified and corrected in v2.
- Run-003 is currently reviewing the exact immutable v2 bytes using fresh independent authority, adversarial and outside-view lanes.
- No WBS may be built until a latest design obtains a valid council `pass` or `pass_with_notes` and the HUMAN later decides budget/migration policy.
