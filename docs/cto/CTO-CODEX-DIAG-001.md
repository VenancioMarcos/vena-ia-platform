# RELATÓRIO TÉCNICO — CTO-CODEX-DIAG-001

Data: 2026-09-08. Executor: Codex. Estado: diagnóstico concluído com ressalvas (AR, usado aqui como conclusão com ressalvas; a ordem não define a legenda).
Autorização: ordem recuperada do Gemini e execução confirmada pelo proprietário nesta tarefa.

## Objetivo
Inspecionar Git local/remoto, privacidade, qualidade da linha v3.1 e maturidade de torneamento, sem implementar código de produção.

## Escopo
Diagnóstico local, consultas remotas somente de leitura, testes existentes e documentação. Sem push, merge, tag, release, deploy, mudança de visibilidade ou máquina. Referências: PROJECT.md §19, AGENTS.md, .ai/ACP.md, GOVERNANCE.md, SECURITY.md, DEC-039–046 e ADR-0036.

## 1. Evidências Git
- Árvore inicial limpa; branch `codex/v3.1-first-controlled-test-path`.
- HEAD: `052cb8ecf40b7ceb9cbc7346d9eadb579e488db6`.
- Remoto consultado diretamente: `main=64ac3b82eaa9dea98e2341809cf608dec4ac63ba`; branch da PR=`d798417c11b2ce4f751d81cf1252250ed20fd030`.
- Um commit local pendente de push; nenhuma sincronização de escrita realizada.
- PR #31: OPEN, Draft, MERGEABLE. Backend CI, Frontend CI e Runtime Policy CI SUCCESS no head remoto d798417, em 2026-08-15. Esses checks NÃO validam 052cb8e.
- Commit 052cb8e: 5 arquivos, 101 inserções, 9 remoções: CHANGELOG.md, CONTEXT.md, apps/api/app/modules/cad/parser.py, apps/api/tests/test_cad.py, docs/FIRST_CONTROLLED_CAD_TO_GCODE_TEST.md.
- Diff de código revisado: substitui busca textual rígida por regex tolerantes a whitespace em SI_UNIT e INCH; adiciona regressão de unidade mm. Não implementa torneamento.
- Comparação origin/main..HEAD: 16 arquivos, 908 inserções e 23 remoções.
- Consulta de rede restrita falhou inicialmente; repetição somente de leitura com acesso permitido confirmou GitHub e hashes. Não há bloqueio de autenticação demonstrado nesta auditoria.

## 2. Auditoria de privacidade
- GitHub retornou `visibility=PUBLIC`, `isPrivate=false`. A intenção de privacidade do proprietário não está atendida pela configuração atual. Nenhuma alteração de visibilidade foi executada.
- .gitignore protege .env, .env.*, caches Python, logs, builds, node_modules, .pnpm-store e backups com padrões específicos. .env.example é exceção intencional.
- `git check-ignore` confirmou .env e .env.local. Não protege genericamente *.key, *.pem, *.cert, *.local, outputs/ e temp/. STEP temporário também não tem regra específica.
- Nenhum .key/.pem/.cert/.local/.step/.stp/.nc rastreado foi encontrado. A busca ampla por nomes retornou .env.example e arquivos legítimos de implementação/documentação; nome contendo token/env não é evidência de segredo.
- Varredura de 226 commits alcançáveis e 1828 blobs únicos: zero ocorrências nas assinaturas de chave privada, token GitHub, token OpenAI e access key AWS verificadas. Único candidato por caminho sensível no índice: .env.example.
- Limitação: busca por assinaturas NÃO prova ausência de senhas arbitrárias, dados pessoais, propriedade intelectual, objetos inalcançáveis ou cópias externas. Não é possível certificar “nenhum segredo em todo o histórico”.
- Recomenda-se adicionar proteções específicas com exceções revisadas para exemplos/fixtures; não ignorar todos os STEP indiscriminadamente, pois um corpus autorizado pode precisar de versionamento.
- `git status --ignored` concluiu com avisos Windows de caminhos longos na .pnpm-store. A enumeração do índice e dos objetos Git não depende dessa travessia e concluiu.
- A afirmação anterior do CTO de main em 4a2f7f5/5 commits está desatualizada frente à consulta direta. GitHub confirma main em 64ac3b8; histórico local alcançável contém 226 commits.

## 3. Resultados de testes e qualidade
- Runtime local existente: Python 3.14.6, experimental segundo runtime-policy.json. CI oficial usa 3.13.11.
- `.venv/Scripts/python.exe -m ruff check .`: PASS.
- `.venv/Scripts/python.exe -m mypy apps/api/app packages/ai scripts`: PASS, 185 arquivos. Escopo equivalente ao workflow oficial, em vez de mypy indiscriminado sobre testes.
- Pytest API: **399 passed, 2 skipped, 0 failed, 0 errors em 258.95 s (4m18s)**, 401 itens coletados. Sem resumo de warnings emitido. Skips: test_auth_security_store.py:126 (integração Redis real não habilitada) e test_jobs.py:441 (requer Redis descartável). Não comprova as integrações Redis reais nem substitui CI em Python 3.13.11.
- Testes usam SQLite em memória e dependências substituídas conforme conftest.py. Nenhuma migration ou alteração de dados persistentes foi executada.

## 4. Análise de lacunas para torneamento
| Camada / referência em HEAD | Implementação observada | Limite |
|---|---|---|
| cad/parser.py:40–114, StepTextParser | Metadados, entidades, pontos e unidade STEP | Não extrai perfil de torno |
| cad/evidence.py:263–357, GeometryEvidenceBuilder._collect; :418 | Classifica faces CYLINDER/CONE/TORUS via OCCT e registra direção axis_x/y/z | Eixos locais de superfícies não provam eixo comum de revolução do sólido nem geratriz |
| cad/features.py:132–199, FeatureRecognizer.recognize | Cilindro: eixo, posição, raio, diâmetro e extensão; regra conservadora de furo passante | Não reconhece uma peça inteira como torneável nem extrai perfil XZ |
| engineering/service.py:169–286, EngineeringCatalogService.recommend | Aceita string turning e calcula parâmetros/tempo/custo reais | Reutiliza fórmula com diâmetro da ferramenta, dentes e avanço por dente; não é algoritmo específico de torno |
| engineering/manufacturing_schemas.py:12–39 | Stock por bounds e intent Literal milling/drilling | Não há contrato de intent turning ou tarugo/perfil de torno |
| engineering/toolpath_schemas.py:12–28 | ToolGeometry: diâmetro, flute_length, holder_diameter; pontos XYZ e avanço mm/min | Ausentes raio de ponta/orientação ISO/quadrante e convenção X de torno |
| engineering/toolpath.py:105–181 | Trajetória linear bounded 3 eixos/2.5D | Exclui turning explicitamente |
| engineering/postprocessor.py:18–81 | Subconjunto G0/G1/G17/G21/G90/G94/M30, XYZ | Sem G18, G70/G71, G95/G96/G97, spindle/ciclos de torno ou modo X raio/diâmetro |

Caminhos acima são relativos a apps/api/app/modules/. São implementações reais de geometria e cálculos genéricos, não stubs de um CAM de torno. Não foi localizado pipeline algorítmico específico de torneamento em apps/packages/services. A presença de raio e diâmetro geométricos não é convenção de programação de eixo X.

### Achado funcional adicional — compatibilidade
`engineering/service.py:212` usa `compatibility.endswith("COMPATIBLE")`. A string INCOMPATIBLE também satisfaz essa condição.
Reprodução isolada, sem banco/máquina e sem alteração de código: seleção sintética com máquina/ferramenta permitindo apenas milling e request turning retornou INCOMPATIBLE, mas spindle_speed AVAILABLE=3000 rpm, feed_rate AVAILABLE=600 mm/min e machining_time AVAILABLE=0.167 min.
Trata-se de parâmetro preliminar incoerente, não de autorização física. Recomenda-se correção focada e regressão que exija indisponibilidade de parâmetros derivados quando incompatível, antes de expandir engenharia. Nenhuma correção foi aplicada nesta missão diagnóstica.

## 5. Bloqueios e recomendações
1. Resolver a decisão de privacidade antes de qualquer push; consulta confirma PUBLIC. Mudar visibilidade não apaga cópias que eventualmente já existam.
2. Corrigir o predicado de compatibilidade e revisar os cálculos genéricos antes de usá-los para turning.
3. Endurecer .gitignore com padrões e exceções explícitos.
4. Submeter 052cb8e ao CI oficial somente quando houver autorização de push; CI remoto atual é do commit anterior.
5. Definir futura missão de reconhecimento de sólido de revolução/perfil, com rejeição de geometrias não suportadas, antes de planejar G-code de torno. Não fixar comando Fanuc, modo diâmetro ou ferramenta CNMG como decisão aprovada por inferência.
6. CONTEXT.md contém registros históricos contraditórios (backend 1.8 e “kernel não implementado” coexistindo com v3.1). Recomenda-se saneamento documental específico, preservando histórico.

## Arquivos criados
- docs/cto/CTO-CODEX-DIAG-001.md (este relatório).
- Auxiliar e JSON de varredura em .pytest_cache/, ignorados e sem valores de segredos.

## Arquivos modificados
- CONTEXT.md: passagem de contexto ao término da missão.

## Critérios de aceitação
Git e remoto verificados; escopo de varredura e seus limites declarados; mapeamento com referências e reprodução do achado realizado. Pytest concluído e registrado. A garantia absoluta de ausência de segredos é deliberadamente não emitida; as limitações da auditoria estão explícitas. Nenhum código de produção foi alterado.

## Próximos passos / handoff ACP
Enviar resultado ao Gemini CTO conforme autorização do proprietário, solicitar próxima ordem e aguardar resposta. Nenhuma decisão arquitetural nova foi tomada.
G9=PENDING_AUTHORITATIVE_REVIEW; PHYSICAL_USE_AUTHORIZED=FALSE; MACHINE_SEND=DNC=NC_TRANSFER=CYCLE_START=FALSE.

## Apêndice — saídas Git literais da auditoria

Captura após criação do relatório; por isso o próprio documento aparece como não rastreado. Árvore inicial estava limpa.

### git status

```text
On branch codex/v3.1-first-controlled-test-path
Your branch is ahead of 'origin/codex/v3.1-first-controlled-test-path' by 1 commit.
  (use "git push" to publish your local commits)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	docs/cto/CTO-CODEX-DIAG-001.md

nothing added to commit but untracked files present (use "git add" to track)
```

### git branch -avv

```text
  codex/cad-to-gcode-gap-analysis                             ce6bd08 [origin/codex/cad-to-gcode-gap-analysis] docs(cad): map controlled gcode validation gap
  codex/roadmap-v2-consolidation                              6d49d88 [origin/codex/roadmap-v2-consolidation] docs: record roadmap pull request
  codex/v1.2-auth-rate-limiting                               acb10dc [origin/codex/v1.2-auth-rate-limiting] chore: prepare v1.2.0 release
  codex/v1.3-backup-recovery                                  7043985 [origin/codex/v1.3-backup-recovery] chore: prepare v1.3.0 release
  codex/v1.4-observability-auditability                       94901fe [origin/codex/v1.4-observability-auditability] chore: prepare v1.4.0 release
  codex/v1.5-asynchronous-processing                          6ff915b [origin/codex/v1.5-asynchronous-processing] chore(release): prepare v1.5.0
  codex/v1.6-reliability-scalability                          0592572 [origin/codex/v1.6-reliability-scalability] chore(capacity): finalize worker recovery evidence
  codex/v1.7-intelligent-engineering                          ac822d0 [origin/codex/v1.7-intelligent-engineering] chore(release): prepare v1.7.0
  codex/v1.8-cad-interoperability                             fffa79e [origin/codex/v1.8-cad-interoperability] chore(release): prepare v1.8.0 candidate
  codex/v1.9-controlled-pilot-readiness                       1184c6c [origin/codex/v1.9-controlled-pilot-readiness] docs(release): prepare v1.9.0 release candidate
  codex/v1.9-roadmap-decomposition                            00cc941 [origin/codex/v1.9-roadmap-decomposition] docs(v1.9): approve package baseline
  codex/v2.0-integrated-engineering-platform                  9f34e70 [origin/codex/v2.0-integrated-engineering-platform] docs(v2): finalize release candidate
  codex/v2.0-roadmap-decomposition                            6b8bdec [origin/codex/v2.0-roadmap-decomposition] docs(roadmap): approve v2.0 package 1
  codex/v2.1-enterprise-engineering-governance                691a378 [origin/codex/v2.1-enterprise-engineering-governance] chore(release): prepare v2.1.0 candidate
  codex/v2.2-general-geometry-evidence                        756c34c [origin/codex/v2.2-general-geometry-evidence] chore(release): prepare v2.2.0
  codex/v2.3-controlled-cad-gcode-validation                  7c9c242 [origin/codex/v2.3-controlled-cad-gcode-validation] chore(release): prepare v2.3.0
  codex/v3.0-manufacturing-digital-thread                     1e41ca4 [origin/codex/v3.0-manufacturing-digital-thread] feat(engineering): add manufacturing digital thread
  codex/v3.0-roadmap-extension                                44ebb35 [origin/codex/v3.0-roadmap-extension] docs(roadmap): approve v2.1 to v3.0 sequence
  codex/v3.1-controlled-test-environment                      c259349 [origin/codex/v3.1-controlled-test-environment] chore(release): prepare v3.1.0 non-production
* codex/v3.1-first-controlled-test-path                       052cb8e [origin/codex/v3.1-first-controlled-test-path: ahead 1] fix(cad): accept whitespace in STEP units
  feature/v0.3-ai-layer                                       21f6b92 [origin/feature/v0.3-ai-layer] fix(ci): expose monorepo packages to backend tests
  feature/v0.9-research-foundation                            5cbe39a [origin/feature/v0.9-research-foundation] docs(cto): record v0.9 validation
  main                                                        64ac3b8 [origin/main] Release v3.1.0 — Controlled CAD-to-G-code Test Environment
  release/v0.3.0-preparation                                  5d348e1 [origin/release/v0.3.0-preparation] chore(release): prepare v0.3.0
  release/v0.4.0                                              020f151 [origin/release/v0.4.0] chore(release): prepare v0.4.0
  release/v1.0.0-mvp                                          04bd11b [origin/release/v1.0.0-mvp] docs(cto): record v1.0 CI approval
  release/v1.1.0-stabilization                                4e13e28 [origin/release/v1.1.0-stabilization] chore: prepare v1.1.0 release
  security/v0.4.1-authentication-authorization                a871de5 [origin/security/v0.4.1-authentication-authorization] docs(status): record security gate draft PR readiness
  remotes/origin/HEAD                                         -> origin/main
  remotes/origin/codex/cad-to-gcode-gap-analysis              ce6bd08 docs(cad): map controlled gcode validation gap
  remotes/origin/codex/roadmap-v2-consolidation               6d49d88 docs: record roadmap pull request
  remotes/origin/codex/v1.2-auth-rate-limiting                acb10dc chore: prepare v1.2.0 release
  remotes/origin/codex/v1.3-backup-recovery                   7043985 chore: prepare v1.3.0 release
  remotes/origin/codex/v1.4-observability-auditability        94901fe chore: prepare v1.4.0 release
  remotes/origin/codex/v1.5-asynchronous-processing           6ff915b chore(release): prepare v1.5.0
  remotes/origin/codex/v1.6-reliability-scalability           0592572 chore(capacity): finalize worker recovery evidence
  remotes/origin/codex/v1.7-intelligent-engineering           ac822d0 chore(release): prepare v1.7.0
  remotes/origin/codex/v1.8-cad-interoperability              fffa79e chore(release): prepare v1.8.0 candidate
  remotes/origin/codex/v1.9-controlled-pilot-readiness        1184c6c docs(release): prepare v1.9.0 release candidate
  remotes/origin/codex/v1.9-roadmap-decomposition             00cc941 docs(v1.9): approve package baseline
  remotes/origin/codex/v2.0-integrated-engineering-platform   9f34e70 docs(v2): finalize release candidate
  remotes/origin/codex/v2.0-roadmap-decomposition             6b8bdec docs(roadmap): approve v2.0 package 1
  remotes/origin/codex/v2.1-enterprise-engineering-governance 691a378 chore(release): prepare v2.1.0 candidate
  remotes/origin/codex/v2.2-general-geometry-evidence         756c34c chore(release): prepare v2.2.0
  remotes/origin/codex/v2.3-controlled-cad-gcode-validation   7c9c242 chore(release): prepare v2.3.0
  remotes/origin/codex/v3.0-manufacturing-digital-thread      1e41ca4 feat(engineering): add manufacturing digital thread
  remotes/origin/codex/v3.0-roadmap-extension                 44ebb35 docs(roadmap): approve v2.1 to v3.0 sequence
  remotes/origin/codex/v3.1-controlled-test-environment       c259349 chore(release): prepare v3.1.0 non-production
  remotes/origin/codex/v3.1-first-controlled-test-path        d798417 docs(engineering): preserve TESTE_01 execution report
  remotes/origin/feature/v0.3-ai-layer                        21f6b92 fix(ci): expose monorepo packages to backend tests
  remotes/origin/feature/v0.9-research-foundation             5cbe39a docs(cto): record v0.9 validation
  remotes/origin/main                                         64ac3b8 Release v3.1.0 — Controlled CAD-to-G-code Test Environment
  remotes/origin/release/v0.3.0-preparation                   5d348e1 chore(release): prepare v0.3.0
  remotes/origin/release/v0.4.0                               020f151 chore(release): prepare v0.4.0
  remotes/origin/release/v1.0.0-mvp                           04bd11b docs(cto): record v1.0 CI approval
  remotes/origin/release/v1.1.0-stabilization                 4e13e28 chore: prepare v1.1.0 release
  remotes/origin/security/v0.4.1-authentication-authorization a871de5 docs(status): record security gate draft PR readiness
```

### git log -n 5 --oneline --decorate

```text
052cb8e (HEAD -> codex/v3.1-first-controlled-test-path) fix(cad): accept whitespace in STEP units
d798417 (origin/codex/v3.1-first-controlled-test-path) docs(engineering): preserve TESTE_01 execution report
6e38175 docs(engineering): record TESTE_01 completion
faf982b fix(web): allow controlled CAD validation runtime
02ed0a0 fix(runtime): load CAD kernel dependencies
```

### git show --stat 052cb8e

```text
commit 052cb8ecf40b7ceb9cbc7346d9eadb579e488db6
Author: Vena_IA Work <vena-ia@local>
Date:   Mon Aug 17 23:45:46 2026 -0300

    fix(cad): accept whitespace in STEP units

 CHANGELOG.md                               |  8 ++++
 CONTEXT.md                                 | 11 ++++++
 apps/api/app/modules/cad/parser.py         | 16 +++++---
 apps/api/tests/test_cad.py                 | 12 ++++++
 docs/FIRST_CONTROLLED_CAD_TO_GCODE_TEST.md | 63 ++++++++++++++++++++++++++++--
 5 files changed, 101 insertions(+), 9 deletions(-)
```

### git diff --stat origin/main..HEAD

```text
 CHANGELOG.md                                       |  41 ++++
 CONTEXT.md                                         |  46 +++-
 apps/api/Dockerfile                                |   5 +-
 apps/api/app/modules/cad/parser.py                 |  16 +-
 apps/api/app/modules/documents/service.py          |  22 +-
 apps/api/tests/test_cad.py                         |  12 +
 apps/api/tests/test_documents.py                   |  56 ++++-
 apps/api/tests/test_first_controlled_cad_path.py   | 211 ++++++++++++++++
 .../web/components/controlled-test-environment.tsx |  74 +++++-
 apps/web/lib/engineering-contracts.ts              |  69 +++++-
 apps/web/tests/e2e/controlled-environment.spec.ts  |  51 +++-
 docs/DECISIONS.md                                  |  19 ++
 docs/FIRST_CONTROLLED_CAD_TO_GCODE_TEST.md         | 269 +++++++++++++++++++++
 docs/RISK_REGISTER.md                              |   1 +
 docs/ROADMAP.md                                    |  10 +
 docs/cto/EXECUTION_STATUS.md                       |  29 +++
 16 files changed, 908 insertions(+), 23 deletions(-)
```

### git diff 052cb8e~1..052cb8e -- apps/api/app/modules/cad/parser.py apps/api/tests/test_cad.py

```text
diff --git a/apps/api/app/modules/cad/parser.py b/apps/api/app/modules/cad/parser.py
index 9273617..9343f0e 100644
--- a/apps/api/app/modules/cad/parser.py
+++ b/apps/api/app/modules/cad/parser.py
@@ -46,6 +46,11 @@ class StepTextParser:
     )
     _file_name = re.compile(r"FILE_NAME\s*\(\s*'([^']*)'", re.IGNORECASE)
     _schema = re.compile(r"FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'", re.IGNORECASE)
+    _millimetre = re.compile(
+        r"SI_UNIT\s*\(\s*\.MILLI\.\s*,\s*\.METRE\.\s*\)", re.IGNORECASE
+    )
+    _metre = re.compile(r"SI_UNIT\s*\(\s*\$\s*,\s*\.METRE\.\s*\)", re.IGNORECASE)
+    _inch = re.compile(r"CONVERSION_BASED_UNIT\s*\(\s*'INCH'", re.IGNORECASE)

     def parse(self, content: bytes) -> StepAnalysis:
         if not content.startswith(b"ISO-10303-21;"):
@@ -96,13 +101,12 @@ class StepTextParser:
             maximum=tuple(max(axis) for axis in axes),  # type: ignore[arg-type]
         )

-    @staticmethod
-    def _length_unit(text: str) -> str:
-        normalized = text.upper()
-        if "SI_UNIT(.MILLI.,.METRE.)" in normalized:
+    @classmethod
+    def _length_unit(cls, text: str) -> str:
+        if cls._millimetre.search(text):
             return "mm"
-        if "SI_UNIT($,.METRE.)" in normalized:
+        if cls._metre.search(text):
             return "m"
-        if "CONVERSION_BASED_UNIT('INCH'" in normalized:
+        if cls._inch.search(text):
             return "in"
         return "UNKNOWN"
diff --git a/apps/api/tests/test_cad.py b/apps/api/tests/test_cad.py
index aff2f5f..0afd670 100644
--- a/apps/api/tests/test_cad.py
+++ b/apps/api/tests/test_cad.py
@@ -41,6 +41,18 @@ def test_step_parser_extracts_metadata_and_envelope() -> None:
     assert result.volume is None


+def test_step_parser_accepts_standard_whitespace_in_length_unit() -> None:
+    content = (
+        b"ISO-10303-21;\nDATA;\n"
+        b"#1=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT ( .MILLI.,\n .METRE. ));\n"
+        b"ENDSEC;\nEND-ISO-10303-21;"
+    )
+
+    result = StepTextParser().parse(content)
+
+    assert result.length_unit == "mm"
+
+
 def test_step_parser_rejects_missing_terminator() -> None:
     with pytest.raises(StepParseError, match="terminator"):
         StepTextParser().parse(b"ISO-10303-21;")
```

## Estado do envio ao CTO
Em 2026-09-08, a tentativa de enviar o resumo técnico ao Gemini foi rejeitada pela revisão automática: autorização de contato considerada insuficiente para transmitir arquitetura, vulnerabilidade e detalhes internos. Nenhum envio confirmado. Solicitada autorização específica para o conteúdo, sem credenciais. Próxima ordem ainda não recebida. Nenhuma tentativa alternativa de transmissão realizada.

## Handoff confirmado e próxima missão
O proprietário autorizou explicitamente o conteúdo técnico. Resumo enviado ao Gemini e confirmado na conversa em 2026-09-08. CTO aprovou com ressalvas e emitiu CTO-CODEX-FIX-002: igualdade estrita no estado completo de compatibilidade, teste negativo, .gitignore e saneamento de CONTEXT; commit local na mesma branch; sem push/merge/publicação. A condição está na linha 208 do HEAD auditado (a referência aproximada 212 anterior indicava o mesmo trecho).
