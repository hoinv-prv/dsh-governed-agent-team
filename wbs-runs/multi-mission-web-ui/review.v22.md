# Review candidate multi-mission-web-ui, revision 22

- SHA-256: `f6d7e37d882c96982feea06e766b26c5a4b0d29aca05bf119ebfa007f8be7c8a`
- Base: HUMAN-approved revision 21 `113c041b61324d124cf36429d25852cbf6e78ee923548a87faf1609d0e857a03`
- Validate/hash: PASS.

## Trigger and exact delta

After v21 reconciliation, execution found that v20/v21 authorized deletion write paths but provided no executable deletion mechanism, while available file tools cannot remove files. Revision 22 adds a zero-dependency fixed-purpose Node cleanup tool, hashes it as a plan source, and adds its exact no-argument command to global/task command grants. It can unlink only the two already hash-preserved unauthorized attempt-1 tests.

Selecting this correction requires governance-replan attempt 7. To keep the HUMAN-set cumulative cap exactly 50, one attempt moves from `implementation-freeze` (2→1) to `governance-replan` (6→7); effort ceiling falls 6,170→6,125 minutes. Current charge 32 + remaining 18 = 50.

Independent review required the hash-pinned cleanup tool to remain read-only; its accidental task write grant was removed while the two deletion targets remain writable. No product redesign, verification command, dependency, review/HUMAN gate, Workspace path, DSH/network/dependency/accepted-conformance boundary, or other task limit changes.
