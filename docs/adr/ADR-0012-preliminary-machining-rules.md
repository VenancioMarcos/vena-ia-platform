# ADR-0012 — Regras preliminares de fresamento

**Status:** Aprovado
**Data:** 2026-07-30

## Decisão

A primeira fundação v0.7 usa regras determinísticas tipadas para três famílias
de material e limita rotação/avanço à capacidade informada da máquina. Todos os
resultados são preliminares e exigem revisão humana.

Não são gerados toolpaths, G-code, comandos de máquina ou alegações de segurança.
Catálogos persistentes de materiais, máquinas e ferramentas permanecem para os
incrementos seguintes da própria v0.7.

## Fórmulas

```text
rpm = 1000 × velocidade_de_corte / (π × diâmetro)
avanço = rpm × número_de_dentes × avanço_por_dente
tempo_de_corte = comprimento_de_corte / avanço
```

Os limites de RPM e avanço da máquina são aplicados antes da estimativa de tempo.
