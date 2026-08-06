# Runbook — provedor de IA

O único provider autorizado continua OpenAI; não existe failover automático.

* confirme `OPENAI_API_KEY` somente no secret manager/ambiente;
* valide a policy e os settings antes de iniciar a API/worker;
* 401/403 indicam configuração/permissão e não recebem retry;
* 429 e indisponibilidade temporária respeitam attempts, jitter, backoff e deadline;
* respostas vazias/malformadas e vetores não finitos falham sem persistência;
* contagem/dimensão de embeddings são validadas antes do pgvector;
* backpressure é por processo e retorna erro explícito, sem fila ilimitada;
* nenhum prompt, resposta, embedding, token ou ID de domínio entra em métrica.

Após retorno do provider, repita somente a operação idempotente autorizada ou use o
retry durável do job. Nunca apresente fallback sintético como resposta real.
