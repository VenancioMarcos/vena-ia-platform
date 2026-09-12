# CTO-CODEX-AUTO-018 — Reverificação de raios quantizados

**Data:** 2026-09-09
**Estado:** implementação validada; commit/envio como próximos passos.
**Base:** 6d4665a, AUTO-017 aprovada por relatório pelo Gemini.

## Objetivo e escopo

Função pura reconstrói raios dos extremos com AUTO-015, mantém Z exatamente,
IDs/tipos/ordem/contagens e recalcula comprimento de corte. Revalidar plano e
precisão antes de executar. Movimento que colapse a comprimento zero é rejeitado,
sem eliminar/mesclar movimentos silenciosamente. profile_id continua referência
ao perfil nominal original; não identifica conteúdo do plano reconstruído.
Wrapper retorna plano reconstruído e verificação contínua das mesmas zonas/fixture/
envelope explicitamente fornecidos. Reutiliza verificador de fronteiras declarado,
não modifica schema do sumário numérico (false/NOT_EVALUATED). Não integra ainda
o novo wrapper ao orquestrador. PASS não é autoridade física nem segurança NC.

## Arquivos previstos

turning_quantization.py; testes dedicados de reconstrução/reverificação;
ADR0037/DEC047, CONTEXT/CHANGELOG e registros CTO.

## Testes e critérios

16 testes novos passed em 0.57 s: original PASS/quantizado PASS e original
PASS/quantizado interferência no meio do segmento para três tipos; IDs/Z/corte/flags,
vazio, precisão inválida, movimentos colapsados, revalidação e castanhas.
Regressão completa 646 passed (=630+16), 2 skipped, zero falhas em 118.55 s.
Redis real auth/jobs ignorados como antes. Ruff PASS; mypy PASS193 fontes;
7 links/fences e diff PASS. Python3.14.6 experimental, sem CI remoto novo.
Log ignorado .pytest_cache/auto018-pytest.log.
Tangência na fronteira fechada é violação; exemplo original passa com folga,
quantização desloca contra zona. Não quantizar Z ou inferir dados físicos.

## Próximos passos

Commit local, relatório com SHA real ao CTO e aguardar próxima ordem.
NON_PRODUCTION; G9=PENDING_AUTHORITATIVE_REVIEW; PHYSICAL_USE_AUTHORIZED=false;
CONTROLLER_PROFILE_UNRESOLVED; sem Git de rede.

## Parecer e continuidade

Commit c28405d7f2af941c46c5123ce0480386b7e08ab1 enviado com árvore limpa;
aprovado pelo Gemini por relatório. AUTO-019 recebida; ajuste de distinção de
falha de reconstrução acolhido pelo CTO e substituído por AUTO-019A.
