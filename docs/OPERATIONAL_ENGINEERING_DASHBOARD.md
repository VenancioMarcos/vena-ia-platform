# Operational Engineering Dashboard v2.0

## Objetivo

A visão de projeto apresenta o workflow integrado e a assistência especializada sem
transportar autoridade de domínio para o navegador. O frontend usa o cliente HTTP
existente e renderiza os contratos versionados do backend.

## Cadeia e estados

A cadeia visível é CAD → Features → Engineering → Process Planning → CNC Neutral →
Integrated Report. Cada etapa mantém seu próprio estado; o status global é
exclusivamente `workflow_status` do backend. Ausência, parcial, bloqueio e falha ficam
visíveis e nunca são substituídos por carregamento infinito.

`COMPLETE_PRELIMINARY` continua `NON_PRODUCTION` e
`REQUIRES_HUMAN_REVIEW`. A confirmação do checklist é estado local de leitura,
nunca aprovação produtiva, certificação ou autorização de fabricação.

## Assistência, Research e evidência

O resultado determinístico e `AI ASSISTANCE` são blocos separados. A interface
expõe status, resposta, evidence references, limitações, warnings, missing evidence,
input trace e citações por documento/página/chunk/método/qualidade. DOE permanece
preliminar e ANOVA apenas descritiva.

Catálogos usam provenance neutra `GLOBAL AUTHENTICATED`; a UI não os apresenta como
recursos da organização. Organization/Team/papel nunca são aceitos do navegador como
autoridade. Auth, ownership e isolamento continuam no backend.

## Segurança CNC

A visão exibe somente `vena-ia.cnc-neutral-plan/v1`, `SIMULATION_ONLY`,
`executable_output=false` e revisão humana. Não há editor, download NC, toolpath,
postprocessor, G/M-code, transmissão ou controle de máquina.

## Validação

Playwright cobre desktop e largura reduzida, navegação por teclado, labels, headings,
status textual, fluxo determinístico, assistência Research/citations, missing inputs,
feature não suportada, ausência de evidence, falha de provider e autorização
fail-closed. Build e typecheck permanecem gates independentes.

## Registro de Entrega

### Objetivo

Consolidar a experiência operacional revisável do Package 3.

### Escopo

Dashboard, tipos públicos, estados, assistência, evidence, revisão humana,
acessibilidade focal e E2E controlado.

### Arquivos criados/modificados

Componentes/tipos/testes em `apps/web`, workflow de Frontend CI e documentação v2.0.

### Testes realizados

Typecheck, build de produção e E2E Playwright em dois viewports; regressão terminal
registrada em `docs/cto/EXECUTION_STATUS.md`.

### Critérios de aceitação

Autoridade no backend, contratos explícitos, falha visível, separação IA/determinismo,
limites científicos e ausência de CNC executável.

### Próximos passos

Revisão do CTO e Owner Release Gate posterior; merge/tag/Release não fazem parte
desta entrega.
