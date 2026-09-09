# CTO-CODEX-AUTO-017 — Quantização no orquestrador

**Data:** 2026-09-09
**Estado:** implementação validada; commit/envio como próximos passos.
**Base:** 770ac7b; AUTO-016 aprovada pelo Gemini por relatório.

## Objetivo e escopo

Quarto estágio numérico depois de fronteiras declaradas PASS. Precisão estrita
1..6 com default3 sintético, incluída no digest canônico dos parâmetros.
Resultado SUCCESS exige perfil/plano/verificação/quantização; falhas anteriores
não carregam quantização nem digest. QUANTIZATION_FAILED preserva três artefatos
anteriores com fronteiras PASS, mas não sumário parcial. Reason fixo sem detalhes.

Metadata registra precisão e SHA256 do JSON canônico do sumário. Resultado
confere esse hash, precisão, contagem e raios originais na sequência start/end
contra o plano. Hash prova consistência de conteúdo, não fonte/autenticidade.
Contrato passa a synthetic-turning/v2 porque SUCCESS agora exige quarto estágio;
runtime API permanece 3.1.0, sem migração nem leitura automática de v1 como v2.
Não há reverificação de fronteiras quantizadas, quantização de Z, prova física,
NC ou integração Digital Thread. Sucesso numérico não altera G9/autoridade.

## Arquivos previstos

turning_service.py, turning_toolpath_schemas.py, test_turning_pipeline_e2e.py,
ADR0037/DEC047, CONTEXT/CHANGELOG e documentos de continuidade CTO.

## Testes e critérios

50 testes E2E passed em 4.11 s (16 novos): casos anteriores ampliados,
precisão/hash/replay, falha de quantização, artefatos ausentes/forjados e
não execução após falha anterior. Suíte completa 630 passed (=614+16),
2 skipped, zero falhas em 137.10 s. Redis real auth/jobs ignorados como antes.
Ruff PASS; mypy PASS193 fontes; 7 links/fences e diff PASS. Python3.14.6
experimental; sem novo CI remoto. Log ignorado .pytest_cache/auto017-pytest.log.
Uma linha vazia excedente no EOF foi removida, sem alteração funcional.

## Próximos passos

Commit local, relatório com SHA real ao CTO e aguardar próxima ordem.
NON_PRODUCTION; G9=PENDING_AUTHORITATIVE_REVIEW; PHYSICAL_USE_AUTHORIZED=false;
CONTROLLER_PROFILE_UNRESOLVED; sem Git de rede.
