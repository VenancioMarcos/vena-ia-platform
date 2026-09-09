# CTO-CODEX-CAM-008 — Orquestração sintética E2E

**Data:** 2026-09-09
**Estado:** CAM-008A concluída localmente, com ressalvas de escopo sintético; validação PASS.
**Base:** f55534a, CAM-007A aprovada tecnicamente no escopo por relatório;
514 passed/2 skipped, Ruff/mypy PASS em 191 fontes.

## Objetivo

Unir extrator CAD, planejador sintético e verificador de fronteiras declaradas
em função interna isolada, com resultado auditável e nenhuma autoridade física.

## Escopo

Função orchestrate_synthetic_turning_pipeline e resultado estrito por estágio.
Sem endpoints, persistência, fresamento, NC, G9, publicação ou deploy.

## Refinamento prévio enviado ao CTO

Fator BRep limitado às unidades suportadas mm/m/in, tolerâncias explícitas e
exclusion_zones obrigatório. Timestamp UTC fornecido pelo chamador preserva
pureza/replay, sem alegação de relógio confiável. Modelo imutável de metadados
substitui dict mutável: versões, hashes de parâmetros e serialização BRep real,
sem inventar hash do STEP original ou identidade geométrica canônica.
Falhas por estágio interrompem etapas seguintes; NOT_EVALUATED não é sucesso.

## Arquivos criados

- apps/api/app/modules/engineering/turning_service.py: orquestrador interno.
- apps/api/tests/modules/engineering/test_turning_pipeline_e2e.py: 34 testes E2E.
- Este registro de entrega.

## Arquivos modificados

- turning_toolpath_schemas.py: metadados e resultado estritos.
- ADR-0037/DEC-047, CONTEXT, CHANGELOG e documentos de estado CTO.
- CTO-CODEX-CAM-007.md: parecer recebido da entrega anterior.

## Testes realizados

34 testes E2E passed em 3.63 s. Ruff PASS; mypy PASS em 192 fontes.
Suíte API completa: 548 passed (=514+34), 2 skipped em 122.35 s, zero falhas.
Perfis extraídos de STEP canônico/escalonado; CAD negativo chave/prisma, stock
insuficiente, chuck colidente, plano vazio, unidades m/in reais transformadas,
escalas inválidas inclusive NaN/Inf, timestamps sem UTC e contratos forjados.
Falhas injetadas de serialização/CAD/planner/verificador têm status correspondente
sem vazar diagnóstico nativo. Replay inclui resultado JSON inteiro e BRep original
preservado; alterar tempo/fixture muda hash de parâmetros, outra geometria muda
hash BRep. Resultado bloqueia autoridade, ausência de artefatos e profile_id trocado.
Uma asserção inicial usou nome incorreto do reason code de stock; corrigida para
STOCK_DOES_NOT_CONTAIN_FINISHED_ENVELOPE, sem mudar o contrato existente.

## Critérios de aceitação

E2E cilindro/escalonado; negativos CAD/stock/chuck; autoridade false em todos
os resultados. Metadados coerentes, imutáveis, determinísticos no escopo declarado.

## Próximos passos

Aguardar resposta técnica, documentar o contrato definitivo, implementar/testar,
commit local, enviar relatório e pedir/aguardar próxima ordem.
NON_PRODUCTION; G9=PENDING_AUTHORITATIVE_REVIEW; PHYSICAL_USE_AUTHORIZED=false.

## Decisão recebida

Ajustes confirmados na íntegra; CAM-008 substituída por CAM-008A. Commit:
feat(engineering): implement deterministic synthetic turning E2E orchestrator.

## Contratos e implementação

_Inputs estrito valida os parâmetros antes do pipeline. Datum é revalidado por
conteúdo porque seu schema mínimo anterior não revalida instâncias. Escala exige
float/int numérico estrito (sem bool/string), mapeando somente 1.0/1000.0/25.4.
Outro valor, incluindo NaN/Inf, gera CAD_EXTRACTION_FAILED e nenhum estágio CAD/CAM.
Contratos inválidos de demais parâmetros rejeitam por ValidationError; não se
converte ausência de contexto ou modelo forjado em sucesso.

Canonicalização JSON ordenada/compacta, allow_nan=false, inclui todos os parâmetros
validados, tolerâncias, datum, stock, params, fixture, AABB, zonas, timestamp e
schema_version. Escala não finita tem tag textual explícita NaN/+Infinity/-Infinity
para registrar a falha, sem JSON NaN ou conversão silenciosa para null.
Hash de parâmetros e hash BRep são separados; não alegar que o primeiro inclui
a geometria. Mudança de timestamp é mudança de entrada e muda aquele digest.

BRep é copiado antes de serializar e extrair. BRepTools.Write_s em BytesIO com
formato ASCII V3, sem triangulação/normais; SHA256 calculado no payload real.
Metadados registram versão do binding cadquery-ocp. Limite 512 faces antes da
cópia e 20 MB de serialização (checado após gerar bytes); não há preempção de
kernel nativo nem garantia de identidade geométrica canônica entre serializações.
Timestamp é declaração UTC do chamador, sem chamada interna de relógio. Arquivo
STEP original não é entrada desta função: nenhum digest/proveniência STEP inventado.

Falha de serialização => CAD_EXTRACTION_FAILED, digest ausente. Falha de extração
preserva digest, sem profile/plan/verification. Falha de planejamento preserva
profile, sem plan/verification. Falha/NOT_EVALUATED da verificação preserva plano
e relatório se existente. Exceções de cada estágio são convertidas para reason
code fixo, sem detalhes nativos; exceções de planejamento conhecidas preservam
seu reason code. Só retorna SUCCESS_SYNTHETIC com relatório PASS efetivo.

SyntheticTurningMetadata e SyntheticTurningExecutionResult estritos e imutáveis;
validação cruza status/artefatos, profile_id do plano com conteúdo do perfil e
índices do relatório com movimentos reais. Plano vazio não admite sucesso.
Schema synthetic-turning/v1 cobre este contrato inicial; não versiona/assina os
componentes do Digital Thread existente. Metadados são evidência local de replay,
não garantia criptográfica de revisão, autenticidade ou aprovação humana.

is_physical_ready/physical_use_authorized/executable_output=false;
emission_status=CONTROLLER_PROFILE_UNRESOLVED; relatório/plan continuam com
colisão NOT_VALIDATED e limitações de stock/ferramenta/fixação reais. Sem endpoints,
persistência, migrações, pós, runtime, fresamento ou alteração de gates/G9.

## Validação final e entrega

548 passed/2 skipped em 122.35 s; 34 E2E passed em 3.63 s; Ruff PASS;
mypy PASS em 192 fontes; git diff --cached --check PASS; 5 links relativos PASS.
Skips Redis real auth/jobs inalterados; sem resumo de warnings. Python 3.14.6
local experimental; sem novo CI remoto. Nenhum código alterado após a suíte.
Log local ignorado: .pytest_cache/cam008a-pytest.log.

Critérios cumpridos para o orquestrador sintético interno e metadados delimitados.
Próximos passos: commit local, enviar relatório, pedir parecer/próxima ordem e
aguardar resposta real. Nenhum push/merge/tag, endpoint, NC ou autoridade física.
