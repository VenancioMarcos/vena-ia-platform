# Registro de Riscos

**Data da revisão:** 2026-08-07

| ID | Severidade | Risco e evidência | Mitigação recomendada | Estado |
|---|---|---|---|---|
| R-001 | CRÍTICO | Identidade era aceita pelo header `X-User-ID`. | Substituído por JWT assinado, cookie HttpOnly/Bearer e identidade carregada do banco. | MITIGADO v0.4.1 |
| R-002 | CRÍTICO | Cadastro permitia autoatribuição de `admin`. | Cadastro rejeita `role`, força `member` e não expõe promoção pública. | MITIGADO v0.4.1 |
| R-003 | ALTO | Rotas não aplicavam autorização uniforme por proprietário. | Autorização centralizada protege usuários, projetos, arquivos, documentos, chats e IA. | MITIGADO v0.4.1 |
| R-004 | ALTO | Upload confiava em extensão/MIME controlados pelo cliente. | Allowlist exclusiva de PDF, MIME exato, `%PDF-`, tamanho e caminho interno seguro. | MITIGADO v0.4.1 |
| R-005 | ALTO | Respostas RAG poderiam não ter vínculo verificável com a origem documental. | Busca retorna documento, página, chunk e score; geração recebe apenas trechos recuperados e os trata como dados não confiáveis. | MITIGADO v0.5 |
| R-018 | MÉDIO | Embeddings dependem de provedor externo e dimensão fixa compatível com a coluna vetorial. | Configuração explícita, contagem/dimensão/vetores finitos, timeout/retry classificado e falha segura antes da persistência. | MITIGADO PARCIALMENTE v1.6 PACKAGE 2 / MONITORAR |
| R-019 | ALTO | Envelope calculado por pontos STEP pode divergir da bounding box topológica e volume não é confiável sem kernel geométrico. | OCCT controlado separa metadata textual de propriedades topológicas; evidence v1 registra hash, topologia, bounds, métricas, unidades e provenance sobre corpus sintético. Formas fora da fronteira e tolerância industrial permanecem sob revisão. | MITIGADO PARCIALMENTE v2.2 PACKAGE 1 / MONITORAR |
| R-039 | ALTO | Binding geométrico nativo pode ampliar crash de processo, ABI, supply chain e timeout não preemptivo. | Versão fixada/import lazy, limite de arquivo e de elementos, corpus sintético e erro seguro; isolamento/preempção de crash nativo permanecem gate posterior. | MITIGADO PARCIALMENTE v2.2 PACKAGE 1 / MONITORAR |
| R-040 | ALTO | Reconhecimento incorreto de feature pode transformar primitiva geométrica em intenção de fabricação inexistente. | Evidence geral v1 separa classificação geométrica de feature/manufatura, registra ambiguidades e mantém rule de features conservadora; falsos claims e regressão são testados, com revisão humana obrigatória. | MITIGADO PARCIALMENTE v2.2 PACKAGE 1 / MONITORAR |
| R-041 | ALTO | Feature válida pode ser convertida indevidamente em decisão ou liberação de processo. | Manufacturing model exige intent explícito, stock válido, setup/recurso autorizado e revisão; geometry classes nunca geram operação. Drilling requer target confirmado além de cilindro. | MITIGADO PARCIALMENTE v2.2 PACKAGE 2 / MONITORAR |
| R-042 | CRÍTICO | A fronteira Organization/Team pode permitir escalada de papel ou acesso cruzado entre organizações/equipes. | Package 1 usa identidade apenas do token/banco, memberships allowlisted, menor privilégio, owner transacional, índices únicos, cross-organization/team 404, schemas anti-mass-assignment, revogação e auditoria. O gate da release cobre falsificação de papel/header, mass assignment e isolamento. | MITIGADO PARCIALMENTE v1.9 RELEASED / MONITORAR |
| R-043 | ALTO | Evidence parcial/stale, checklist incompleto, checksum divergente ou rollback falho pode ser interpretado como falsa prontidão de piloto. | Estados fechados nunca promovem PARTIAL/FAILED/NOT_AVAILABLE; privacy e contexto são gates; verificação canônica retorna MATCH/MISMATCH; rollback falho bloqueia; toda saída exige revisão humana e não produção. | MITIGADO PARCIALMENTE v1.9 RELEASED / MONITORAR |
| R-044 | ALTO | A integração CAD→feature→engineering→planning→CNC neutro→report pode transformar evidência parcial de um domínio em conclusão indevida de outro. | Contratos v2.2 preservam evidence hash/provenance, `ASK_ONLY_WHEN_BLOCKING`, estados fechados, precedência e replay; planning verification declara não ser simulação física. | MITIGADO PARCIALMENTE v2.2 PACKAGE 2 / MONITORAR |
| R-045 | CRÍTICO | Um workflow integrado e dashboard podem ser interpretados como sistema aprovado para produção ou máquina. | Dashboard mantém `NON_PRODUCTION`, revisão humana, `simulation_only=true`, `executable_output=false`, separa estágios/IA e não oferece toolpath/G/M-code/NC/DNC/transmissão/controle. Evidência de uso real continua necessária. | MITIGADO PARCIALMENTE v2.0 PACKAGE 3 / MONITORAR |
| R-046 | ALTO | Assistente/agente pode sobrescrever regra determinística, preencher lacuna ou elevar sugestão a decisão. | Perfis allowlisted recebem contexto minimizado, retornam texto separado do snapshot imutável, não possuem tools e bloqueiam output CNC/claims de autoridade; provider failure preserva o workflow. | MITIGADO PARCIALMENTE v2.0 PACKAGE 2 / MONITORAR |
| R-047 | ALTO | Síntese Research integrada pode extrapolar fontes, DOE preliminar ou ANOVA descritiva como validação científica. | Bridge versionado exige documento/página/chunk/método, bloqueia ausência, marca chunks como dados não confiáveis e preserva DOE preliminar/ANOVA descritiva sem F-test, p-value, causalidade ou comprovação. | MITIGADO PARCIALMENTE v2.0 PACKAGE 2 / MONITORAR |
| R-048 | CRÍTICO | Catálogos e dados Engineering globais podem vazar ou ser alterados entre organizações quando a plataforma ampliar automação. | Packages 1–2 adicionam ownership por Organization, legado bloqueado, referências read-only, migration reversível, authorization/evidence fail-closed, lifecycle técnico e testes cross-org/revogação. Não existe bulk export nem reconciliation mutável. | MITIGADO PARCIALMENTE v2.1 PACKAGE 2 / MONITORAR |
| R-049 | CRÍTICO | Evidência de simulação pode ser interpretada como validação física, de máquina ou liberação produtiva. | v2.3 P3 adiciona reconstrução Level-2 independente e bounded, falha fechada de stock/coverage/gouge/rapid/fixture, replay e harness cego G0–G9. O request público não aceita review authority; G9 fica pending até evidence autoritativa server-side. Readiness/physical authority permanecem false. B-Rep exato, holder collision e kinematics continuam ausentes. | MITIGADO PARCIALMENTE v2.3 PACKAGE 3 / MONITORAR |
| R-050 | CRÍTICO | Orchestration, tools ou agentes futuros podem escalar sugestão para mutação, decisão ou execução sem autoridade. | TASK-V23-003A bloqueia review/G9 no body. v3.0 usa manifestos imutáveis, replay, tenancy server-side e inteligência read-only sem tools ou mutation; forged/stale/broken evidence falha fechado. Escrita/execução futura ainda exige decisão formal. | MITIGADO PARCIALMENTE v3.0 / MONITORAR |
| R-051 | CRÍTICO | Download de G-code candidato pode ser confundido, adulterado ou reutilizado como programa aprovado para máquina. | TASK-V31-002 usa prova HMAC curta vinculada a user/org/output/blind/thread, membership atual, revalidação de hash/manifest/RS274/replay, G9 pendente e headers/UI non-production. Não há conexão de máquina; validação física e revisão humana permanecem obrigatórias. | MITIGADO PARCIALMENTE v3.1 / MONITORAR |
| R-052 | CRÍTICO | Integridade automática ou simulação bounded pode ser confundida com evidência suficiente para G9 ou teste físico. | TASK-V31-003 separa evidence automática, adjudicação humana autoritativa, simulação externa independente e pré-condições físicas. TASK-V31-004 consolida pacote determinístico hash/version-bound, output-only, sem reviewer/decision input ou endpoint de transição. Todos os invariantes físicos permanecem falsos. | MITIGADO PARCIALMENTE v3.1 / MONITORAR |
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
| v2.0 Integrated Engineering Platform | R-044 a R-047 | versão publicada; riscos permanecem residuais/monitorados e deploy continua separado |
| v2.1 Enterprise Engineering Governance — RC | R-042, R-048 | ownership, migration/backfill, autorização e governance evidence organization-scoped aprovados; riscos permanecem residuais/monitorados |
| v2.2 Advanced Engineering Planning & Verification | R-019, R-039 a R-045, R-049 | corpus/planning/simulation evidence aprovados sem execução ou falsa validação física |
| v3.0 Manufacturing Intelligence & Digital Thread | R-044, R-046, R-047, R-050 | provenance integral e inteligência bounded sem autoridade produtiva/científica autônoma |
| v3.1 Controlled Test Environment | R-049, R-050, R-051 | download autenticado/revalidado, G9 pendente, zero autoridade ou conexão física |

## Segurança de segredos

- `.env` está ignorado pelo Git e não aparece no histórico.
- Nenhum padrão conhecido de chave OpenAI, token GitHub, chave AWS ou chave privada
  foi encontrado nos arquivos rastreados nem no histórico Git local.
- `.env.example` contém somente placeholders; `OPENAI_API_KEY` e
  `AUTH_SECRET_KEY` estão vazios.
- Nenhum arquivo de credencial, cookie, chave privada ou dado pessoal foi localizado.
- A verificação por padrões não substitui secret scanning dedicado no CI.

## Classificação CNC

CAD, features, planning, toolpath e G-code sintéticos existem somente como candidatos
e evidence `NON_PRODUCTION`. Não existe NC/DNC, transmissão, cycle start ou controle
de máquina. Toda evolução permanece `REQUIRES_HUMAN_REVIEW`; Level-2 bounded não
equivale a B-Rep exato, cinemática, validação física nem produção.
