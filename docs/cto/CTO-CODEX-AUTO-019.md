# CTO-CODEX-AUTO-019A — Quinto estágio sintético

**Data:** 2026-09-09
**Base:** c28405d; AUTO-018 aprovada por relatório.
**Estado:** ajuste acolhido antes da implementação; entrega validada.
**Conclusão da validação:** 2026-09-10.

## Objetivo e escopo

Integrar reverificação radial como quinto estágio sob synthetic-turning/v3.
AUTO-019 substituída por AUTO-019A: colapso/exceção não é colisão detectada.
QUANTIZED_VERIFICATION_FAILED preserva quatro artefatos/digest da quantização,
sem plano/relatório quantizados; reason fixo. Violação real preserva seis artefatos
com relatório não-PASS e índices reais; SUCCESS exige PASS em ambos relatórios.
Hash SHA256 do relatório quantizado em sucesso e violação; validar correspondência
R reconstruído/Z nominal/IDs/tipos/contagens entre plano/sumário/plano quantizado.
Não quantizar Z, emitir NC ou conferir autoridade física. Hash não é assinatura.

## Arquivos previstos

turning_toolpath_schemas.py, turning_service.py, testes E2E; ADR0037/DEC047,
CONTEXT/CHANGELOG e registros CTO de continuidade.

## Testes e critérios

62 testes E2E passed em 5.05 s (12 novos): fixtures positivas; zona radial
26.5004..26.5006 e allowance0.50026 induzem violação real após quantização;
allowance9.99999 e clearance0.00001 induzem colapso real do planner.
Primeiro cenário de colapso mantinha clearance1.0 e não colapsava; ajustados
apenas parâmetros do teste, sem alterar planner. Exceções e forjas cobertas.
Regressão completa: 658 passed (=646+12), 2 skipped, zero falhas em 128.60 s.
Redis real auth/jobs ignorados como antes. Ruff PASS; mypy PASS193 fontes;
7 links/fences e diff PASS. Python3.14.6 experimental, sem CI remoto novo.
Log ignorado .pytest_cache/auto019-pytest.log.

## Próximos passos

Commit local, relatório com SHA real e aguardar próxima ordem real.
NON_PRODUCTION; G9=PENDING_AUTHORITATIVE_REVIEW; PHYSICAL_USE_AUTHORIZED=false;
CONTROLLER_PROFILE_UNRESOLVED; sem Git de rede.
