# CTO-CODEX-AUTO-042 — Adaptador textual STEP local

**Data:** 2026-09-12  
**Estado:** Em validação local

## Entrega

`step-geometry-adapter.ts` inspeciona no máximo 64 KiB de texto STEP em memória,
extrai schema AP203/AP214/AP242, unidade e identificador de aplicação quando
presentes. A presença de B-Rep é apenas textual; sem token reconhecido, retorna
motivo estruturado. Não gera pontos, trajetórias ou geometria para o visualizador.

A rota mostra metadados em card colapsável após a aceitação local e informa que a
análise definitiva depende de despacho assíncrono autorizado. Não há HTTP, backend,
dependências, emissão ou ação física.
