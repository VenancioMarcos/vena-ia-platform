# Relatório de gargalos — perfil sintético pequeno

| Gargalo/limite | Evidência | Severidade | Mitigação atual | Próximo gate |
|---|---|---|---|---|
| IA: limite por processo | policy fixa 8 por API; perfil usa concorrência total 4 | baixa no perfil, residual horizontal | decisão A: suficiente somente para topologia testada; 16 teórico em 2 processos | Redis compartilhado se perfil futuro exceder |
| Worker: um job por processo | dois workers/claims únicos no harness e CI Redis | média | dois workers, lease, heartbeat, retry/recovery PostgreSQL→Redis | medir processamento PDF real maior |
| PostgreSQL/Redis/MinIO | CI usa serviços únicos compartilhados | média | budgets, fail-closed, readiness e recovery | topologia externa/pool dedicado antes de piloto |
| Métricas por processo | R-032; sem backend histórico | média | evidência JSON checksummed + auditoria PostgreSQL | backend/exporter em gate autorizado |
| Timeout síncrono | R-038; carga não preempta biblioteca | média | deadline cooperativo, lease e recusa de resultado tardio | isolamento de processo se comprovadamente necessário |
| Harness CPU/hash | 200 operações sem erro; números muito abaixo do guardrail | informativa | execução curta e separada | não usar como capacidade da plataforma |

O primeiro limite explícito da topologia testada é o worker unitário por processo;
adicionar o segundo worker preserva claims exclusivos. O limite de IA por processo é
suficiente para concorrência 4 do perfil, mas não prova escalabilidade horizontal.
Nenhuma otimização preventiva ou arquitetura paralela foi introduzida.
