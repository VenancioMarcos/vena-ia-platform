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

## Uso no workflow integrado v2.0 Package 1

O `IntegratedEngineeringWorkflowService` reutiliza `recommend()` uma única vez e
passa o mesmo objeto a `report_from_recommendation()`. Fórmulas, RPM, feed, tempo,
custo, compatibilidade e report builder não são duplicados. Inputs adicionais de
processo permanecem explícitos no planning; ausência ou incompatibilidade nunca vira
aprovação. O contrato e limites completos estão em
`docs/INTEGRATED_ENGINEERING_WORKFLOW.md`.
