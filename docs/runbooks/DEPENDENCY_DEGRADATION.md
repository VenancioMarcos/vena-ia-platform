# Runbook — degradação de dependências

Contrato: `vena-ia.resilience-policy/v1`.

| Dependência | Lenta/intermitente | Indisponível/inválida | Recuperação |
|---|---|---|---|
| PostgreSQL | timeout limitado; sem sucesso antes do commit | falha fechada; readiness 503 | probe leve `SELECT 1` |
| Redis | timeout limitado; sem fallback silencioso | auth e fila falham fechadas | worker reconcilia do PostgreSQL |
| MinIO | connect/read limitados, SDK sem retry implícito | documento não fica disponível | bucket/stat confirmam retorno |
| OpenAI | retry classificado e limitado | 502/503 seguro, sem resposta falsa | próxima operação usa o mesmo provider |
| Worker | lease/heartbeat e deadline cooperativo | retry durável ou terminal | reconciliador reapresenta jobs elegíveis |

`/health` continua leve e não consulta dependências. `/ready` usa probes bounded,
retorna somente estados allowlisted e nunca expõe host, credencial, stack ou topologia.
Saturação de IA retorna 503 com `Retry-After: 1`; o frontend não repete automaticamente.

Execute `python scripts/resilience_drill.py` para os 20 cenários sintéticos. O drill
não chama API paga, não usa dados reais e não mede capacidade, SLA ou SLO.
