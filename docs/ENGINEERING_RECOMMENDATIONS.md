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
