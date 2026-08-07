# Registro de Riscos

**Data da revisão:** 2026-08-06

| ID | Severidade | Risco e evidência | Mitigação recomendada | Estado |
|---|---|---|---|---|
| R-001 | CRÍTICO | Identidade era aceita pelo header `X-User-ID`. | Substituído por JWT assinado, cookie HttpOnly/Bearer e identidade carregada do banco. | MITIGADO v0.4.1 |
| R-002 | CRÍTICO | Cadastro permitia autoatribuição de `admin`. | Cadastro rejeita `role`, força `member` e não expõe promoção pública. | MITIGADO v0.4.1 |
| R-003 | ALTO | Rotas não aplicavam autorização uniforme por proprietário. | Autorização centralizada protege usuários, projetos, arquivos, documentos, chats e IA. | MITIGADO v0.4.1 |
| R-004 | ALTO | Upload confiava em extensão/MIME controlados pelo cliente. | Allowlist exclusiva de PDF, MIME exato, `%PDF-`, tamanho e caminho interno seguro. | MITIGADO v0.4.1 |
| R-005 | ALTO | Respostas RAG poderiam não ter vínculo verificável com a origem documental. | Busca retorna documento, página, chunk e score; geração recebe apenas trechos recuperados e os trata como dados não confiáveis. | MITIGADO v0.5 |
| R-018 | MÉDIO | Embeddings dependem de provedor externo e dimensão fixa compatível com a coluna vetorial. | Configuração explícita, contagem/dimensão/vetores finitos, timeout/retry classificado e falha segura antes da persistência. | MITIGADO PARCIALMENTE v1.6 PACKAGE 2 / MONITORAR |
| R-019 | ALTO | Envelope calculado por pontos STEP pode divergir da bounding box topológica e volume não é confiável sem kernel geométrico. | OCCT controlado separa metadata textual de propriedades topológicas e valida box/área/volume/corpus; formas fora da fronteira validada e tolerância industrial permanecem sob revisão. | MITIGADO PARCIALMENTE v1.8 PACKAGES 2–4 / MONITORAR |
| R-039 | ALTO | Binding geométrico nativo pode ampliar crash de processo, ABI, supply chain e timeout não preemptivo. | Versão fixada, import lazy, limite de arquivo, corpus sintético e erro seguro; isolamento/preempção permanecem gate posterior. | MONITORAR v1.8 PACKAGE 2 |
| R-040 | ALTO | Reconhecimento incorreto de feature pode transformar primitiva geométrica em intenção de fabricação inexistente. | Rule versionada e conservadora separa primitivas de features, exige evidência topológica estrita, corpus de falsos positivos/negativos, referências locais e revisão humana; closed hole/slot são adiados. | MITIGADO PARCIALMENTE v1.8 PACKAGE 3 / MONITORAR |
| R-041 | ALTO | Feature válida pode ser convertida indevidamente em decisão ou liberação de processo. | Bridge allowlisted produz apenas candidate não executável, exige feature evidence/review válido, falha fechado para contexto ausente e reutiliza recommendation v1.7 somente com catálogos explícitos. | MITIGADO PARCIALMENTE v1.8 PACKAGE 4 / MONITORAR |
| R-042 | CRÍTICO | A fronteira Organization/Team pode permitir escalada de papel ou acesso cruzado entre organizações/equipes. | Package 1 usa identidade apenas do token/banco, memberships allowlisted, menor privilégio, owner transacional, índices únicos, cross-organization/team 404, schemas anti-mass-assignment, revogação e auditoria. Testes sintéticos cobrem falsificação, self-promotion e isolamento. | MITIGADO PARCIALMENTE v1.9 PACKAGE 1 / MONITORAR |
| R-043 | ALTO | Evidence parcial/stale, checklist incompleto, checksum divergente ou rollback falho pode ser interpretado como falsa prontidão de piloto. | Estados fechados nunca promovem PARTIAL/FAILED/NOT_AVAILABLE; privacy e contexto são gates; verificação canônica retorna MATCH/MISMATCH; rollback falho bloqueia; toda saída exige revisão humana e não produção. | MITIGADO PARCIALMENTE v1.9 PACKAGE 2 / MONITORAR |
| R-020 | ALTO | Parâmetros de corte genéricos podem ser inadequados para ferramenta, material, fixação ou máquina reais. | Package 2 v1.7 exige fonte/versão, falha explícita para dado ausente, aplica limites declarados e revisão humana; nunca gera ou envia código para máquina. | MITIGADO PARCIALMENTE v1.7 PACKAGE 2 / MONITORAR |
| R-021 | CRÍTICO | Estruturas CNC preliminares poderiam ser confundidas com saída liberada para máquina. | Não gerar G-code; marcar simulação/revisão humana e `executable_output=false`; proibir transmissão e produção. | MONITORAR v0.8 |
| R-022 | ALTO | Referências heurísticas podem ser separadas ou interpretadas incorretamente. | Preservar texto bruto, página, método e estado preliminar; exigir revisão humana. | MONITORAR v0.9 |
| R-023 | MÉDIO | Metadados bibliográficos podem estar incompletos ou incorretos. | Registrar origem; manter ausentes como nulos; não consultar ou inventar DOI/autores/título. | MONITORAR v0.9 |
| R-024 | ALTO | Sínteses podem alucinar ou extrapolar evidências recuperadas. | Grounding obrigatório no RAG, evidências por documento/página/chunk e revisão humana. | MONITORAR v0.9 |
| R-025 | ALTO | Artigos podem conter prompt injection. | Tratar chunks como dados não confiáveis, reforçar prompt do sistema e testar instruções maliciosas. | MONITORAR v0.9 |
| R-026 | ALTO | Saídas preliminares podem ser usadas como conclusão científica. | Estados explícitos de revisão e limitações em sínteses, DOE, ANOVA e relatórios. | MONITORAR v0.9 |
| R-027 | ALTO | Preparação ANOVA pode ser confundida com inferência validada. | Não calcular F, valor-p ou significância; expor somente resumo descritivo e checklist. | MONITORAR v0.9 |
| R-028 | CRÍTICO | Recursos científicos poderiam vazar entre projetos. | AuthorizationService em todos os recursos; identidade somente do JWT; acesso negado como 404. | MONITORAR v0.9 |
| R-029 | ALTO | Biblioteca preliminar pode ser apresentada como revisão sistemática. | Documentar exclusão de PRISMA, bases externas, meta-análise e publicação. | MONITORAR v0.9 |
| R-030 | ALTO | Rate limiting de autenticação precisava compartilhar estado entre réplicas. | Redis aplica incremento/TTL atômicos nas rotas de cadastro/login e falha fechado; gateway confiável continua necessário para topologias com proxy. | MITIGADO PARCIALMENTE v1.2 PACKAGE 4 / MONITORAR PROXY |
| R-031 | ALTO | PostgreSQL e MinIO não possuíam recuperação verificável. | Packages 1–3 adicionam contratos, restore combinado, AES-256-GCM, retenção segura e drill mensurado; repetição operacional, custódia de chaves e critérios formais pré-piloto ainda exigem aceite. | MITIGADO PARCIALMENTE v1.3 PACKAGE 3 / REVISÃO PRÉ-PILOTO |
| R-032 | MÉDIO | Métricas e tracing existem somente no processo, sem retenção ou backend operacional externo. | Packages 2–3 fecham cardinalidade, documentam reinício/réplicas e geram evidência reproduzível; selecionar backend/exportação somente em gate futuro autorizado. | MITIGADO PARCIALMENTE v1.4 PACKAGE 3 / MONITORAR |
| R-033 | ALTO | Chat/RAG depende de PostgreSQL, MinIO, pgvector e provedor de IA. | Budgets, retry bounded, backpressure, readiness, alertas e drills demonstram falha/recuperação sem resposta falsa; dependências continuam externas. | MITIGADO PARCIALMENTE v1.6 PACKAGE 2 / MONITORAR |
| R-035 | ALTO | Relatórios aceitavam evidência declarada sem verificar correspondência com o chunk persistido. | Validar documento, página, índice e trecho antes de persistir o relatório. | MITIGADO v1.1 |
| R-036 | MÉDIO | Requisições sem timeout, falhas silenciosas e dependência da listagem de relatórios podiam bloquear ou confundir o fluxo principal do frontend. | Cliente API único com timeout; erros de logout/chat visíveis; relatórios carregados sem impedir projeto, documentos e histórico. | MITIGADO v1.1 |
| R-037 | BAIXO | Operações do frontend recarregavam até quatro endpoints mesmo quando a resposta já continha o recurso atualizado. | Atualizar localmente o recurso retornado e, em falha, sincronizar somente documentos ou histórico; cancelar requests no unmount. | MITIGADO v1.1 |
| R-034 | MÉDIO | Não há deploy, capacidade produtiva ou escalabilidade validados. | Gate descartável usa duas APIs/dois workers reais e PostgreSQL/Redis/MinIO compartilhados, com carga/soak limitados; ambiente alvo, piloto e sizing produtivo continuam obrigatórios. | MITIGADO PARCIALMENTE v1.6 PACKAGE 3 R1 / MONITORAR |
| R-006 | MÉDIO | O frontend apresentava textos históricos enquanto backend e roadmap avançavam. | Textos operacionais foram atualizados e as versões de API/frontend unificadas em 1.0.0. | MITIGADO v1.0 |
| R-007 | MÉDIO | Não havia lockfile frontend; o CI usava instalação não congelada. | `pnpm-lock.yaml` versionado e CI usa `pnpm install --frozen-lockfile`. | MITIGADO v0.4.1 |
| R-008 | MÉDIO | O ambiente local auditado usa Python 3.14.6, enquanto o runtime oficial é Python 3.13.11. | Matriz/manifesto alinham CI, container e local recomendado em 3.13.11; regressão 3.14.6 passa, mas permanece experimental e não bloqueia o gate oficial. | MITIGADO v1.6 PACKAGE 1 / 3.14 EXPERIMENTAL |
| R-009 | MÉDIO | Imagens flutuantes podiam alterar runtime sem mudança no Git. | Todas as bases/serviços usam tag explícita + digest; policy fail-closed proíbe `latest` e runbook exige revisão/rollback. | MITIGADO v1.6 PACKAGE 1 |
| R-010 | MÉDIO | Eventos sensíveis precisavam de correlação persistente com requests e mutações operacionais. | Packages 1–3 adicionam schema/redaction, IDs persistidos, retenção de auditoria em PostgreSQL e drill integral com evidência allowlisted. | MITIGADO v1.4 PACKAGE 3 |
| R-011 | BAIXO | Existe `.env` local real, embora ignorado e sem segredo detectado na auditoria. | Manter ignorado, limitar permissões e revisar antes de qualquer empacotamento. | MONITORAR |
| R-012 | BAIXO | A suíte gerava aviso de depreciação de `TestClient`/HTTPX. | Dependência de desenvolvimento migrada para HTTPX2 e imports direcionados ao cliente Starlette compatível. | MITIGADO v1.1 |
| R-013 | MÉDIO | Logout precisava compartilhar revogação entre réplicas e reinícios. | Redis guarda somente chave derivada do fingerprint com TTL do JWT; falha de Redis bloqueia consulta e escrita com auditoria. | MITIGADO v1.2 PACKAGE 4 |
| R-014 | MÉDIO | Usuários legados preservados pela migration podem não possuir hash de senha. | Admin define credencial ausente uma única vez, com auditoria, política oficial e invalidação das sessões anteriores. | MITIGADO v1.2 PACKAGE 3 |
| R-015 | BAIXO | O contexto Docker do Web incluía artefatos locais (`node_modules` e `.next`), ampliando o build para centenas de MB. | `.dockerignore` dedicado reduz o contexto a arquivos-fonte e exclui ambientes, dependências, builds e logs locais. | MITIGADO v0.4.1 |
| R-016 | MÉDIO | A ingestão de PDF da fundação v0.5 ocorria de forma síncrona na requisição HTTP. | Jobs duráveis, recovery/lease/idempotência e dois workers controlados sem duplicação; capacidade real de PDF ainda depende de piloto. | MITIGADO PARCIALMENTE v1.6 PACKAGE 3 / MONITORAR |
| R-017 | MÉDIO | PDFs criptografados ou sem camada textual não geram chunks. | Falha explícita possui códigos seguros; avaliação formal B adia OCR até isolamento, corpus, qualidade, custo e aprovação humana. | ABERTO / OCR ADIADO v1.5 PACKAGE 2 |
| R-038 | MÉDIO | Timeout cooperativo não interrompe à força uma biblioteca síncrona bloqueada e efeitos parciais podem preceder o término. | Deadline/retry impedem novas tentativas e recusam resultado tardio; lease, cancelamento e recovery preservados. Processo isolado/preemptivo continua gate futuro. | MONITORAR v1.6 PACKAGE 2 |

## Tratamento planejado v1.2–v2.0

| Gate | Riscos principais | Condição de saída |
|---|---|---|
| v1.2 Security and Data Protection | R-030, R-013, R-014 | rate limiting, revogação de sessão e credencial legada auditável; o Package 1 mitiga apenas cadastro/login e não substitui o limite distribuído |
| v1.3 Backup and Recovery | R-031, R-011 | restore testado de PostgreSQL/MinIO, checksums, retenção e nenhum artefato sensível no Git |
| v1.4 Observability and Auditability | R-010, R-032, R-033 | logs correlacionados/redigidos, auditoria, readiness, métricas e runbooks |
| v1.5 Asynchronous Processing | R-016, R-017, R-033 | jobs idempotentes, retry/recovery e OCR somente após gate de qualidade/segurança |
| v1.6 Reliability and Scalability | R-008, R-009, R-018, R-034 | runtimes/imagens reproduzíveis, resiliência e capacidade medidas |
| v1.7 Engineering Catalogs and CAM | R-020 | dados/rules rastreáveis, limites de máquina e revisão humana |
| v1.8 CAD Interoperability | R-019 | kernel decidido por ADR e propriedades validadas contra corpus conhecido |
| v1.9 Controlled Pilot Readiness | R-021 a R-029 | isolamento, restore, SLOs e simulação controlada; nenhuma transmissão CNC |
| v2.0 Integrated Engineering Platform | riscos residuais | dono, prazo, controle e aceite registrados; deploy permanece missão separada |

## Segurança de segredos

- `.env` está ignorado pelo Git e não aparece no histórico.
- Nenhum padrão conhecido de chave OpenAI, token GitHub, chave AWS ou chave privada
  foi encontrado nos arquivos rastreados nem no histórico Git local.
- `.env.example` contém somente placeholders; `OPENAI_API_KEY` e
  `AUTH_SECRET_KEY` estão vazios.
- Nenhum arquivo de credencial, cookie, chave privada ou dado pessoal foi localizado.
- A verificação por padrões não substitui secret scanning dedicado no CI.

## Classificação CNC

CAD, CAM, CNC, geração de G-code e simulação estão ausentes ou apenas reservados
em documentação. Não existe saída CNC para validar. Qualquer implementação futura
permanece `REQUIRES_HUMAN_REVIEW` até aprovação de um processo completo de
validação e simulação.
