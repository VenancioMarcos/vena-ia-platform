# Runbook — capacidade sintética controlada

Contrato: `vena-ia.capacity-profile/v1` em `capacity-profile.json`.

1. Execute `python scripts/capacity_policy.py`.
2. Execute os testes focais de capacidade e o E2E autenticado.
3. Gere evidência fora do repositório com `python scripts/capacity_harness.py
   --output ../capacity-evidence.json --commit <sha>`.
4. Confirme `GUARDRAIL_RESULT=PASS`, checksum e cleanup.
5. Compare cenários separadamente; não agregue leitura, upload, IA, worker e backup.
6. Se houver saturação, preserve rejeição bounded e meça recuperação antes de elevar limite.
7. Nunca apresente os resultados como capacidade produtiva, SLA, SLO ou piloto aprovado.

O perfil usa duas APIs lógicas e dois workers controlados, provider determinístico,
dados sintéticos, carga pequena e soak de 3 segundos. O workflow é limitado a dez
minutos e usa serviços fixados. Execuções longas permanecem manuais e autorizadas.
