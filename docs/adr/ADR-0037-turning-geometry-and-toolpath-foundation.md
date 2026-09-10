# ADR-0037 — Contratos propostos para torneamento controlado em XZ

**Status:** Aprovado tecnicamente com ressalvas — incremento IMPL-004; demais contratos PROPOSED
**Data:** 2026-09-08
**Responsável:** Codex (executor); Gemini (revisão técnica AR da SPEC-003)

## Contexto e problema

A linha v3.1 NON_PRODUCTION possui evidência OCCT de superfícies e candidatos
limitados a fresamento 3 eixos/2.5D. Reconhecer Cylinder/Cone não demonstra eixo
comum de revolução, perfil usinável ou capacidade de torneamento. Esta proposta
é aditiva aos [contratos CAD](ADR-0031-general-geometry-topology-evidence.md),
[manufatura](ADR-0032-manufacturing-interpretation-planning.md) e
[toolpath](ADR-0033-bounded-toolpath-candidates.md); não altera suas versões.

A proposta integral abaixo não está implementada; ver o incremento delimitado ao final. A aprovação desta especificação não
homologa controlador, ferramenta, fixação, segurança física ou gate G9.

## Decisão proposta

Manter o Modular Monolith e reutilizar o adapter OCCT e o shape já carregado.
Propor read models versionados próprios de torneamento no CAD e Engineering,
sem inferir operações a partir de faces nem reutilizar o pós de fresamento.
Não há endpoint, migration ou mudança de persistência nesta missão.

### 1. Geometria, eixo e datum

Contrato proposto `vena-ia.turning-profile/v1`:

| Campo | Semântica e validação proposta |
|---|---|
| `source_artifact_hash`, `topology_evidence_id` | Proveniência do STEP e da evidência original; sem caminhos locais ou segredos |
| `kernel_version`, `algorithm_version` | Fronteira explícita de identidade/replay |
| `status`, `reasons` | `AVAILABLE`, `MISSING_INPUT`, `AMBIGUOUS`, `UNSUPPORTED`, `INVALID`; falha nunca retorna perfil utilizável |
| `units` | Milímetros após conversão comprovada; unidade desconhecida bloqueia |
| `axis_origin_world`, `axis_direction_world` | Eixo candidato comum com direção unitária, sustentado por faces identificadas |
| `world_to_setup` | Transformação rígida, sem escala/reflexão; origem e orientação rastreadas ao datum selecionado |
| `datum_face_id` | Face frontal final plana, normal ao eixo; seleção explícita, nunca a face bruta por inferência |
| `linear_tolerance_mm`, `angular_tolerance_rad` | Tolerâncias numéricas finitas positivas com origem/versão; não tolerâncias de fabricação |
| `profile_segments` | Segmentos ordenados no semiplano radial positivo, pontos `(radius_mm, z_mm)` e faces/arestas de origem |
| `ambiguities`, `limitations` | Limitações explícitas, inclusive fronteira entre perfil reconhecido e operação suportada |

Datum proposto: Z=0 na face frontal acabada; Z positivo aponta para fora da peça
na direção livre da montagem; corpo usualmente em Z negativo; X=0 é o eixo.
O datum inclui direção axial e vetor radial de referência para remover a
ambiguidade angular de uma peça de revolução. A orientação da máquina real exige
um setup explícito posterior. Coordenadas geométricas internas usam raio;
`x_diameter_mm = 2 * radius_mm` ocorre uma única vez no contrato programado.
Distâncias, folgas, raio de ponta e colisões são calculados no espaço físico
radial, nunca diretamente em X de diâmetro. Não aceitar convenção implícita.

Algoritmo candidato, a provar em missão de implementação:

1. Validar unidades, shape, um único sólido fechado e limites de complexidade.
   Usar faces analíticas Cylinder/Cone e planos terminais normais ao eixo;
   rejeitar cavidades, sólidos múltiplos, superfícies livres e topologia inválida
   na primeira cobertura. Não inferir eixo por bounding box.
2. Obter eixos analíticos transformados e agrupar por colinearidade dentro das
   tolerâncias. Eixos anti-paralelos representam a mesma reta; a direção final
   deriva do datum. Verificar todas as faces e a cobertura angular completa,
   não apenas a maioria dos cilindros; uma seção isolada não prova revolução.
3. Se houver vários candidatos ou datum não resolvido, retornar ambiguidade.
   Construir plano que contém o eixo e o vetor radial escolhido; seccionar o
   BRep, aplicar transformações/limites das faces e reconstruir conectividade.
4. Selecionar e ordenar a fronteira externa no semiplano radius>=0, preservando
   degraus e segmentos radiais. Rejeitar gaps, duplicatas não resolvidas,
   auto-interseções e regiões internas; não substituir pelo casco convexo.
5. Confrontar o perfil reconstruído com todas as superfícies e domínios do sólido.
   Registrar erro geométrico máximo e evidência de cobertura; ausência de prova
   bloqueia. Ordenação e IDs canônicos independem da ordem incidental do OCCT.

Cones podem ser reconhecidos como perfil linear inclinado, mas não autorizam
cilindramento cônico: o primeiro planner aceita somente operações retas abaixo.
Limites numéricos, complexidade e equivalência geométrica exigem calibração em
corpus; esta especificação não inventa valores universais.

### 2. Stock, fixação e intenção

Contrato proposto `vena-ia.turning-setup/v1`, ligado ao perfil e aos catálogos
autorizados da organização, sem criar catálogo paralelo:

| Campo | Regra |
|---|---|
| `stock.diameter_mm`, `stock.length_mm` | Finitos positivos, fornecidos; não copiados da bounding box final |
| `stock.front_z_mm` | Posição explícita da face bruta; fundo = front_z - length |
| `face_allowance_mm` | >=0; distância axial bruta até Z=0, coerente com front_z |
| `diameter_allowance_mm` | >=0, sobremetal total em diâmetro na região alvo; remoção radial é metade |
| `finish_face_allowance_mm`, `finish_radial_allowance_mm` | Material remanescente após a operação, >=0; distinto do sobremetal bruto |
| `fixture_id`, `exclusion_envelopes` | Placa/castanhas e demais obstáculos em coordenadas físicas do setup, com proveniência |
| `grip_length_mm`, `free_length_mm` | Fixação/saída declaradas e consistentes com stock; resistência não inferida |
| `machine_id`, `tool_id`, `operation` | Referências existentes com ownership e capacidade de turning verificadas |
| `clearances_mm`, `axial_limit_mm` | Folgas positivas e fronteira de trabalho explícitas, incluindo corpo/suporte |

O stock deve conter o perfil final e o material remanescente de todas as regiões
selecionadas. Em perfil escalonado, calcular/validar sobremetal por região; não
aplicar uma diferença global como profundidade uniforme. Fixação ausente ou
inconsistente bloqueia planejamento e toolpath; não é inferida de um cilindro.

Primeiro escopo: faceamento plano simples e cilindramento externo longitudinal
reto, ferramenta externa única, um setup, sem eixo C/Y ou ferramenta acionada.
Intenção explicita região, profundidade radial por passe, avanço com unidade,
velocidade e acabamento remanescente. Direção de corte deve ser compatível com
suporte/inserto. São excluídos roscas, canais, corte de separação, torneamento
interno, cones usinados, arcos, undercuts e ciclos G70/G71/G72/G76.

### 3. Ferramenta de torneamento

Contrato proposto `vena-ia.turning-tool/v1`:

| Campo | Regra |
|---|---|
| `insert.kind` | `EXTERNAL_TURNING`; designação ISO opcional, nunca substitui geometria |
| `insert.nose_radius_mm` | Finito >0, medido/documentado |
| `insert.wedge_angle_deg`, `insert.clearance_angle_deg`, `insert.rake_angle_deg` | Ângulos no plano de referência declarado; consistência geométrica verificável, sem default universal |
| `insert.included_angle_deg` | Ângulo da forma do inserto em planta, distinto do ângulo de cunha |
| `holder.cutting_direction` | Direção no setup (p.ex. Z negativo), com restrições radiais e mão do suporte |
| `holder.geometry`, `insert.geometry` | Envelope físico e transformação relativos ao ponto de referência; ausências bloqueiam validação |
| `reference_point`, `nose_center_offset` | Ponta teórica versus centro do raio definidos separadamente no espaço radial |
| `orientation_code` | Inteiro 1..9 mais `orientation_mapping_id/version`; código sozinho não valida quadrante |
| `compensation_policy` | Proposta de compensação geométrica no gerador; sem G41/G42 automático nesta fase |

O mapeamento de orientação Fanuc 1..9 depende do diagrama/manual do controlador,
da montagem e da referência da ponta. Não inventar tabela universal nem assumir
CNMG/PCLNR/r=0,8 mm como ferramenta homologada. Validador independente deve
conferir ponto comandado, envelope da pastilha e corpo não cortante; não aplicar
a regra de metade do diâmetro de uma fresa ao inserto de torno.

### 4. Trajetória e pós-processador

Contrato neutro proposto `vena-ia.turning-toolpath/v1`: segmentos físicos em
`(radius_mm,z_mm)`, tipo `RAPID`/`LINEAR_CUT`, referências de região, velocidades
e unidades explícitas, estado de material por passe e movimentos de entrada/
saída. Retração e aproximação respeitam stock restante e zonas de exclusão;
limites apenas dos endpoints não provam ausência de interseção do segmento.

Contrato programado proposto `vena-ia.turning-post-profile/v1` exige fabricante,
modelo/versão do comando, sistema de códigos, manual/revisão, X em diâmetro,
semântica absoluta, plano ZX, unidades mm, modo de avanço, spindle, limites,
offsets/referência da ferramenta, resolução/arredondamento e allowlist exata.
Perfil ausente/não validado => `CONTROLLER_PROFILE_UNRESOLVED`, sem NC emitido.

Não existe cabeçalho ISO/Fanuc universal seguro. Na lista oficial de torno Haas,
G90 é ciclo de torneamento, G94 é ciclo de faceamento e G95 é rosqueamento rígido
com ferramenta acionada; G98/G99 selecionam avanço por minuto/rotação. Essa
evidência demonstra a ambiguidade; **não adota Haas como controlador-alvo**.
Assim, a sequência G18/G21/G90/G95/G96/G50 citada na missão não é copiada como
programa. G90/G94/G95 só poderiam ser emitidos com semântica comprovada para
o perfil escolhido. Não misturar fresamento, torno ou sistemas de códigos.

Requisitos semânticos do futuro cabeçalho: plano ZX (G18 onde documentado), mm
(G21), coordenadas absolutas conforme dialeto, avanço por rotação em mm/rev ou
por minuto em mm/min explicitamente selecionado. CSS em m/min (G96 no perfil
compatível) requer limite RPM explícito previamente aplicado (G50 onde suportado),
coerente com limites de máquina, fixação e ferramenta. Em faceamento próximo a
raio zero, a fórmula de CSS não pode dividir por zero ou gerar RPM ilimitada;
política de limitação/transição deve ser validada antes da emissão. RPM fixa
(G97 onde suportado) é modo distinto, nunca fallback silencioso.

A primeira saída candidata usaria somente movimentos G00/G01, X em diâmetro e
Z absoluto, mais o conjunto modal/auxiliar mínimo homologado no perfil. Sem
ciclos enlatados ou compensação de ponta delegada ao controlador nesta etapa.
Reanalisar a saída arredondada com verificador independente, conferir modos,
limites, unidades, conversão raio/diâmetro e envelope de movimento. Um caminho
linear não comprova remoção de material, dinâmica da máquina ou segurança física.

### 5. Integração, rastreabilidade e aceitação futura

Contratos e builders aditivos em `apps/api/app/modules/cad` e `engineering`;
não ampliar silenciosamente enums/allowlists de fresamento. Reutilizar auth,
ownership, gates e Digital Thread mediante missão separada. Hashes canônicos
devem ligar fonte, setup, ferramenta, versões, perfil do controlador, trajetória
e evidências; replay e integridade não concedem autoridade.

Testes futuros mínimos: cilindro/degraus reconhecidos e transformados; cone
reconhecido com operação excluída; eixos concorrentes, sólido perfurado ou não
axissimétrico rejeitados; unidades desconhecidas; datum invertido/ausente;
stock insuficiente; campo não finito; orientação sem mapeamento; teste físico
de distância radial separado da coordenada de diâmetro; CSS no centro; colisão
entre endpoints; controlador indefinido e código de dialeto errado bloqueados.
Verificar determinismo e regressão completa de fresamento antes de integração.

## Alternativas e consequências

- Reutilizar planner/pós de fresa: rejeitado por semântica incompatível.
- Inferir processo de qualquer face cilíndrica: rejeitado por ausência de intenção,
  fixação e evidência global de revolução.
- Emitir imediatamente Fanuc genérico/G71: rejeitado por dialeto não validado e
  opacidade dos ciclos na primeira prova.
- Contratos separados: propõem evolução testável, com custo de extrator,
  verificador e perfil específico ainda não implementados.

## Pendências e limites

Revisão técnica do ADR e aprovação documental antes de implementação em missão
separada. Seleção real do controlador e manual, mapeamento 1..9, ferramenta,
fixação e dados de corte permanecem pendentes; não impedem a proposta abstrata.
`NON_PRODUCTION`, `G9=PENDING_AUTHORITATIVE_REVIEW` e
`PHYSICAL_USE_AUTHORIZED=false` permanecem. Sem machine-send, DNC, transferência
NC, cycle start, push, merge, tag, publicação ou deploy nesta missão.

## Fontes primárias consultadas em 2026-09-08

- [OCCT BRepAdaptor_Surface](https://dev.opencascade.org/doc/refman/html/class_b_rep_adaptor___surface.html): acesso a superfícies analíticas e transformações. A documentação corrente redireciona para OCCT 8.0.1; não afirma disponibilidade idêntica no binding instalado.
- [OCCT BRepAlgoAPI_Section](https://dev.opencascade.org/doc/refman/html/class_b_rep_algo_a_p_i___section.html): operação candidata para interseção BRep/plano, não prova automática de perfil usinável.
- [Haas — lista oficial de códigos de torno](https://www.haascnc.com/service/service-content/guide-procedures/lathe---g-codes.html): contraexemplo documentado à semântica universal do cabeçalho sugerido.

As regras arquiteturais e invariantes acima são propostas do projeto; as fontes
suportam capacidades da API e a distinção de dialetos, não homologam esta solução.

## Incremento aprovado — CTO-CODEX-IMPL-004

Parecer Gemini recebido em 2026-09-08: AR, baseado no relatório da SPEC-003, sem
inspeção direta do commit remoto. Correção de dialeto acolhida. Autorizada a
fundação local de cinco schemas Pydantic e verificador preliminar de eixo comum.
Não equivale à aprovação de G9 ou dos contratos completos de CAD/CAM/pós.

`engineering/turning_schemas.py` implementa somente dados declarados: ponto radial,
polyline/origem/direção/fechamento, stock mínimo, ferramenta mínima e requisito de
controlador. Estritos, sem extras/coerção/NaN/Inf; points usa tuple imutável em
Python e array no JSON, evitando mutação após validação. Validação de fechamento
não prova simplicidade, área, proveniência ou equivalência com um BRep. Stock
mínimo não contém setup/fixação; ferramenta mínima não valida ângulos completos,
orientação 1..9 ou envelope. Nenhum modelo é um candidato executável.

`ControllerProfileRequirement.x_mode` aceita RADIUS/DIAMETER como declaração a
resolver (conforme IMPL-004), sem alterar a convenção programada DIAMETER proposta.
`emission_status` sempre retorna CONTROLLER_PROFILE_UNRESOLVED. Não há emissor NC.

`cad/axisymmetry.py` compara todos os pares de retas cilíndricas/cônicas com
origens, direção normalizada e tolerâncias explícitas. Adapter OCCT inspeciona um
sólido válido, todas as faces, planos perpendiculares ao eixo e span angular
completo de superfícies analíticas. Topologia inválida, eixos divergentes,
superfícies desconhecidas e recursos excessivos retornam AXISYMMETRY_FAILED.
Sucesso AXISYMMETRY_PRELIMINARY_PASS não prova revolução global: U completo não
exclui todo recorte; furos coaxiais e análise de interior exigem extrator futuro.
Sem retorno de geratriz/datum inferidos, endpoints, integração ou alteração do
pipeline vigente. O chamador deve declarar a unidade real das coordenadas BRep,
que pode diferir da unidade original do STEP após a importação do kernel.

Os limites 512 faces e 10.000 pontos são orçamentos conservadores deste helper;
não prometem cobertura geral ou preempção de crash nativo. Tolerâncias vêm do
chamador e são numéricas, não fabricação. Status PASS é relativo a esses valores.
Referências de implementação: [Pydantic ConfigDict](https://docs.pydantic.dev/latest/api/config/)
e [OCCT BRepCheck_Analyzer](https://dev.opencascade.org/doc/refman/html/class_b_rep_check___analyzer.html).

## Incremento autorizado — CTO-CODEX-STEP-005

O Gemini aprovou IMPL-004 com ressalvas por relatório e emitiu STEP-005, permitindo
extrator e fixtures, sem CAM/NC. `cad/profile_extractor.py` implementa somente
cilindros externos simples/escalonados. Mantém datum frontal explícito (origem e
direção unitária), BRep em unidade declarada, perfil aberto em raio e Z monotônico
não crescente; faces frontal/traseira e ombros são segmentos radiais em Z
constante, sem o fechamento da linha de centro. Não dobra raio internamente.

O algoritmo candidato de seção do ADR é delimitado neste incremento por uma
alternativa analítica: intervalos axiais das faces cilíndricas transformadas,
ordenação e continuidade C0, reconstrução da união de cilindros e diferença
booleana em AMBOS os sentidos contra o BRep original. Qualquer face residual,
falha do kernel ou datum incompatível bloqueia. Não usar volume igual como prova.
A união/reconstrução impede transformar um teste de eixos ou caixa envolvente
em alegação de perfil externo completo. Interior, cone, intervalos sobrepostos,
lacunas e múltiplos sólidos não são suportados. Limite de 32 intervalos.

`PROFILE_AVAILABLE_REQUIRES_REVIEW` significa equivalência numérica no kernel,
não prova metrológica/física. Transformações e diferenças operam em cópias quando
necessário; tolerâncias de origem continuam risco numérico explícito. Chamador
fornece datum e unidade REAL do BRep; não há endpoint público, persistência ou
proveniência Digital Thread implementados neste incremento. As quatro fixtures
AP203/AP214 sintéticas e o gerador têm metadados fixos e unidades mm.

Fontes primárias: [OCCT Cut](https://dev.opencascade.org/doc/refman/html/class_b_rep_algo_a_p_i___cut.html)
e [STEPControl_Writer](https://dev.opencascade.org/doc/refman/html/class_s_t_e_p_control___writer.html).
APIs exercitadas no binding instalado 7.9.3.1.1; docs correntes são 8.0.1.


## Exceção técnica delimitada — CTO-CODEX-CAM-006A

Após identificar ausência de fixture/envelope/referência da ferramenta, o Codex
submeteu o conflito ao CTO. Gemini acolheu e substituiu CAM-006 por CAM-006A:
plano matemático sintético de ponto ideal, isolado do runtime e do pós. Esta
exceção permite apenas estudar decomposição de passes sem as entradas físicas;
**não permite chamar o resultado de toolpath validado ou sem colisões**.

`turning_toolpath_schemas.py` fixa is_collision_free=false,
collision_status=NOT_VALIDATED, executable_output=false e
physical_use_authorized=false. Modelos estritos, finitos e imutáveis; comprimento
é a soma geométrica dos segmentos CUTTING, incluindo ar, não corte de material
ou tempo físico. `profile_id` identifica o conteúdo do perfil sintético, não sua
proveniência STEP/Digital Thread. Não há valor de avanço ou dados de material.

`turning_planner.py` decompõe faceamento por profundidade axial e desbaste por
profundidade radial, parâmetros explícitos de teste. Stock frontal em
Z=face_allowance, fundo=face_allowance-length. Cada diâmetro atinge exatamente
seu alvo de sobremetal radial; o último passe de cada região pode ser menor que
ap, nunca maior. Sobremetal axial protege frente e ombros, sem operação traseira.
Perfis externos cilíndricos com raio não decrescente em Z negativo; undercuts,
cones, stock insuficiente, valores inválidos e orçamento excessivo são rejeitados.

RAPID/RETRACT são segmentos de ponto ideal com folga geométrica de referência,
sem afirmar que a posição é segura em máquina. Continuidade e comprimentos são
checados no contrato; não equivalem a verificador de colisão com material,
pastilha, suporte ou fixação. Nenhuma ferramenta real ou compensação é consumida.
Limites: 1000 passes por operação, 10000 movimentos por plano; sem integração.


## Incremento técnico aprovado — CTO-CODEX-CAM-007A

Em 2026-09-09, Gemini acolheu integralmente o conflito de CAM-007 e autorizou
CAM-007A: verificador independente de fronteiras sintéticas declaradas. A ordem
original foi substituída; não implementar interferência de haste com stock sem
receber material remanescente. AABB local explícita relativa ao ponto ideal,
sem inferência a partir de quadrante, pastilha ou ângulos. Zonas retangulares
estáticas fornecidas explicitamente; tuple vazia significa nenhuma zona adicional.
Plano conservador de chuck vale em todo R; diâmetro é somente metadado.

Todos os segmentos RAPID/CUTTING/RETRACT são testados continuamente contra
plano axial e zonas expandidas pelos offsets da AABB. Contato é violação;
linha central aplica R>=0 ao ponto ideal, não ao envelope local assinado.
Plano vazio NOT_EVALUATED; entradas inválidas rejeitadas por revalidação.
PASS significa apenas declared_boundaries_passed; is_verified=false,
collision_status=NOT_VALIDATED e autoridade/executable_output=false.
Não modela stock, remoção, ferramenta/fixação reais, NC ou G9.


## Incremento técnico aprovado — CTO-CODEX-CAM-008A

Gemini confirmou integralmente os ajustes de CAM-008 e emitiu CAM-008A em
2026-09-09. Orquestrador interno isolado: BRep -> perfil -> plano sintético ->
verificador -> resultado tipado, sem endpoints/persistência ou pipeline de fresa.
Unidade BRep real explicitada por fator 1.0/1000.0/25.4; tolerâncias explícitas;
zonas obrigatórias; timestamp UTC do chamador (declaração, não relógio confiável).
Metadados imutáveis incluem digest dos parâmetros canonizados e da serialização
BRep nativa, não identidade geométrica canônica, hash do STEP ou Digital Thread.

Falhas CAD/planejamento/verificação abortam os estágios seguintes. Só há
SUCCESS_SYNTHETIC com perfil, plano e relatório PASS de fronteiras declaradas;
NOT_EVALUATED não é sucesso. is_physical_ready/physical_use_authorized/
executable_output=false em todos os casos; controlador permanece não resolvido.


## Decisão técnica — CTO-CODEX-POST-009A

Em 2026-09-09, o CTO acolheu integralmente o conflito POST-009, cancelou a emissão
NC e substituiu a missão por POST-009A, estritamente documental. O pacote
[pré-requisitos do controlador](../engineering/TURNING_CONTROLLER_PREREQUISITES.md)
especifica identidade/manual aplicáveis, semântica real de códigos, valores de
processo, referência de ferramenta/compensação, setup/material remanescente,
trajetórias completas e reverificação após quantização. Nenhum valor real foi
inferido. Códigos citados são itens de investigação, não cabeçalho aprovado.

CTRL/TOOL/SETUP/PATH/POST exigem evidência e revisão; família genérica, formulário
preenchido, hash ou SUCCESS_SYNTHETIC não promovem autoridade. Permanece
CONTROLLER_PROFILE_UNRESOLVED e sem pós-processador de torno. Um próximo marco
possível é a revisão documental de pacote real fornecido por fonte autorizada;
implementação de candidato e G9/operação física continuam marcos separados.


## Marco documental local — CTO-CODEX-STAB-010

Fundação sintética consolidada como v3.2.0-turning-synthetic-alpha, sem tag,
release ou alteração dos manifests/runtime 3.1.0. O marco cobre somente os
incrementos CAD/CAM/verificador/orquestrador/pré-requisitos já delimitados.
CONTROLLER_PROFILE_UNRESOLVED continua bloqueando emissão NC de torno; nenhum
controle físico, publicação ou aprovação G9. Auditoria em ../cto/CTO-CODEX-STAB-010.md.


## Incremento técnico aprovado — CTO-CODEX-AUTO-012A

Após HOLD-011, o CTO emitiu AUTO-012 e acolheu o ajuste de segurança:
AUTO-012A acrescenta apenas TurningQuantizationReport, declaração numérica de
X em diâmetro, reconstrução X/2 e desvio radial assinado (reconstructed-original).
R/X são finitos não negativos; is_boundary_safe=false, boundary_status=
NOT_EVALUATED e limitação literal NUMERICAL_QUANTIZATION_CHECK_ONLY.
Não há Z/zonas/trajectória, quantizador textual, NC, controlador homologado ou
integração Digital Thread. Coerência aritmética não significa segurança física.


## Incremento técnico aprovado — AUTO-015

Após EXEC-014/70e4d13, CTO autoriza função pura de quantização NUMÉRICA em
módulo isolado, sem NC. Política: X=2*R binário, Decimal.from_float exato e
ROUND_HALF_UP em contexto local independente, 1..6 casas (default sintético 3).
Rejeitar overflow e desaparecimento de X positivo; relatório existente permanece
false/NOT_EVALUATED. Não afirma equivalência com decimal ideal ou controlador.

### AUTO-016 — Agregado numérico de extremos (2026-09-09)

Após aprovação AUTO-015 em ebbe37e, agregar ambos os extremos em ordem
start/end por movimento; contagem de movimentos e exatamente 2N relatórios.
Máximo positivo/mínimo negativo incluem zero; validação estrita e falha total
em ponto inválido. Sem quantização de Z, prova de material ou fronteiras.

### AUTO-017 — Quarto estágio numérico (2026-09-09)

Integrar quantização apenas após fronteiras declaradas PASS. Resultado local
synthetic-turning/v2 exige sumário no sucesso; QUANTIZATION_FAILED preserva
artefatos anteriores. Precisão em parâmetros/metadata e hash canônico do sumário;
validar vínculo de contagem/raios/precisão/hash, sem autoridade física ou NC.

### AUTO-018 — Reconstrução radial e reverificação (2026-09-09)

Reconstruir apenas R, preservar Z/IDs/tipos/contagens; recalcular comprimento
de corte e rejeitar segmentos colapsados. Reutilizar verificador de fronteiras
declaradas sem promover PASS a segurança física ou NC. Wrapper isolado do E2E.

### AUTO-019A — Quinto estágio e falhas distintas (2026-09-09)

CTO acolheu separar falha de reconstrução/verificação de violação real. Contrato
v3 exige seis artefatos no sucesso e na violação; falha interna preserva quatro
sem fabricar relatório/plano posterior. Validar vínculos e digest; Z original.
