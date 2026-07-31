# Smoke test manual — v1.0

1. Execute a instalação de `docs/INSTALLATION.md` e confirme `/health` com
   `status=ok` e `version=1.0.0`.
2. Crie conta, faça login, crie projeto e atualize a página.
3. Envie PDF textual pequeno, processe e indexe.
4. Pergunte algo presente no PDF; confirme resposta e fonte por página/chunk.
5. Atualize a página; confirme histórico na ordem usuário/assistente.
6. Gere e reabra relatório `DRAFT_REQUIRES_HUMAN_REVIEW`.
7. Faça logout e confirme redirecionamento/401.
8. Com outra conta, tente URLs do projeto, documento, chat e relatório; espere
   `404` seguro.
9. Confirme que nenhum fluxo gera G-code ou transmite dados a máquina.

O equivalente automatizado está em `apps/api/tests/test_mvp_e2e.py` e usa storage,
extração e provider determinísticos sem credencial ou API paga.
