# Recomendações preliminares de engenharia v1

`POST /engineering/recommendations/preliminary` aceita itens versionados de
material, máquina e ferramenta e uma operação allowlisted (`milling`, `drilling`
ou `turning`). A identidade vem exclusivamente da autenticação existente.

RPM e feed usam fórmulas explícitas e limites declarados. Tempo usa somente
comprimento reto informado, sem criar toolpath. Custo usa taxa/hora e componentes
fornecidos, sem preço externo, e não constitui orçamento comercial. Valores
ausentes ou inválidos retornam `NOT_AVAILABLE`.

Unidades: mm, m/min, rpm, mm/min e minutos; moeda é código explícito de três letras.
Arredondamento: parâmetros em duas casas, tempo em três e custo em duas.

Toda resposta contém `PRELIMINARY_ENGINEERING_REQUIRES_HUMAN_REVIEW`. Não há
coordenadas, offsets, G-code, M-code, toolpath, transmissão ou controle CNC.

`POST /engineering/reports/preliminary` reutiliza integralmente a recomendação e
gera JSON versionado com conclusão segura, itens indisponíveis, rastreabilidade,
incerteza baseada somente na completude dos dados e checklist humano nunca
preenchido automaticamente. A incerteza não representa segurança física.

## Ownership e compatibilidade v2.1 Package 1

Itens criados pela API são `ORGANIZATION_OWNED`. A criação exige `organization_id`
na query e membership OWNER/ADMIN no banco; qualquer membership ativa pode listar.
Sem organização, a listagem retorna somente `SYSTEM_REFERENCE` autenticada.
`LEGACY_UNSCOPED` nunca entra em selection/recommendation.

`scope_type` e `organization_id` são aditivos ao contrato v1. Mistura cross-org falha
fechado. Código/versão iguais podem existir em organizações distintas; referências de
sistema preservam unicidade global.

Governance evidence pode ser consultada individualmente em
`GET /engineering/catalogs/{catalog_id}/governance`; a mesma autorização vale antes
da composição. Limites: `docs/ENGINEERING_GOVERNANCE_EVIDENCE.md`.

No RC v2.1.0, selection, recommendation e review report preservam schemas v1;
nenhum scope legado ou cross-org é promovido por compatibilidade.

## Uso no workflow integrado v2.0 Package 1

O `IntegratedEngineeringWorkflowService` reutiliza `recommend()` uma única vez e
passa o mesmo objeto a `report_from_recommendation()`. Fórmulas, RPM, feed, tempo,
custo, compatibilidade e report builder não são duplicados. Inputs adicionais de
processo permanecem explícitos no planning; ausência ou incompatibilidade nunca vira
aprovação. O contrato e limites completos estão em
`docs/INTEGRATED_ENGINEERING_WORKFLOW.md`.
