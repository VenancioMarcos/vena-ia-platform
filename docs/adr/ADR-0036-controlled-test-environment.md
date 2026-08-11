# ADR-0036 — Controlled CAD-to-G-code Test Environment

**Status:** Implemented — awaiting CTO review

## Context

Existing releases provide deterministic evidence, bounded candidate generation,
independent verification and an immutable Digital Thread, but not one authenticated
orchestration/download path. Joining these services can create false physical
authority if client state or an automatic gate is treated as production approval.

## Decision

Add an orchestration service that reuses existing modules without duplicating their
algorithms or persistence. Require token identity, active organization membership and
organization-scoped catalogs. Issue a short-lived HMAC proof bound to authenticated
user and immutable artifact hashes. Revalidate every downloadable candidate
server-side, including independent RS274, blind replay and Digital Thread replay.
Keep G9 permanently pending in this public contract.

The UI displays all gates and limitations and exposes only a `.candidate.nc`
download. It has no G9 approval, machine connection or production control.

## Consequences

The chain is operable in a controlled test environment with traceable evidence and no
new migration. It remains bounded synthetic validation: exact material removal,
holder collision, kinematics, real controller validation and physical authorization
stay outside scope. Client payloads cannot produce a valid download without the
server proof, current membership and matching immutable hashes.
