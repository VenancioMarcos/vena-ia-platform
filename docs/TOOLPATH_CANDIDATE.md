# Toolpath Candidate v1

`vena-ia.toolpath-candidate/v1` é um artefato determinístico e não executável para
validação controlada. Só consome `vena-ia.manufacturing-geometry-model/v1` com
`vena-ia.verified-process-plan/v1` pronto para revisão e uma operação explícita.

## Escopo

O gerador produz apenas segmentos lineares 3-axis/2.5D, rapid/feed candidatos,
clearance/retract explícitos, ferramenta, limites da máquina, regiões-alvo e hashes
de provenance/replay. Cada resultado declara `REQUIRES_HUMAN_REVIEW`,
`executable_output=false` e `production_authority=false`.

## Verificação independente

O verificador não reutiliza a geração. Ele valida allowlist de primitive, números
finitos, bounds, continuidade, semântica feed/rapid, referências de região e
interseção preliminar de pontos de feed com o envelope final protegido pela geometria
da ferramenta. Uma falha gera `REJECTED`.

## Limites

Não há arcos, CAM universal, cutter sweep, collision de holder/fixture, remoção de
material, cinemática, postprocessor, RS274, G/M-code, NC/DNC, transmissão ou controle
de máquina. A verificação física continua falsa.
