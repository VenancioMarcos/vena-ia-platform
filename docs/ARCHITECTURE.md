# Arquitetura Técnica — Ponteiro

O documento canônico de arquitetura da Vena_IA Platform foi consolidado na raiz do repositório:

➡️ **[`/ARCHITECTURE.md`](../ARCHITECTURE.md)**

A decisão arquitetural formal permanece registrada em `docs/adr/ADR-001.md`.

## Baseline CAD/CAM/CNC/SIM vigente

O pipeline ponta a ponta está integrado na `main` em `227bc35`. O fluxo CAD STEP
permanece descrito na Seção 23 do documento canônico; a Seção 24 consolida CAD →
CAM → CNC → SIM, os módulos, contratos e barreiras fail-closed. A baseline permanece
sem porta de máquina, liberação de G9 ou autoridade física.
