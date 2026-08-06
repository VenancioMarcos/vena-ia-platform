# Evidência de capacidade sintética controlada — v1.6 Package 3

Perfil: `vena-ia.capacity-profile/v1` (`ci-synthetic-pilot-small`). Evidência:
`vena-ia.capacity-evidence/v1`. O teste local usa 200 operações, concorrência 4,
duas APIs lógicas, dois workers e soak de 3 segundos.

## Resultado local inicial

| Cenário | Operações | Falhas | p50 | p95 | p99 | Throughput observado |
|---|---:|---:|---:|---:|---:|---:|
| harness CPU/hash sintético | 200 | 0 | 0,0011 ms | 0,0031 ms | 0,0156 ms | 28.498/s |

Soak: 3,000 s, 653.833 operações triviais, zero erro, zero crescimento líquido
medido pelo `tracemalloc`, pico 116 bytes, fila final zero e cleanup PASS. Estado
compartilhado sintético: 200 submissions, 200 claims únicos, zero duplicação.

Esses números medem apenas overhead do harness no runner local e variam por máquina.
Não representam API, banco, storage, IA, capacidade produtiva, usuários suportados,
SLA, SLO, benchmark comercial ou aprovação de piloto/deploy.

## Guardrails técnicos

Zero violação de isolamento, resposta falsa, estado impossível, duplicação, segredo,
job preso ou fila residual. Falha permitida: zero. p95 do harness: até 500 ms.
Crescimento no soak curto: até 8 MiB. Recuperação e cleanup são obrigatórios.
Esses limites são `TECHNICAL_TEST_GUARDRAIL`, não compromisso operacional.
