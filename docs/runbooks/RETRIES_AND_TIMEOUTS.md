# Runbook — retries e timeouts

Contrato: `vena-ia.resilience-policy/v1` em `resilience-policy.json`.

1. Execute `python scripts/resilience_policy.py` antes e depois de alterar budget.
2. Nunca aumente tentativas, timeout, backoff ou concorrência sem regressão e revisão.
3. Retry é autorizado por operação. Autenticação, autorização, payload/resposta
   inválidos, conflito e not-found não são repetidos.
4. Conexão, resolução, timeout, 429 e 502/503/504 podem ser repetidos somente dentro
   de `max_attempts`, deadline global e teto de backoff.
5. `Retry-After` é respeitado somente até o teto local; nunca prolonga o deadline.
6. Ao esgotar, preserve erro seguro; não fabrique resposta nem marque job concluído.
7. Para rollback, reverta manifesto, settings, `.env.example`, código e testes no
   mesmo commit. Não altere apenas um lado da policy.

O jitter é determinístico em testes por injeção da fonte aleatória. Cancelamento
cooperativo não interrompe uma chamada síncrona em andamento; R-038 permanece aberto.
