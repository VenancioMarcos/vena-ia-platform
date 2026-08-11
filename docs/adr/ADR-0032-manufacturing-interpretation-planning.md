# ADR-0032 — Manufacturing Interpretation and Verified Process Planning

**Status:** Implemented — TASK-V22-002 / awaiting CTO review

## Contexto

Topology evidence descreve geometria, não stock, intenção, setup ou processo. A
conversão automática de cylinder/plane em drilling/milling criaria falsa autoridade.

## Decisão

Adotar `manufacturing-geometry-model/v1`, `verified-process-plan/v1` e
`planning-verification-evidence/v1` como read models efêmeros. Inputs explícitos de
stock/intent/fixture/datum e os catálogos autorizados v2.1 são gates. Regiões externas
ao envelope são bounded; interior incerto permanece desconhecido. Accessibility é
somente cardinal 3-axis/2.5D. IDs/replay são hashes canônicos.

## Alternativas rejeitadas

* stock = final bounding box: inventa matéria-prima;
* FeaturePlanningBridge como planner geral: regra fechada não cobre stock/setup;
* cylinder→drilling ou plane→milling: confunde forma com intenção;
* promover virtual CNC validation: não há engine física/collision/kinematics;
* catálogo paralelo: quebraria ownership e R-048.

## Consequências

Novo endpoint aditivo, sem migration/persistência. Ausência retorna missing-input
estruturado. Planning verification prova coerência/replay, não segurança física.

## Integração documental

A Gap Analysis da PR #26 é portada integralmente para a PR #27. Documentos de estado
da PR #27 são a linha oficial atual; PR #26 torna-se redundante somente após prova de
blob remoto preservado. Histórico verdadeiro não é reescrito.

## Limites

Sem v2.3, toolpath, postprocessor, G/M-code, NC/DNC, simulation Level 2/3 ou máquina.
