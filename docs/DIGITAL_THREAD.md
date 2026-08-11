# Versioned Digital Thread v1

`vena-ia.digital-thread/v1` is an immutable non-production manifest connecting CAD,
topology evidence, manufacturing geometry, verified process plan, toolpath candidate,
G-code candidate, verification evidence, review state and report.

Each artifact records identity, type, schema, canonical content hash, organization,
lifecycle, upstream/downstream references, provenance, generation/replay metadata,
verification references and limitations. Invalid hashes, ordering, refs, versions,
stale/revoked state and cross-organization access fail closed.

`vena-ia.bounded-manufacturing-intelligence/v1` can explain, summarize, compare and
identify missing evidence. It is read-only, has no tools and cannot mutate facts,
approve gates, resolve G9 or grant physical authority.

No table, ledger, event sourcing or migration is introduced. G9 remains
`PENDING_AUTHORITATIVE_REVIEW`; readiness and physical authority remain false.
