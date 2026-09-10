# Torneamento sintético alpha — Dossiê técnico local

**Data:** 2026-09-10
**Marco documental:** v3.2.0-turning-synthetic-alpha — NON_PRODUCTION.
**Base de código:** 84492a5548d1911ccada07dc512d3e700e7075b2.
**Branch:** codex/v3.1-first-controlled-test-path.
**Contrato de resultado:** synthetic-turning/v3; API/manifests 3.1.0.

## Finalidade e alcance

Consolidar evidências da cadeia interna determinística de torneamento sintético.
Este marco é documentação local: nenhuma tag, release, publicação ou implantação.
Pareceres do Gemini foram baseados nos relatórios do executor, sem revisão
independente do diff ou ensaio em máquina. Não existe pós-processador industrial
ou Fanuc homologado, nem emissão NC de torneamento nesta cadeia.

O fluxo histórico de fresamento 3 eixos/2.5D possui candidatos controlados de
revisão registrados no repositório; isso não autoriza máquina e não implica
emissor de torno. As ilustrações externas do Gemini são conceituais, não telas
executadas ou prova de funcionalidades. SHA de commit Git não é SHA256 de programa.
Um hash de payload também não é assinatura, homologação ou autoridade humana.

## Arquitetura dos cinco estágios

| Estágio | Entrada e cálculo | Saída e limite |
| --- | --- | --- |
| 1. CAD B-Rep | OCCT, unidade/datum/tolerâncias explícitos; eixos analíticos e reconstrução booleana do envelope externo cilíndrico | Perfil RZ aberto para cilindro/escalonado; cone, furos/chaveta/prisma fora do domínio |
| 2. Planejamento 2D | Perfil, stock e parâmetros declarados; passes lineares de faceamento e cilindramento | Plano de ponto ideal, sem ferramenta física, F numérico ou remoção material |
| 3. Fronteiras nominais | Segmentos contínuos contra plano axial e retângulos expandidos pelo AABB local (Minkowski) | PASS apenas das fronteiras declaradas; todos os tipos e contato fechado avaliados |
| 4. Quantização numérica | R para X=2R binário exato; Decimal ROUND_HALF_UP local; precisão1..6 | Dois relatórios por movimento, extremos assinados; Z ainda original, NOT_EVALUATED para fronteiras no sumário |
| 5. Reverificação radial | Plano com R reconstruído de X/2 e Z original; mesmo verificador contínuo | Detecta violação introduzida por quantização; colapso de segmento é falha, sem exclusão silenciosa |

A função pública interna é orchestrate_synthetic_turning_pipeline em
apps/api/app/modules/engineering/turning_service.py. Nenhum endpoint, persistência,
Digital Thread oficial ou interface de máquina foi adicionado por esta cadeia.
A serialização BRep versionada tem hash próprio, separado dos parâmetros. Não é
identidade geométrica canônica nem digest do STEP original. Timestamp UTC é
entrada declarada, não horário atestado. JSON canônico vincula parâmetros e
precisão; hashes do sumário e relatório conferem apenas consistência do conteúdo.

## Matriz de estados e artefatos

| Estado | Artefatos preservados | Significado |
| --- | --- | --- |
| CAD_EXTRACTION_FAILED | Metadata; nenhum dos seis artefatos geométricos | Unidade/geometria/serialização rejeitada; hash só se realmente produzido |
| PLANNING_FAILED | Perfil | Planejamento rejeitado após extração |
| BOUNDARY_VERIFICATION_FAILED | Perfil, plano, relatório nominal se disponível | Violação nominal, não avaliação ou exceção; sem quantização |
| QUANTIZATION_FAILED | Perfil, plano e relatório nominal PASS | Não existe sumário numérico válido |
| QUANTIZED_VERIFICATION_FAILED | Quatro anteriores incluindo sumário | Reconstrução/verificação falhou; nenhum plano/relatório quantizado inventado |
| QUANTIZED_BOUNDARY_VIOLATION | Seis artefatos e hashes dos relatórios disponíveis | Relatório real de interferência após reconstrução radial |
| SUCCESS_SYNTHETIC | Perfil, plano, relatório nominal, sumário, plano reconstruído e relatório quantizado | Ambos os relatórios de fronteiras PASS no domínio sintético declarado |

Campos quantizados existentes exigem correspondência de IDs/operações/contagens,
tipos de movimento/avanço, R reconstruído e Z nominal; índices e hashes coerentes.
A validação do schema não recomputa a política de quantização ou substitui o
verificador; conteúdo coerente não comprova origem/autenticidade de entradas.

## Limites obrigatórios

| Controle | Estado |
| --- | --- |
| PHYSICAL_USE_AUTHORIZED | false |
| G9 | PENDING_AUTHORITATIVE_REVIEW |
| NO_HUMAN_REVIEW_BYPASS | true |
| Emissão de torno | CONTROLLER_PROFILE_UNRESOLVED |
| MACHINE_SEND / DNC / NC_TRANSFER / CYCLE_START | false |
| is_verified / is_collision_free / executable_output | false |
| collision_status | NOT_VALIDATED |
| Quantização axial Z | Não implementada |
| Material remanescente / ferramenta / fixação físicos | Não validados |
| Git de rede / merge / tag / release / deploy nesta sequência | Não executados |

Limites computacionais: até512 faces CAD na checagem, 1000 passes, 10000
movimentos/20000 relatórios, 128 zonas e200000 pares de verificação. BRep máximo
20MB verificado após serialização; kernel nativo não possui preempção. Limites
computacionais não são limites operacionais de máquina. AABB e stock declarados
não demonstram ferramenta real nem volume de material remanescente.

## Inventário dos 17 commits locais anteriores à consolidação

Referência histórica d798417, sem nova consulta remota. São commits, não 17
estágios do pipeline. O commit documental desta missão será o décimo oitavo.

| Ordem | Commit | Mensagem Git exata |
| --- | --- | --- |
| 1 | 052cb8e | fix(cad): accept whitespace in STEP units |
| 2 | 08569ff | fix(engineering): ensure strict compatibility check and harden gitignore |
| 3 | b86f51e | docs(cto): record fix approval and next specification mission |
| 4 | 9b5a83b | docs(turning): propose architecture and contracts for 2-axis turning foundation |
| 5 | b5b04b7 | feat(turning): implement ADR-0037 turning schemas and axisymmetry validator |
| 6 | 57a0fcf | feat(cad): implement turning profile extractor and synthetic STEP fixtures |
| 7 | d3785d3 | feat(cam): implement synthetic 2D linear turning planner and schemas |
| 8 | f55534a | feat(cam): implement synthetic boundary and exclusion zone verifier |
| 9 | 5f50559 | feat(engineering): implement deterministic synthetic turning E2E orchestrator |
| 10 | f3fb048 | docs(turning): document controller prerequisites and postprocessor gap matrix |
| 11 | dc75997 | chore(release): consolidate v3.2.0-turning-synthetic-alpha baseline and documentation |
| 12 | 70e4d13 | feat(cam): add numerical quantization check schema contracts |
| 13 | ebbe37e | feat(cam): implement diameter quantization mathematical evaluator |
| 14 | 770ac7b | feat(cam): implement toolpath plan diameter quantization evaluator |
| 15 | 6d4665a | feat(engineering): integrate plan diameter quantization into E2E orchestrator |
| 16 | c28405d | feat(cam): implement boundary reverification for quantized toolpath plans |
| 17 | 84492a5 | feat(engineering): integrate robust quantized boundary verification into E2E pipeline |

## Evidências de teste

Base AUTO019A: 658 passed, 2 skipped em128.60s; 62 E2E em5.05s. Ruff PASS e
mypy PASS193 fontes. Regressão da consolidação: 658 passed, 2 skipped, zero falhas em161.38s. Skips exigem Redis
real descartável em auth/jobs; Python local3.14.6 experimental, sem CI remoto novo.

Exemplos reproduzíveis: fixtures STEP cilíndrica/escalonada positivas; chaveta e
prisma rejeitados; planos nominais aprovados que passam a interferir em faixa
radial após arredondamento; segmento curto colapsado retorna falha de reconstrução,
sem inventar colisão. Revalidação profunda rejeita adulteração por model_copy;
replay confere JSON e hashes com entradas/timestamp/binding iguais.

## Pré-requisitos para evolução

Ver [matriz de controlador e pós](../../engineering/TURNING_CONTROLLER_PREREQUISITES.md)
e [ADR0037](../../adr/ADR-0037-turning-geometry-and-toolpath-foundation.md).
Faltam máquina/comando/versão/manual/sistema de códigos aplicáveis; ferramenta,
offset/compensação, setup/material remanescente; parâmetros reais de corte e
trajetórias de aproximação/troca/saída; precisão de todos os eixos e reverificação
da saída textual exata. Nenhum valor ou autorização pode ser inferido do PASS.
Publicação exige autorização própria; operação física exige revisão humana e
evidências externas. O fechamento documental não concede essas autorizações.
