# ADR-0033 — Bounded Toolpath Candidates and Independent Verification

**Status:** Implemented — v2.3 Package 1

## Contexto

v2.2 fornece geometria e plano de processo verificado, mas não uma trajetória. A
próxima fronteira precisa permanecer controlada e não produzir autoridade física.

## Decisão

Criar contratos aditivos de toolpath e verificação, com apenas segmentos lineares
3-axis/2.5D. O verificador é uma classe independente do gerador e falha fechado.
Regiões vêm exclusivamente do plano v2.2 e o envelope final é protegido de forma
preliminar pela metade do diâmetro da ferramenta.

## Consequências

Há evidência de candidato/replay, não CAM nem simulação. Postprocessing, RS274,
G-code, material removal, collision e cinemática são gates posteriores. Toda saída
permanece não executável, sem machine-send e sob revisão humana.
