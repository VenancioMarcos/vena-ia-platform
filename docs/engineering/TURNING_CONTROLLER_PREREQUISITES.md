# Torneamento — Pré-requisitos de controlador e pós-processamento

**Status:** Especificação documental; controlador real não selecionado.
**Versão:** 1.0
**Data:** 2026-09-09
**Missão:** CTO-CODEX-POST-009A, substitui a POST-009 cancelada.
**Base técnica:** [ADR-0037](../adr/ADR-0037-turning-geometry-and-toolpath-foundation.md),
[decisões](../DECISIONS.md#dec-047--contratos-propostos-de-torneamento-xz),
[entrega](../cto/CTO-CODEX-POST-009.md), [limites permanentes](../PERMANENT_OPERATIONAL_LIMITS.md).

## 1. Estado e regra de emissão

A cadeia existente produz somente resultados matemáticos sintéticos internos.
Não há perfil real de controlador homologado ou pós-processador de torneamento.
A missão POST-009 tentou fixar códigos genéricos e emitir avanço/recuo sem dados;
o CTO acolheu o conflito e cancelou a geração NC, autorizando este documento.

CONTROLLER_PROFILE_UNRESOLVED bloqueia emissão NC de torneamento. O estado
SUCCESS_SYNTHETIC não resolve esse bloqueio e não atesta ausência de colisão real.
Os campos is_physical_ready, physical_use_authorized, executable_output,
is_collision_free e is_verified permanecem false; collision_status=NOT_VALIDATED.
G9=PENDING_AUTHORITATIVE_REVIEW; NON_PRODUCTION. Sem envio à máquina, DNC,
transferência NC, cycle start, push, merge, tag, release ou deploy.

Um formulário preenchido é uma declaração. Uma referência de manual é evidência
para revisar uma semântica específica. Nenhum dos dois, isoladamente, homologa
trajetória, pós-processador, segurança física ou autoridade humana de G9.

## 2. O que existe e o que ainda falta

| Camada | Implementação local e evidência | Limite atual | Dependência seguinte |
| --- | --- | --- | --- |
| CAD STEP-005 | Perfil radial/Z de cilindros externos simples/escalonados; comparação BRep por reconstrução booleana | Datum/unidade/tolerância declarados; não cobre furos, cones ou geometrias gerais | Peça e datum reais com revisão de equivalência e tolerâncias |
| CAM-006A | Faceamento e desbaste linear de ponto ideal com sobremetais explícitos | Sem pastilha, porta-ferramenta, valor de avanço ou processo físico | Referência e geometria reais da ferramenta, stock/setup, condições de corte |
| CAM-007A | Interseção contínua contra plano axial e retângulos estáticos declarados | AABB sintética; sem remoção/material remanescente ou fixação real | Geometria/proveniência de corpos, material por estágio e trajetórias físicas |
| CAM-008A | Orquestrador interno, falhas por estágio, metadados imutáveis e replay | Hash de parâmetros separado da serialização BRep; sem hash do STEP original ou Digital Thread | Rastreabilidade revisada dos artefatos reais e contrato de integração separado |
| ControllerProfileRequirement | ID/modo X/modo de avanço declarados | Sempre CONTROLLER_PROFILE_UNRESOLVED | Identidade exata, manual e mapeamento revisado |
| Pós de torno | Nenhum emissor implementado | Não existe candidato NC desta cadeia | Resolver entradas e contratar validação do pós antes de implementar |

Referências de código: [extrator](../../apps/api/app/modules/cad/profile_extractor.py),
[planejador](../../apps/api/app/modules/engineering/turning_planner.py),
[verificador](../../apps/api/app/modules/engineering/turning_verifier.py),
[orquestrador](../../apps/api/app/modules/engineering/turning_service.py),
[contratos mínimos](../../apps/api/app/modules/engineering/turning_schemas.py),
[contratos sintéticos](../../apps/api/app/modules/engineering/turning_toolpath_schemas.py).
Baseline 5f50559: 548 testes API aprovados e 2 ignorados por Redis real não
habilitado. A contagem cobre toda a suíte API, não 548 testes exclusivos de torno.

## 3. Matriz obrigatória de requisitos

Cada linha começa PENDENTE. Para revisão, fornecer o valor declarado, unidade,
fonte primária com revisão/seção/página, evidência de aplicabilidade à máquina
e registro da avaliação técnica. Conflitos ficam EM_REVISAO; não escolher o
valor mais conveniente. Valores de exemplo neste documento não preenchem a matriz.

| ID | Informação necessária | Evidência exigida | Condição que impede avançar |
| --- | --- | --- | --- |
| CTRL-01 | Fabricante/modelo exato da máquina e do controlador; identificação interna opaca | Documentação do equipamento e confirmação de correspondência | Família genérica ou modelo presumido |
| CTRL-02 | Versão de firmware/software e sistema/opções de códigos ativos | Manual/revisão aplicável e configuração confirmada sem credenciais | Versão, sistema ou opção desconhecidos |
| CTRL-03 | Manual de programação/operação: título, ID, revisão, idioma, seções | Fonte oficial verificável; hash do arquivo efetivamente recebido quando cabível | Manual de outro produto, referência não consultada ou só mensagem de IA |
| AXIS-01 | Eixos, sentidos positivos e plano de interpolação efetivos | Diagramas e descrição no manual aplicável | Assumir G18 ou sentido de aproximação sem mapeamento |
| AXIS-02 | X programado em raio/diâmetro, unidades e convenção absoluta/incremental | Referência documental e configuração ativa | Dobrar raio duas vezes, assumir G90 universal ou misturar datum/unidade |
| AXIS-03 | Datum da peça, sistema de coordenadas e offsets relevantes | Desenho/setup revisados e mecanismo documental de offsets | Usar a origem sintética como posição física comprovada |
| FEED-01 | Modo semântico por minuto/rotação e código correspondente nesse sistema | Tabela de códigos e condições modais do manual exato | Inferir G94/G95 pela família ou pelos códigos da fresa |
| FEED-02 | Valor de avanço por operação, unidade, fonte e validade para material/ferramenta | Dados técnicos aplicáveis e revisão de engenharia | Há somente feed_rate_type ou valor F inventado |
| SPIN-01 | RPM fixa/CSS, códigos reais, direção e limites de aplicação | Manual e dados do spindle, fixação e processo | Inventar rotação, sentido ou selecionar modo por default |
| SPIN-02 | Teto de RPM aplicável e precedência dos limites | Limites revisados de máquina, placa/castanhas, peça, ferramenta e setup | CSS sem teto ou teto sem evidência de aplicabilidade |
| SPIN-03 | RPM/Vc numéricos e política perto do centro/transições | Fonte de processo e análise revisada do comportamento do comando | Valor CSS isolado ou extrapolação ao centro sem análise |
| TOOL-01 | Ferramenta/inserto/suporte exatos e geometria do conjunto | Desenho/catálogo/medição com revisão e referência dimensional | Só raio de ponta ou AABB sintética declarada |
| TOOL-02 | Ponto programado: ponta teórica, centro do raio ou outra referência | Diagrama de referência e convenção do pós/comando | Misturar ponto ideal e referência física |
| TOOL-03 | Offset de ferramenta, estratégia de compensação e responsável pelo cálculo | Manual, contrato de referência e validação da estratégia | Aplicar compensação duas vezes ou inferir G41/G42 |
| TOOL-04 | Orientação/identificador de quadrante e ângulos de ataque/saída | Mapeamento específico do fabricante/comando e geometria aplicável | Considerar 1–9 um vetor universal ou ignorar corpo não cortante |
| SETUP-01 | Stock real, datum, dimensão, material e tolerâncias | Desenho/registro revisado do bruto e da peça | Só parâmetros sintéticos ou stock sem posição comprovada |
| SETUP-02 | Placa/castanhas, aperto, balanço, contraponto e exclusões aplicáveis | Geometria e setup revisados; folgas com origem declarada | Plano Z sintético tratado como envelope físico completo |
| SETUP-03 | Material remanescente por estágio e região cortante/não cortante | Modelo validado de remoção ou abordagem conservadora justificada | Checar haste contra stock ausente ou remover material por inferência |
| PATH-01 | Posição física inicial e condições modais exigidas | Contrato de inicialização e revisão dos movimentos completos | Emissão começa em posição desconhecida ou omite start_point |
| PATH-02 | Aproximação inicial, transições e retrações de cada operação | Trajetória física contínua verificada com setup/corpos/material | Mapear RETRACT automaticamente para rápido ou avanço |
| PATH-03 | Ponto/rota de troca e término; referência máquina/peça explícita | Manual e setup; verificação do caminho inteiro | Supor home, G28 ou G53 como recuo universal seguro |
| POST-01 | Sintaxe, modos, numeração, unidades, feed/spindle/coolant/fim | Perfil versionado e semântica revisada de cada emissão | Cabeçalho universal ou tabela sem vínculo ao manual |
| POST-02 | Resolução de X/Z/F/S, casas, arredondamento e limites numéricos | Manual/configuração e política do formatador proposta | Três casas por conveniência, NaN/Inf/overflow ou valor não representável |
| POST-03 | Reconstrução e reverificação do caminho a partir do texto quantizado | Leitor/verificador independente do formato alvo e testes de fronteira | Só testar string ou comparar plano anterior ao arredondamento |
| TRACE-01 | Vínculo peça/setup/ferramenta/controlador/planos/versões/revisões | Pacote rastreável imutável com hashes e escopo de evidência | Hash de serialização tratado como aprovação ou identidade canônica |
| REVIEW-01 | Critérios e registros das revisões técnicas necessárias | Registro explícito de escopo, evidência e autoridade competente | Declaração de IA ou flag do cliente promovida a aprovação humana |

A coluna de códigos identifica assuntos a comprovar; não fornece um cabeçalho.
G18, G90, G94/G95, G96/G97, G50, G41/G42, G28/G53 e códigos M só poderão aparecer
num futuro perfil após comprovação de sua semântica e aplicabilidade específicas.

## 4. Contraexemplo documental ao dialeto universal

A [lista oficial de torno Haas](https://www.haascnc.com/service/service-content/guide-procedures/lathe---g-codes.html),
reverificada em 2026-09-09, associa G90 a ciclo de torneamento, G94 a ciclo de
faceamento e G95 a rosqueamento rígido com ferramenta acionada. Portanto esses
códigos não podem ser fixados universalmente como absoluto/avanço por minuto/
avanço por rotação. Isso não seleciona Haas para a plataforma e não prova a
semântica de qualquer Fanuc, Siemens, Mitsubishi ou outro controlador.

Os campos de processo devem primeiro declarar a semântica desejada e sua unidade;
um futuro perfil específico traduz essa semântica para códigos documentados.
Nomear uma família GENERIC_LATHE_ISO não substitui tal evidência.

## 5. Quantização e reverificação do resultado textual

A conversão matemática interna, quando o perfil real exigir diâmetro, é X*=2R.
A saída textual usa Q(X*), onde Q é a política de quantização explicitamente
selecionada para o comando. Em geral Q(2R) não é exatamente 2R. O raio representado
pelo texto será R_texto=Q(2R)/2, e deve ser esse valor reconstruído que entra no
verificador independente posterior. Z_texto também precisa ser reconstruído.

Exemplo puramente decimal: R=12.34526 mm implica X*=24.69052 mm. Arredondar X para
três casas ao valor mais próximo dá 24.691 mm e R_texto=12.3455 mm, diferença
radial de +0.00024 mm. Isso não autoriza três casas para nenhuma máquina real.

Para arredondamento ao mais próximo com passo q_X, o erro textual de X é no
máximo q_X/2 e o erro radial é no máximo q_X/4. Analogamente, erro de Z no máximo
q_Z/2. Esses limites são apenas matemáticos sob a política declarada, excluindo
erros anteriores de representação/cálculo, precisão do comando e erro físico.
Truncamento, arredondamento direcionado e outras políticas têm limites distintos.

Exemplo de fronteira: um ponto Z=-9.9996 mm fica acima da zona proibida Z<=-10 mm;
arredondado a três casas torna-se Z=-10.000 mm e toca a fronteira, que é violação
no contrato sintético atual. Um verificador anterior à formatação não cobre isso.

O futuro contrato deve definir: tratamento de empates e zero com sinal, precisão
decimal por eixo/grandeza, faixa representável, overflow/underflow, rejeição de
NaN/Inf, finitude após conversão, movimentos que colapsam a comprimento zero e
alteração de monotonicidade/continuidade por arredondamento. Também deve conferir
unidade/modos/offsets/compensação que determinam o significado de cada coordenada.

Critério futuro: ler de volta a saída exata, reconstruir todos os movimentos
incluindo aproximação/transições/término e repetir verificação independente contra
as fronteiras físicas aplicáveis. Comparar com o plano de origem e registrar
erros dentro de limites revisados. Não usar tolerância CAD como tolerância de
fabricação ou margem automática de colisão. Esta missão não implementa esse pós.

## 6. Template para coleta futura de dados

Preencher somente dados técnicos não confidenciais autorizados para o projeto.
Usar IDs internos opacos para equipamento, setup e registro de revisão. Não incluir
senha, token, endereço de rede, acesso remoto, número de série sensível ou dados de
cliente. Não é necessário criar conta ou conceder acesso para preencher o pacote.
PENDENTE significa ausência de evidência, não zero, default ou aprovação.

```text
PACOTE: TURNING_CONTROLLER_INTAKE_V1
ESTADO: DECLARADO_PENDENTE_DE_REVISAO
CONTROLLER_PROFILE_STATUS: CONTROLLER_PROFILE_UNRESOLVED
PHYSICAL_USE_AUTHORIZED: false
G9: PENDING_AUTHORITATIVE_REVIEW

IDENTIDADE
  equipamento_id_interno: PENDENTE
  fabricante_modelo_maquina: PENDENTE
  fabricante_modelo_controlador: PENDENTE
  firmware_software_versao: PENDENTE
  sistema_de_codigos_e_opcoes_ativas: PENDENTE
  evidencia_de_correspondencia_ao_equipamento: PENDENTE

REFERENCIAS
  manual_titulo_id_revisao_idioma: PENDENTE
  fonte_oficial_url_ou_arquivo_autorizado: PENDENTE
  secoes_paginas_e_condicoes_de_aplicacao: PENDENTE
  digest_arquivo_efetivamente_recebido_se_aplicavel: PENDENTE

EIXOS_DATUM_E_MODOS
  unidade_e_resolucao_por_eixo: PENDENTE
  x_raio_ou_diametro_e_evidencia: PENDENTE
  plano_e_sentidos_positivos: PENDENTE
  absoluto_incremental_e_semantica_documentada: PENDENTE
  datum_e_offsets_peca_maquina: PENDENTE

PROCESSO
  material_stock_e_descricao_peca_autorizada: PENDENTE
  modo_semantico_de_avanco_e_unidade: PENDENTE
  valor_F_por_operacao_fonte_validade_e_revisao: PENDENTE
  modo_spindle_rpm_ou_css_e_direcao: PENDENTE
  rpm_ou_vc_valor_unidade_fonte_e_revisao: PENDENTE
  teto_rpm_limites_concorrentes_e_justificativa: PENDENTE
  politica_centro_transicoes_coolant_e_parada: PENDENTE

FERRAMENTA_E_SETUP
  ferramenta_inserto_suporte_geometria_e_fonte: PENDENTE
  ponto_programado_e_referencia_do_raio: PENDENTE
  offsets_estrategia_e_responsavel_por_compensacao: PENDENTE
  orientacao_quadrante_diagrama_e_limites_angulares: PENDENTE
  stock_posicao_dimensoes_material_e_tolerancias: PENDENTE
  placa_castanhas_aperto_balanco_e_outros_corpos: PENDENTE
  exclusoes_folgas_reais_e_fontes: PENDENTE
  material_remanescente_por_estagio_e_metodo: PENDENTE

TRAJETORIAS_E_QUANTIZACAO
  estado_posicao_inicial_e_modais: PENDENTE
  aproximacao_transicoes_retracoes_e_saida: PENDENTE
  ponto_rota_de_troca_referencia_e_verificacao: PENDENTE
  resolucao_casas_e_politica_de_arredondamento: PENDENTE
  limites_de_erro_e_representacao_por_grandeza: PENDENTE
  metodo_independente_de_releitura_e_reverificacao: PENDENTE

RASTREABILIDADE_E_REVISAO
  versoes_e_vinculos_peca_setup_ferramenta_controlador: PENDENTE
  evidencias_testes_e_limites_de_cobertura: PENDENTE
  registro_de_revisao_id_escopo_e_papel_responsavel: PENDENTE
  conflitos_e_pendencias_nao_resolvidos: PENDENTE
  decisao_tecnica_documentada: PENDENTE
```

## 7. Contrato de revisão e próximo marco

1. Receber o pacote autorizado e conferir a identidade do comando e a referência
   primária. Anotar dados não verificáveis e conflitos, sem preencher por inferência.
2. Revisar separadamente semântica de códigos, referência de ferramenta, setup,
   material, dados de corte, trajetória completa e quantização. Cada conclusão deve
   apontar evidência específica e limites de aplicabilidade.
3. Elaborar uma especificação de pós para um único perfil exato, com critérios
   positivos/negativos e método de releitura/reverificação da saída. A aprovação
   dessa especificação deve declarar se autoriza apenas implementação local futura.
4. Implementação de candidato, integração no runtime/Digital Thread e revisão G9
   são marcos distintos, cada qual com seu escopo e evidências. Nenhum formulário,
   teste sintético ou parecer de IA autoriza a execução física.

O próximo marco disponível é a revisão documental do pacote real, se ele for
fornecido por fonte autorizada. Sem isso, o CTO pode definir trabalho sintético
ou documental adicional de escopo próprio, mas a emissão NC permanece bloqueada.
Não instalar automações, publicar arquivos ou solicitar acessos por inferência.

## 8. Critérios de aceitação desta entrega documental

- Mapeamento completo entre as quatro camadas locais e suas limitações reais.
- Identidade e semântica exigidas por evidência, sem códigos universais fixos.
- Ausências de F, ferramenta/setup e material remanescente explicitadas.
- Quantização separada de conversão ideal, com exemplos e reverificação proposta.
- Template preenchível sem dados secretos e sem valores/aprovações inventados.
- Emissão bloqueada, nenhuma implementação NC e nenhuma promoção de autoridade.
