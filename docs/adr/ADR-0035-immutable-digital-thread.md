# ADR-0035 — Immutable Digital Thread and Bounded Intelligence

**Status:** Implemented — v3.0 Release Candidate

## Context

The platform has deterministic artifacts but lacked one versioned, replayable chain.
A database ledger would add tenancy and lifecycle complexity without a current need.

## Decision

Create a frozen `vena-ia.digital-thread/v1` manifest over existing artifacts and
storage. Canonical hashes, schema allowlists, lifecycle, chain refs, provenance,
organization ownership and replay fail closed. Authorization comes from token plus
database membership. Add read-only bounded intelligence with no tools or mutation.

## Consequences

The chain is portable and auditable without migration. Caller-managed storage does
not become an authoritative ledger. Intelligence cannot modify evidence, resolve G9,
approve G-code or grant physical authority. Persistence can be reconsidered only with
a real reversible tenancy-safe requirement.
