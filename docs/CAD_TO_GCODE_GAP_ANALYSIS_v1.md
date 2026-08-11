# CAD_TO_GCODE_GAP_ANALYSIS_v1

**Status:** `READY_FOR_CTO_REVIEW`

**Task:** `TASK-CADGCODE-001`

**Baseline verificada:** `v2.1.0`

**Baseline da análise:** `main@705e76b534bf8748fdbc15a212293e43430557ed`

**Safety:** `NO_MACHINE_SEND`, `NO_DNC`, `NO_AUTOMATIC_NC_TRANSFER`,
`NO_CYCLE_START`, `NO_DIRECT_MACHINE_CONTROL`,
`NO_AUTONOMOUS_PHYSICAL_EXECUTION`, `NO_HUMAN_REVIEW_BYPASS`

Qualquer saída executável futura começa classificada como
`CANDIDATE_FOR_VALIDATION / NON_PRODUCTION / REQUIRES_HUMAN_REVIEW`.
Este documento propõe arquitetura e gates; não implementa toolpath,
pós-processador, G/M-code, NC/DNC, simulação física ou controle de máquina.

## 1. Executive Summary

A Vena_IA v2.1.0 possui uma cadeia preliminar, determinística e auditável de
STEP para propriedades geométricas, três classes de evidência geométrica,
um único candidato de planejamento (`THROUGH_CYLINDRICAL_HOLE` → drilling),
recomendações por catálogos e um plano CNC neutro não executável. Ela não
possui interpretação geral de fabricação, planejamento de setups/operações,
toolpath, pós-processador, G-code candidato, remoção de material, detecção de
colisão ou simulação específica de máquina.

O menor caminho seguro não é ensinar o sistema a reconhecer a peça do teste.
É introduzir contratos gerais entre B-Rep, stock e regiões de remoção;
restringir o primeiro marco a fresamento 3 eixos/2.5D em perfil sintético;
gerar trajetória determinística limitada; pós-processar para um subconjunto
versionado de RS274; e verificar por implementação independente antes de
revisão humana. Um teste físico exige adicionalmente simulação específica da
máquina e autorização humana G10.

Recomendação: concluir os dois Packages v2.2 já previstos e criar um marco
arquitetural separado **v2.3 — Controlled CAD-to-G-code Validation**, em vez de
forçar o escopo executável dentro de v2.2 ou aguardar v3.0. O digital thread de
v3.0 melhora persistência e governança, mas não bloqueia um ensaio sintético
controlado, desde que os artefatos sejam imutáveis, versionados e rastreáveis.

## 2. Verified Baseline v2.1.0

| Evidência | Resultado verificado |
|---|---|
| `main` local/remota | `705e76b534bf8748fdbc15a212293e43430557ed` |
| Tag anotada `v2.1.0` | aponta para `a086b284f95f586f12509d609a01546d43a92c8d` |
| GitHub Release | publicada, não Draft e não prerelease, em 2026-08-07 |
| Release | `Vena_IA Platform v2.1.0 — Enterprise Engineering Governance` |
| Alembic | single head `e61c4f8a2b90` |
| Testes diagnósticos | 69 aprovados em CAD, features, planning, CNC, workflow e rehearsal |
| Deploy | não realizado |

`DECISIONS.md` na raiz está ausente. O equivalente oficial existente e usado é
`docs/DECISIONS.md`. `docs/ARCHITECTURE.md` é um apontador; a autoridade é
`ARCHITECTURE.md` na raiz.

### Divergências documentação ↔ implementação

1. `ARCHITECTURE.md` descreve fluxo de parser para STEP/STL/DXF/IGES; upload e
   análise reais aceitam somente PDF e STEP, e os serviços DXF/STL são READMEs
   reservados. A redação arquitetural excede a implementação.
2. `CONTEXT.md` contém linhas históricas que ainda chamam o backend de v1.8.0 e
   registram o head `c27f6d9e4a10`, embora o mesmo documento registre corretamente
   v2.1.0 e `e61c4f8a2b90` em seção anterior.
3. O ROADMAP histórico de v0.8 mencionava blocos preliminares de G-code; código,
   contratos e decisões posteriores implementaram deliberadamente somente preview
   neutro, não executável. O estado real é a implementação fail-closed.
4. `docs/RISK_REGISTER.md` ainda marca v2.1 como RC na matriz de tratamento,
   embora a Release esteja publicada.
5. `docs/RELEASE_NOTES_v2.1.0.md` conserva a frase de gate de publicação já
   superado. É wording histórico, não estado operacional.

## 3. Current Architecture

A arquitetura é um modular monolith FastAPI. A cadeia relevante é:

```text
DocumentService (auth + extensão/MIME/assinatura)
  → StepTextParser (metadados Part 21)
  → OpenCascadeGeometryKernel (B-Rep carregada e propriedades globais)
  → FeatureRecognizer rule 1.0.0 (faces e through-hole estrito)
  → FeaturePlanningBridge rule 1.0.0 (somente drilling candidate)
  → EngineeringCatalogService (material/máquina/ferramenta e parâmetros)
  → CNCPlanningService (preview neutro não executável)
  → IntegratedEngineeringWorkflow (composição efêmera + human review)
```

Os contratos públicos relevantes são:

- `vena-ia.geometry-analysis/v1`;
- `vena-ia.geometry-features/v1`;
- `vena-ia.feature-planning/v1`;
- `vena-ia.engineering-recommendation/v1`;
- `vena-ia.cnc-neutral-plan/v1`;
- `vena-ia.integrated-engineering-workflow/v1`;
- `vena-ia.virtual-cnc-plan-validation/v1`.

Não há persistência do workflow integrado nem digital thread de manufatura.

## 4. Current CAD 3D Capability

### Entrada e kernel

- Formatos reais: `.step` e `.stp`, MIME `application/step` ou `model/step`,
  assinatura `ISO-10303-21;`; limite efetivo do kernel de 50 MiB.
- O parser textual extrai filename, schema, tipos/contagem de entidades,
  `CARTESIAN_POINT`, envelope preliminar e unidade textual (`mm`, `m`, `in` ou
  `UNKNOWN`). Ele não resolve B-Rep.
- O kernel real é OCCT 7.9.3 via `cadquery-ocp==7.9.3.1.1`. Ele lê e transfere
  roots STEP, forma um `OneShape`, valida topologia e calcula bounding box,
  área e volume quando a classe/validade permite.

### Inventário objetivo

| Capacidade | Estado | Evidência/limite |
|---|---|---|
| B-Rep/topologia carregada | EXISTS interno | OCCT `TopoDS_Shape`; não há contrato público geral |
| Solids/compound | PARTIAL | classe global e volume; sem inventário/relacionamento |
| Faces | PARTIAL | travessia até 10.000; apenas plane/cylinder |
| Edges/vertices | ABSENT no contrato | não percorridos nem expostos |
| Shells/wires/loops | ABSENT no contrato | não percorridos nem expostos |
| Planos/cilindros | EXISTS limitado | classificação e evidência local |
| Cones/arcos/NURBS/freeform | ABSENT na análise | kernel pode representar, adapter não expõe |
| Orientação | PARTIAL | normal de plane e eixo/orientation de cylinder |
| Bounding box/área/volume | EXISTS | propriedades globais; volume condicionado |
| Relações/adjacência | ABSENT | nenhum grafo topológico |
| Unidades | PARTIAL/FRÁGIL | declaração textual; sem normalização/prova de escala |
| Tolerância do kernel | ABSENT | contrato retorna `NOT_AVAILABLE`; rule usa `1e-6` na unidade declarada |
| Assemblies | ABSENT | roots colapsados em `OneShape`; sem estrutura/produto |
| PMI/MBD/GD&T | ABSENT | não extraídos |
| Feature recognition | PARTIAL/fechado | plane, cylinder, axis-aligned through-hole |
| Versionamento/evidence | EXISTS | rule `1.0.0`, confidence, refs locais, limitações |
| Corpus real | ABSENT | nenhum arquivo CAD versionado encontrado |
| Corpus sintético | EXISTS limitado | box, cylinder, through/blind bores, multi-bore e invalid topology |

### Respostas A–F

**A.** Sim, o kernel consegue carregar geometria STEP não descrita previamente,
desde que OCCT a aceite. **B.** O nível atual é apenas B-Rep interna mais
propriedades globais e superfícies primitivas suportadas; não é compreensão de
fabricação. **C.** Sim, feature recognition depende de allowlist fechada e rule
`1.0.0`. **D.** Bounding box, área, volume, validade e tipo global são análise
genérica; plane/cylinder/through-hole são regras específicas. **E.** Topologia,
propriedades métricas, adjacência, conectividade, orientação, regiões fechadas e
candidatos geométricos podem ser derivados sem perguntar, mas precisam de contrato
novo e evidência. **F.** Unidade, tolerância, referências locais instáveis,
`OneShape`, ausência de adjacency/stock/PMI e o critério de furo restrito ao envelope
global são fronteiras frágeis. Nenhuma delas autoriza inferir intenção produtiva.

## 5. Current CAD 2D Capability

`CAD_2D_CAPABILITY = ABSENT`.

- DXF, DWG, IGES 2D e desenhos não são aceitos pelo upload.
- Linhas, arcos, círculos, polilinhas, layers, blocos, cotas, texto, vistas,
  tolerâncias, espessura, profundidade e anotações não são interpretados.
- `services/parser-dxf` é apenas placeholder de serviço futuro.
- PDF é aceito como documento/RAG, não como drawing técnico geométrico.

CAD 2D deve ficar fora do primeiro marco. Incluí-lo adicionaria parsing,
reconstrução de vistas, semântica de cotas e associação 2D↔3D ao caminho crítico.
No primeiro ensaio, tolerância, acabamento e datum ausentes no STEP devem ser
inputs humanos explícitos, não extraídos de drawing.

## 6. Geometry Interpretation Capability

`GEOMETRY_INTERPRETATION = PARTIAL`.

A arquitetura possui a B-Rep necessária como fonte, mas perde quase toda sua
estrutura ao convertê-la para os contratos atuais. Falta uma representação geral,
estável e auditável de subshapes, relações e transformações. A regra não deve
enumerar previamente features do corpo de prova.

Representação mínima proposta, justificada pela lacuna observada:
`vena-ia.manufacturing-geometry-model/v1`.

Campos mínimos:

- hash do documento, kernel, versão, unidade normalizada, tolerância e transform;
- final B-Rep hash e inventário estável de solids/shells/faces/wires/edges/vertices;
- tipo geométrico, bounds, orientação e adjacency por identificadores estáveis;
- stock explícito ou estado `MISSING`; nunca derivado silenciosamente do envelope;
- regiões de material a remover e superfícies protegidas, com método/evidence;
- candidatos de datum, direções de acesso e setups, nunca seleções automáticas;
- cavidades, saliências, regiões internas/externas e profundidades geométricas;
- ambiguidades, fatos ausentes, confiança, assumptions e provenance.

Essa camada é necessária porque `geometry-features/v1` descreve ocorrências
isoladas e não consegue representar stock-final, adjacency, proteção, acesso ou
setups. Ela não deve conter operação, ferramenta ou autoridade de fabricação.

## 7. Manufacturing Interpretation Capability

`MANUFACTURING_INTERPRETATION = PARTIAL_LOW`.

Existe somente uma ponte: um furo cilíndrico passante estrito vira possibilidade
de drilling. Faces planas/cilíndricas permanecem evidência sem intenção. Faltam:

- stock-final difference e classificação de regiões removíveis/protegidas;
- acessibilidade por ferramenta/holder e direções candidatas;
- datums, WCS, setups e workholding;
- tolerância/acabamento e prioridade funcional;
- seleção entre estratégias e tratamento de ambiguidades;
- prova de cobertura e preservação de superfícies.

O sistema deve derivar fatos geométricos; catálogos devem fornecer recursos e
limites; o usuário deve fornecer intenção e fatos de processo não contidos no CAD.

## 8. Process Planning Capability

`PROCESS_PLANNING = PARTIAL_LOW`.

Os catálogos de material, máquina e ferramenta têm ownership organizacional v2.1,
seleção fail-closed, versões e recomendações determinísticas. Há parâmetros
preliminares de milling/drilling/turning, tempo de corte simplificado e custo/setup
opcionais. O workflow reutiliza tudo sem persistência.

| Necessidade | Hoje | Fonte futura correta |
|---|---|---|
| Setup(s) | ABSENT | geometry candidates + fixture/WCS humanos |
| Sequência | ABSENT | planner determinístico com precedências |
| Seleção de operação | PARTIAL | geometry + regras + intent; hoje só drilling candidate |
| Seleção de ferramenta | PARTIAL | usuário informa ID; não há search/ranking por região |
| Parâmetros | PARTIAL | catálogos; faltam engagement, stepdown/stepover e estratégia |
| Origem/WCS | ABSENT | usuário/fixture; candidato geométrico auditável |
| Stock | ABSENT | input obrigatório ou modelo autorizado |
| Tolerância/acabamento | INPUT opcional | obrigatório por superfície crítica |
| Fixture | INPUT textual | precisa contrato geométrico e envelope |
| Estratégia | ABSENT | planner/toolpath por capability allowlist |

## 9. Toolpath Capability

`TOOLPATH_CAPABILITY = ABSENT`.

Não existe cutter-location model, operação geométrica, trajectory planner,
lead-in/out, stepdown/stepover, linking, retract, avoidance, rest machining ou
verificação de cobertura.

### Alternativas avaliadas

| Alternativa | Maturidade/licença | 2.5D, determinismo e testes | Compatibilidade/risco | Decisão |
|---|---|---|---|---|
| OCCT direto | Maduro; LGPL-2.1 + exception | bons algoritmos geométricos, mas não é motor CAM completo | já integrado; alto esforço próprio e risco de safety | base geométrica, não gerador isolado |
| FreeCAD CAM | Maduro e abrangente; LGPL-2.1+ | jobs, pocket/contour, tool library, simulation e postprocessors | processo/runtime pesado; acoplamento e superfície amplos | spike isolado, não primeira dependência embutida |
| OpenCAMLib | Biblioteca CAM; LGPL-2.1; drop/push cutter | útil para waterline/drop-cutter e cutters; cobertura não completa | bindings Python, foco em STL; integração e manutenção a provar | candidato de avaliação para verificação/3D futuro |
| Algoritmo interno limitado | Maturidade inicial; licença do projeto | excelente determinismo/testabilidade para 2.5D allowlist | escopo deve ser muito estreito; dívida e risco explícitos | recomendado para primeiro marco sintético |
| Serviço local externo | depende do motor | isolamento e comparação independente | operacionalmente mais complexo | adaptador futuro se spike vencer gates |

Fontes primárias: [OCCT overview/licença](https://dev.opencascade.org/doc/overview/html/index.html),
[FreeCAD CAM](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/CAM_Workbench.md),
[FreeCAD licença](https://github.com/FreeCAD/FreeCAD/blob/main/LICENSE) e
[OpenCAMLib](https://github.com/aewallin/opencamlib).

Componente mínimo recomendado: `ToolpathCandidate/v1`, limitado a 3 eixos/2.5D,
uma operação simples aprovada pelo planner, linhas/arcos no plano XY, níveis Z,
retract/clearance explícitos, cutter/holder envelope, provenance e hash. A operação
é escolhida pelo conteúdo do CAD dentro da allowlist; não é hardcoded pelo teste.

## 10. Postprocessor/G-code Capability

`POSTPROCESSOR_CAPABILITY = ABSENT`; `GCODE_CAPABILITY = ABSENT`.

O neutral plan existente contém `controller_family=FANUC_OI_STRATEGY_PLACEHOLDER`
e `machine_profile=ROMI_D1250_PLANNED_COMPATIBILITY`. São placeholders contratuais,
não perfis funcionais. Não há dialeto, modal state, formatter, mapping de operação,
golden programs, parser de retorno ou prova em controlador.

O futuro postprocessor mínimo deve ser pure-function, allowlisted, versionado,
reprodutível e consumir somente `ToolpathCandidate/v1` já aprovado. A saída não
deve ser armazenada como “programa de produção”; deve ser um artefato candidato
com hash, manifest, input hashes e relatório do verificador independente.

## 11. Simulation/Verification Capability

`vena-ia.virtual-cnc-plan-validation/v1` valida estrutura e flags do plano neutro:
schema, review flags, neutralidade, ausência de bloco executável, alvo de
transmissão e controle. Todos os checks são produzidos como PASS após Pydantic.
Ela não interpreta G-code, não executa trajetória e não simula stock, ferramenta,
fixture, colisão ou cinemática.

### Níveis propostos

1. **Level 1 — obrigatório para qualquer candidato:** parser/AST independente do
   gerador; allowlist de G/M subset; estado modal; unidades/plano/WCS/distance/feed;
   limites; spindle/tool/coolant state; rapid/retract; fim de programa; proibição de
   offsets, parâmetros, subrotinas e códigos não autorizados; replay determinístico.
2. **Level 2 — obrigatório para o marco controlado e antes de teste físico:**
   reconstrução independente de trajetória, sweep da ferramenta/holder, remoção de
   stock, gouge/remaining material, envelope, fixture, rapid collision, engagement,
   cobertura e erro geométrico contra final B-Rep.
3. **Level 3 — obrigatório antes de qualquer teste físico:** perfil real de máquina,
   limites/kinematics, controlador/dialeto exato, offsets/tool table e simulação ou
   dry-run equivalente sob procedimento humano aprovado.

LinuxCNC oferece uma referência formal e atual de semântica RS274/NGC, inclusive
estado modal e ordem de execução; isso é referência de parser, não autorização de
compatibilidade com máquina real: [G-code Overview](https://linuxcnc.org/docs/html/gcode/overview.html).
FreeCAD CAM/CAMotics podem servir como oráculos auxiliares em spikes, nunca como
única evidência safety.

## 12. User Missing-Input Model

### Derivar automaticamente com evidence

- final B-Rep, subshape graph, dimensões e orientações;
- stock-final difference somente quando stock explícito existe;
- regiões, direções de acesso e datum/setup candidates;
- capacidades e limites de catálogos autorizados;
- operações candidatas e incompatibilidades.

### Exigir do usuário/configuração autorizada

- stock: forma, dimensões, material, condição e sobremetal;
- material grade/hardness e condição;
- machine profile e controller profile exatos;
- ferramentas, holders, comprimento, offsets e limites;
- fixture/workholding, keep-out volumes, datum e WCS;
- unidades de saída, tolerâncias, acabamento e superfícies críticas;
- manufacturing intent e operações/estratégias permitidas;
- coolant e restrições locais de segurança.

O sistema pergunta somente campos `MISSING` ou `AMBIGUOUS` que bloqueiam um gate.
Nunca infere GD&T, fixture, stock, WCS ou machine/controller a partir de STEP sem
evidência explícita.

## 13. Blind-Test Strategy

1. Um profissional qualificado prepara referência selada: CAD, stock, fixture,
   recursos, processo, trajetória e resultados esperados, com hashes.
2. O corpus de desenvolvimento não contém o CAD nem derivados; o time implementador
   recebe somente contratos e uma classe pública de complexidade.
3. O sistema recebe CAD e inputs produtivos legítimos, mas não a lista esperada de
   features/operações. Toda pergunta e resposta é registrada.
4. O output é congelado antes de abrir a referência. Replays usam manifest de versões.
5. Dois avaliadores independentes comparam e adjudicam divergências.

Métricas mínimas:

- interpretação geométrica correta, elementos omitidos e falsos reconhecimentos;
- erro dimensional e unidade/coordinate transform;
- missing inputs solicitados e perguntas desnecessárias;
- operações corretas/indevidas, sequência, ferramenta e parâmetros;
- cobertura da trajetória, material remanescente, gouge e erro geométrico;
- validações pass/fail, falsos negativos e falsos positivos;
- intervenção humana, tempo e divergência do processo profissional.

Critério essencial: zero unsafe false negative. Um bloqueio conservador pode ser
aceito e medido; um artefato inseguro aprovado invalida o marco.

## 14. Gap Matrix

| Capacidade | Estado | Classe | Bloqueio |
|---|---|---:|---|
| STEP secure ingest | EXISTS | A | não |
| B-Rep kernel/global properties | PARTIAL | A | contrato geral ausente |
| General topology graph | ABSENT/BLOCKER | A | sim |
| Closed feature rules | PARTIAL | B | não basta para teste geral |
| CAD 2D | ABSENT/DEFER | C | não |
| Stock-final interpretation | ABSENT/BLOCKER | A | sim |
| Accessibility/setups/datums | ABSENT/BLOCKER | A | sim |
| Organization-owned catalogs | EXISTS | A | não |
| General process planning | ABSENT/BLOCKER | A | sim |
| Deterministic parameters | PARTIAL | A | strategy inputs ausentes |
| Toolpath | ABSENT/BLOCKER | A | sim |
| Postprocessor | ABSENT/BLOCKER | A | sim |
| G-code parser/static verifier | ABSENT/BLOCKER | A | sim |
| Material-removal verifier | ABSENT/BLOCKER | A | sim |
| Machine-specific simulation | ABSENT | A para físico | sim para físico |
| Human review | EXISTS como flag | A | workflow técnico precisa definição |
| Physical-use authorization | policy EXISTS | A | nunca automático |
| Digital thread persistente | ABSENT/DEFER | B | não para ensaio sintético |

Classe A é obrigatória; B importante mas não bloqueadora do primeiro ensaio;
C é adiável.

## 15. Critical Path

```text
CURRENT_v2.1
→ G0 secure STEP + normalized units
→ G1 stable B-Rep/topology evidence
→ ManufacturingGeometryModel (stock-final/access candidates)
→ G2 reviewed manufacturing interpretation
→ deterministic setup/operation/resource process plan
→ G3 + G4
→ bounded 3-axis/2.5D ToolpathCandidate
→ G5 independent geometry/toolpath checks
→ versioned synthetic postprocessor
→ G6
→ candidate RS274 subset
→ G7 independent AST/modal/static verifier
→ G8 Level-2 material-removal verification
→ G9 qualified human review
→ CAD_TO_GCODE_CONTROLLED_VALIDATION_READY
```

Para uso físico, acrescentar Level 3 e G10. As dependências são sequenciais onde
o contrato downstream exige evidence upstream; parser e simulador independentes
podem ser construídos paralelamente após contratos congelados.

## 16. Minimum CNC Target Recommendation

Primeiro alvo:

```text
MACHINE_PROFILE=VENA_SYNTHETIC_3AXIS_MILL_V1
CONTROLLER_PROFILE=VENA_RS274_SAFE_SUBSET_V1
POSTPROCESSOR_VERSION=VENA_SYNTHETIC_3AXIS_POST_V1
```

Escopo: XYZ cartesiano, unidades milimétricas, plano XY, coordenadas absolutas,
feed/min, uma ferramenta, linhas e arcos apenas se o verificador independente
provar geometria; sem macros, variables, subroutines, probing, canned cycles,
cutter compensation, coordinate mutation, multi-axis, turning ou códigos vendor.

Fanuc Oi/Romi D1250 não são o primeiro alvo porque não há perfil funcional nem
evidência de controlador/máquina. Um alvo real só substitui o sintético após
qualificação específica e novo gate humano.

## 17. Required Safety Gates

| Gate | Entrada/evidence e PASS | Responsável | Falha/rollback | Risco |
|---|---|---|---|---|
| G0 Parse integrity | hash, MIME/signature, schema, unit; parse completo e limites | CAD owner | quarantine/reject | R-019/R-039 |
| G1 Geometry | B-Rep válida, topology graph, transform, tolerance/evidence | Geometry reviewer | block; preserve artifact | R-040 |
| G2 Manufacturing interpretation | stock-final, protected/removal regions, ambiguity closed | Manufacturing engineer | request inputs/reject | R-041 |
| G3 Process plan | setups, precedence, intent, WCS assumptions, review | Process engineer | return to G2 | R-041/R-044 |
| G4 Resource compatibility | org-scoped machine/tool/material, hard limits, versions | Resource owner | incompatible/block | R-048/R-050 |
| G5 Toolpath | coverage, clearance, holder/tool sweep, deterministic replay | CAM reviewer | discard candidate | R-045/R-049 |
| G6 Postprocessor | exact input/output contract, golden + metamorphic tests, hash | Post owner | revoke version | R-045/R-049 |
| G7 Static G-code | independent AST/modal/units/WCS/limits/forbidden-code PASS | Safety verifier | reject artifact | R-045/R-049 |
| G8 Simulation | Level 2 PASS; Level 3 additionally for physical use | Verification owner | block/revise upstream | R-045/R-049 |
| G9 Human review | qualified checklist, evidence bundle, signed disposition | Human technical reviewer | reject/request correction | R-044/R-045 |
| G10 Physical use | direct, scoped authorization for exact hashes/machine/setup | Owner/delegated authority under policy | authorization expires/revokes | R-045/R-049 |

Nenhum gate herda PASS por nome de módulo. Toda alteração upstream invalida hashes
downstream. G10 nunca é automático nem implícito.

## 18. Risk Analysis

Os riscos solicitados já cobrem as novas hazards; não é necessário criar IDs
duplicados nesta análise.

| Hazard | Registro existente | Tratamento proposto |
|---|---|---|
| False geometry interpretation | R-039/R-040 | topology evidence, corpus real + blind holdout |
| False manufacturability inference | R-041 | separar geometry/fabrication e exigir missing inputs |
| Unsafe toolpath | R-045/R-049 | G5 + verifier independente + fail closed |
| Postprocessor mismatch | R-045/R-049 | perfil triplo exato, golden tests e revogação |
| Coordinate/unit/offset error | R-045/R-049 | normalização G0; AST/modal G7; offsets forbidden initially |
| Collision false negative | R-045/R-049 | Level 2/3 independente e zero unsafe false negative |
| Simulation false confidence | R-044/R-045 | níveis explícitos; current virtual validator não é simulador |
| CAD test overfitting | R-040 | holdout selado e anti-leakage |
| Cross-org resource leakage | R-048/R-050 | ownership v2.1 e checks downstream fail-closed |
| Native kernel/dependency | R-019/R-039 | pinned runtime, limits, parity e corpus |

## 19. v2.2 Mapping

### Package 1 — natural fit

- ampliar coverage geométrica/topológica geral sem codificar o blind test;
- identificadores estáveis, adjacency, units/tolerance evidence;
- corpus real/sintético e avaliação de false positives/negatives;
- manter interpretação não executável e human review.

### Package 2 — natural fit

- `ManufacturingGeometryModel/v1`;
- stock-final/removal/protected surfaces/access/setup candidates;
- planner de setups, sequência, compatibilidade e evidence;
- Level-0/planejamento verification, ainda sem toolpath/G-code.

O ROADMAP vigente proíbe toolpath/postprocessor/G/M-code em v2.2. Inseri-los sem
decisão formal seria mudança substancial e misturaria entendimento com execução.

## 20. v3.0 Dependency Analysis

Não é necessário antecipar agentes inteligentes, digital thread completo, learning
loop, telemetry de máquina ou otimização contínua de v3.0 para o primeiro ensaio.
A rastreabilidade mínima pode usar manifest imutável, hashes e evidence bundle.

Persistência do digital thread é importante para auditoria longitudinal e escala,
mas é classe B para este marco. Nenhum componente v3.0 deve receber autoridade
para gerar, aprovar ou executar movimento CNC.

## 21. Deferrable Capabilities

- CAD 2D/DXF/DWG e reconstrução semântica de desenhos;
- assemblies e PMI/MBD/GD&T automáticos;
- 3D freeform, 4/5 eixos, turning e mill-turn;
- cones/threads/gears/pattern intelligence;
- multiple fixtures/setups complexos e rest machining;
- machine-send, DNC, cycle start e controle direto (permanentemente fora até ordem);
- AI strategy selection, learning loop e autonomous optimization;
- catálogo universal de postprocessors e interface CAM avançada;
- custo/tempo de produção de alta fidelidade.

## 22. Recommended Roadmap

1. **v2.2 Package 1:** General Geometry Evidence.
2. **v2.2 Package 2:** Manufacturing Interpretation & Verified Process Planning.
3. **v2.3 Package 1:** bounded 3-axis/2.5D toolpath candidate + independent geometry verifier.
4. **v2.3 Package 2:** synthetic versioned postprocessor + independent Level-1 parser/static verifier.
5. **v2.3 Package 3:** Level-2 stock/material-removal verifier + sealed blind-test harness.
6. **v2.3 Release Candidate:** run blind validation, G0–G9, publish evidence; no physical use.
7. **Post-v2.3 separate physical gate:** exact real machine/controller/post, Level 3 and G10.

`v2.2.x` seria possível apenas com alteração formal do ROADMAP, mas é tecnicamente
inferior: ferramenta executável introduz nova boundary de safety. v2.3 torna essa
fronteira visível. Aguardar v3.0 é desnecessário e aumenta o caminho crítico.

## 23. Minimal Packages/Tasks

| Task | Produto | Acceptance essencial |
|---|---|---|
| CADG-101 | topology evidence contract | real + synthetic corpus; stable refs; units/tolerance |
| CADG-102 | manufacturing geometry model | stock-final, regions, access, ambiguity, no operation claim |
| CADG-103 | verified process planner | setups/sequence/resources/missing inputs; no toolpath |
| CADG-201 | ToolpathCandidate 2.5D | bounded allowlist, deterministic, coverage/clearance evidence |
| CADG-202 | independent toolpath verifier | no shared generator logic; sweep/stock/gouge metrics |
| CADG-203 | synthetic postprocessor | exact profile/version, pure output, golden/metamorphic tests |
| CADG-204 | independent RS274 subset verifier | AST/modal/units/WCS/limits/forbidden constructs |
| CADG-205 | blind-test harness | sealed reference, hashes, metrics, anti-leakage |
| CADG-206 | G0–G9 review bundle | all evidence immutable; qualified human disposition |
| CADG-301 | real-machine qualification | future only: Level 3 + exact setup + G10 |

Cada task deve preservar tenancy, reversibilidade, public contracts e negative
tests. Mudança de contrato requer versionamento e ADR aprovado antes de código.

## 24. Criteria for `CAD_TO_GCODE_CONTROLLED_VALIDATION_READY = TRUE`

O estado só pode ser TRUE para um artefato e perfil exatos quando:

1. v2.1 security/tenancy controls permanecem aprovados;
2. CAD holdout passa G0 e G1 sem dados esperados vazados;
3. units, transform, topology, stock e missing facts estão explícitos;
4. interpretação e plano passam G2–G4 com zero unsupported escalation;
5. toolpath candidate determinístico passa cobertura, gouge e clearance G5;
6. postprocessor exato passa G6 e emite somente subset allowlisted;
7. parser/verificador independente passa G7, inclusive negative/metamorphic tests;
8. Level 2 passa G8 com zero unsafe false negative no corpus de aceitação;
9. blind-test metrics e divergência profissional ficam dentro de thresholds
   aprovados previamente pelo CTO, não ajustados após abrir a referência;
10. reviewer qualificado aprova G9 para os hashes exatos;
11. saída continua `NON_PRODUCTION`, sem machine-send/DNC/control;
12. documentação, riscos, versões, SBOM/licenças e rollback estão completos.

Este documento **não** satisfaz esses critérios e não altera o flag:

```text
CAD_TO_GCODE_CONTROLLED_VALIDATION_READY=FALSE
PHYSICAL_USE_AUTHORIZED=FALSE
```

Para qualquer teste físico ainda são obrigatórios Level 3 e G10 direto, específico,
limitado aos hashes, máquina, controller, ferramenta, fixture, stock e procedimento.

## Registro de Entrega

- **Objetivo:** mapear o menor caminho seguro entre v2.1.0 e validação CAD→G-code.
- **Escopo:** auditoria de código, contratos, testes, docs e alternativas; sem código funcional.
- **Arquivos:** este relatório e referências de estado em CHANGELOG/CONTEXT/status CTO.
- **Testes:** 69 testes focais aprovados; Alembic single head confirmado.
- **Aceitação:** 24 seções, matriz, critical path, target, níveis, blind test, gates e roadmap.
- **Próximo passo:** decisão formal CTO/Owner sobre a proposta v2.2→v2.3.
