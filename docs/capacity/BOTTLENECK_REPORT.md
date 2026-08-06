# Relatório de gargalos — gate integrado descartável

| Gargalo/limite | Evidência R1 | Estado | Próximo gate |
|---|---|---|---|
| IA por processo | limite 1 no CI; saturação real em API A/B retorna 503 e Retry-After | decisão A válida somente para a topologia testada; sem coordenação distribuída | medir perfil autorizado maior antes de alterar arquitetura |
| Worker unitário | dois processos, claims Redis, heartbeat individual derivado, interrupção e lease recovery | parcialmente mitigado | corpus maior e execução manual longa |
| PostgreSQL | duas APIs/dois workers no mesmo banco; conexões não são exportadas no bundle | monitorar | pool e telemetria histórica antes de piloto |
| Redis | auth, rate limit, revogação, idempotência, fila, lease e recovery compartilhados | comprovado no CI descartável | sizing e persistência do ambiente alvo |
| MinIO | upload/leitura/cleanup reais; pause/unpause comprova falha segura e retorno | comprovado no CI descartável | storage externo e política operacional autorizada |
| Métricas | continuam por processo; evidência agrega somente resultados seguros | R-032 residual | backend autorizado de métricas |
| Timeout síncrono | lease/deadline não preemptam toda biblioteca bloqueante | R-038 monitorado | isolamento de processo apenas se necessário |
| Harness CPU/hash | preservado como `HARNESS_ONLY_BASELINE` | informativo | nunca usar como capacidade da plataforma |

O limite agregado de IA observado é a soma dos limites locais das duas APIs; não há
coordenação distribuída de concorrência. O gate mede uma topologia pequena em runner
compartilhado e não justifica autoscaling, SLO, SLA, piloto ou deploy.
