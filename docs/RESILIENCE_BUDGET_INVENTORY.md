# Inventário de budgets de resiliência — v1.6 Package 2

Fonte executável: `resilience-policy.json` (`vena-ia.resilience-policy/v1`).
Timeout de conexão não é tratado como timeout total. Zero significa “não aplicável”,
nunca infinito. Nenhuma operação possui tentativas ou fila ilimitadas.

| Operação | Dependência | connect/read/total (s) | Tentativas | Backoff/jitter | Idempotência e esgotamento |
|---|---|---:|---:|---|---|
| frontend request | API | 30/30/30 | 1 | nenhum | cliente não repete; erro explícito |
| connect/readiness | PostgreSQL | 5/0/5 | 1 | nenhum | leitura; readiness 503 |
| auth e fila | Redis | 1/1/1 | 1 | nenhum no cliente | falha fechada 503; recovery deriva do PostgreSQL |
| documento | MinIO | 3/10/13 | 1 | retries SDK desativados | estado não avança sem confirmação |
| chat/embeddings/completion | OpenAI | 5/30/30 | 3 | exponencial 0,25–2; jitter 20%; Retry-After limitado | somente classes permitidas; 502/503 seguro |
| processamento | worker | cooperativo/900 | 3 | exponencial 2–300; jitter 20% | job/idempotency persistidos; terminal ao esgotar |
| backup/restore | PostgreSQL+MinIO | subprocesso/3600 | 1 | nenhum | lock exclusivo; falha fechada |
| lease/heartbeat | Redis | 1/1/1 | 1 por chamada | renovação periódica | lease perdido agenda retry seguro |

## Divergências encontradas e tratadas

O provider OpenAI possuía timeout único de 30 s, sem classificação, deadline global,
retry, jitter ou backpressure. PostgreSQL e MinIO não declaravam seus budgets no
settings. O retry de jobs não tinha teto separado nem jitter. Esses pontos agora
são explícitos, validados na inicialização e cobertos pela policy.

## Limitações residuais

Concorrência de IA é por processo; o worker atual executa um job por processo.
Timeout de bibliotecas síncronas continua cooperativo. A fila Redis é durável e
limitada pelos jobs persistidos, mas este pacote não mede capacidade, carga ou SLO.
