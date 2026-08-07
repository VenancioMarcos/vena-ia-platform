# ADR-0030 — Ownership organizacional de catálogos Engineering

**Status:** Aceita; Packages 1–2 aprovados
**Data:** 2026-08-07
**Decisão relacionada:** `DEC-038`

## Contexto

Os catálogos Engineering eram globais para todo usuário autenticado, permitindo
leitura e combinação entre organizações.

## Decisão

Adicionar `scope_type` e `organization_id`. Itens da API são
`ORGANIZATION_OWNED`; membership ativa lê e OWNER/ADMIN escreve. Team scope foi
rejeitado por não existir requisito técnico. Referências controladas são
`SYSTEM_REFERENCE`, sem owner e read-only. Linhas preexistentes tornam-se
`LEGACY_UNSCOPED` ocultas, sem atribuição inventada.

Token e banco permanecem autoridade. A query apenas seleciona a Organization;
schemas rejeitam authority fields. Consumers downstream aplicam a mesma política.

## Consequências

- Contrato v1 preservado com campos aditivos; criação passa a exigir Organization.
- Unicidade por Organization para owned e global para referências.
- FK `RESTRICT`; nenhuma exclusão silenciosa por cascade.
- Downgrade preserva linhas e não restaura unicidade global incompatível.
- Update/delete, export e retention pertencem ao Package 2.
- R-048 é parcialmente mitigado; deploy e fronteira CNC não mudam.

## Extensão Package 2 — evidence

Governance evidence é composto em leitura por recurso autorizado no contrato
`vena-ia.engineering-governance-evidence/v1`. Nenhuma tabela/migration é adicionada.
Lifecycle reflete estados reais; delete, retenção e reconciliation registram limites.
Audit reference identifica a classe do evento, pois o schema atual não possui resource
ID e não deve gerar correlação falsa.
