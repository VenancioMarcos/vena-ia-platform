# Arquitetura Técnica — Ponteiro

O documento canônico de arquitetura da Vena_IA Platform foi consolidado na raiz do repositório:

➡️ **[`/ARCHITECTURE.md`](../ARCHITECTURE.md)**

A decisão arquitetural formal permanece registrada em `docs/adr/ADR-001.md`.

## Baseline CAD vigente

As Rotas 2 a 5 do pipeline STEP estão integradas na `main` em `00ed21d`. O fluxo
analítico isolado, seus limites e o diagrama navegador → gateway → sandbox → worker
→ perfil RZ → SVG estão registrados na Seção 23 do documento canônico. A baseline
permanece sem porta de máquina ou autoridade física.
