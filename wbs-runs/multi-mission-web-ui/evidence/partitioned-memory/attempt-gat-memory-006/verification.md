# Partitioned memory verification — attempt-gat-memory-006

WBS v23; charge 39. Exact command exited 1: 11 tests, 9 pass, 2 fail.

Normative tenant/epoch audit, zero-prior authenticated GENESIS, sequence high-water, full decision snapshots, every before/after-state crash boundary, exact CLASS-001 cases, and base non-purge domain replay tests progressed. Two bounded recovery assertions failed:

1. replaying a purge suffix deleted the record before the subsequent manifest-inventory evidence loop, so `purge_manifest_won` evidence was omitted despite non-resurrection;
2. a restored tombstone idempotent retry hit `REVISION_CONFLICT` because `revise()` checked current revision before the restored idempotency result.

Hashes: source `88d01951bc8f2cf6225fda142b31c1ac63e2917d2ac73d0403afcf01c5185a6b`; declarations `6c45daf5171e62cca506ff76d46518209b9484a44a0303f34137100e7562f8a6`; tests `dd10b1517d19b831f2b6ddbd8bb6791faf15befdd2b250a59ba64501fd82dc13`, `1d27dfe3de082923e568b732039049c7fff6e0c1c3e74723be3a71fbe6c49b16`, `4451bcf0dfdc4265d626fd3acb159a5bb7c1f527090f502b211d7972560bf8c3`.

No acceptance/review claimed; final attempt 7 may correct only these bounded findings.
