# Partitioned memory review — changes required

Independent review confirms physical selector, normalized retrieval, derived expiry, basic idempotency, and local mutation ownership pass, but identifies material residuals:

1. Audit digest/GENESIS and evidence fields do not match the accepted raw-prior/RFC8785/`sha256:` protocol or carry complete decision-reproduction hashes.
2. Sink prepare precedes journal durability; sink commit/lifecycle/idempotency crash boundaries are incomplete and non-idempotent. Get/search perform backend lookup before audit admission; required operator alerts are absent.
3. Hold/purge HUMAN authority and policy/hash bindings plus purge manifest dispositions/content hashes/deadline/inventory are incomplete; manifest failure boundaries are untested.
4. Old-backup restore rejects on high-water mismatch instead of reconciling purge manifest/anchored suffix and returning restore-without-resurrection evidence.
5. Record/privacy validation remains permissive: empty authority/etc., opaque hashes, missing classification/secret/source-ref/retention/tombstone/prior-revision validation.

Attempt 3 fails independent review. Attempts 4–5 remain under v22 for a revised protocol-complete hypothesis.
