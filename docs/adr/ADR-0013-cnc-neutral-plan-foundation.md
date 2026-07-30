# ADR-0013 — Fundação neutra e não executável de CNC

**Status:** Aprovado
**Data:** 2026-07-30

A primeira entrega v0.8 representa operações e parâmetros em estrutura neutra.
Não gera blocos de controlador, toolpaths ou G-code. Fanuc Oi e Romi D1250 são
apenas perfis planejados, sem alegação de compatibilidade validada.

Toda saída é `SIMULATION_ONLY_REQUIRES_HUMAN_REVIEW`,
`executable_output=false` e proibida para transmissão ou produção. Validação
sintática futura não equivalerá a validação física.
