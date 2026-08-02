# Vena_IA Platform

# Documento 03 — Roadmap Executivo Vena_IA até v2.0

**Status:** Documento Oficial de Planejamento  
**Data:** 2026-07-10  
**Última atualização:** 2026-08-01
**Projeto:** Vena_IA — Engenharia Inteligente para Manufatura CNC  
**Documento relacionado:** `PROJECT.md`  
**ADR relacionado:** `ADR-001 — Adoção de Arquitetura Modular Monolith`

---

# 1. Objetivo

Definir o roadmap executivo da Vena_IA Platform, organizando versões, prioridades, entregas, marcos técnicos e critérios de avanço do projeto.

Este documento orienta a execução progressiva do projeto como plataforma de software, base científica e produto comercial escalável.

---

# 2. Estratégia de Evolução

A evolução da Vena_IA será incremental, partindo de uma fundação técnica simples, testável e bem documentada até módulos avançados de engenharia, IA, CAD/CAM/CNC, simulação, pesquisa científica e gestão industrial.

Princípios de execução:

1. Documentar antes de implementar decisões relevantes.
2. Entregar fundações pequenas e verificáveis.
3. Evitar complexidade operacional prematura.
4. Priorizar MVP funcional antes de recursos avançados.
5. Manter arquitetura Modular Monolith até haver justificativa técnica para extração de serviços.
6. Registrar alterações significativas em ADRs ou no `DECISIONS.md`.

---

# 3. Versões Executivas

## v0.1 — Foundation

Objetivo: criar a base documental, estrutural e operacional do projeto.

Entregas:

* `PROJECT.md`;
* `ARCHITECTURE.md` ou ADR-001;
* `ROADMAP.md`;
* `DECISIONS.md`;
* estrutura inicial do repositório;
* README inicial;
* `.gitignore`;
* `.env.example`;
* Docker Compose inicial;
* health check da API;
* aplicação web inicial.

Critério de conclusão:

* projeto pode ser clonado, configurado e executado localmente em modo básico.

---

## v0.2 — Core

Objetivo: implementar o núcleo operacional da plataforma.

Entregas:

* usuários;
* projetos;
* dashboard;
* estrutura de arquivos;
* chats;
* mensagens;
* modelos iniciais de banco;
* primeira migration;
* testes de API principais.

Critério de conclusão:

* usuário consegue acessar a plataforma local, criar projeto e visualizar estrutura inicial do sistema.

---

## v0.3 — IA Base

Objetivo: criar o assistente Vena_IA inicial.

Entregas:

* integração com OpenAI API;
* chat técnico inicial;
* histórico de conversas;
* prompts base;
* camada de orquestração de IA;
* logs e tratamento de erros;
* documentação de uso de IA.

Critério de conclusão:

* usuário consegue conversar com o assistente e manter histórico associado ao projeto.

---

## v0.4 — Upload e Base de Conhecimento

Objetivo: permitir upload de arquivos e iniciar ingestão documental.

Entregas:

* upload de PDF, STEP, STL, DXF e IGES;
* armazenamento em MinIO;
* metadados no PostgreSQL;
* validação de tipo e tamanho;
* pipeline inicial de documentos;
* extração de texto de PDFs;
* preparação para embeddings.

Critério de conclusão:

* usuário consegue anexar arquivos a projetos e consultar metadados.

---

## v0.4.1 — Security Gate

Objetivo: eliminar vulnerabilidades críticas antes da ingestão semântica.

Entregas:

* cadastro com senha protegida por hash;
* login e token assinado com expiração;
* sessão frontend em cookie HttpOnly;
* autorização por usuário, papel e propriedade;
* remoção de `X-User-ID` como identidade;
* upload PDF com allowlist, MIME e magic bytes;
* matriz de autorização e testes de segurança.

Critério de conclusão:

* usuários não conseguem assumir outra identidade, promover o próprio papel ou
  acessar projetos e documentos de terceiros.

Gate:

* concluído em 2026-07-30 com squash merge da PR #4 e release `v0.4.1`.

---

## v0.5 — RAG

Objetivo: criar a base de conhecimento semântica.

Entregas:

* [x] modelo persistente de chunks;
* [x] extração de texto de PDFs por página;
* [x] chunking configurável e rastreável;
* [x] estados, contratos e endpoints mínimos de ingestão/consulta;
* [x] geração de embeddings;
* [x] armazenamento em pgvector;
* [x] busca semântica;
* [x] respostas com contexto recuperado;
* [x] documentação da fundação do pipeline RAG.

Estado:

* pipeline RAG completo implementado no branch `feature/v0.5-rag-foundation`;
* respostas usam somente contexto recuperado e mantêm citações estruturadas para
  documento, página e chunk.

Critério de conclusão:

* usuário consegue fazer perguntas sobre documentos carregados no projeto.

---

## v0.6 — CAD Inicial

Objetivo: iniciar interpretação técnica de arquivos CAD.

Entregas:

* [x] serviço `parser-step`;
* [x] leitura inicial de STEP;
* [x] extração de metadados geométricos;
* [x] dimensões básicas;
* [x] volume quando tecnicamente viável;
* [x] relatório técnico preliminar;
* [x] avaliação de OpenCascade ou pythonOCC.

Limite desta entrega:

* volume permanece explicitamente indisponível sem kernel geométrico;
* OpenCascade/pythonOCC foi avaliado e adiado conforme ADR-0011.

Critério de conclusão:

* usuário consegue carregar um STEP e obter uma análise geométrica inicial.

---

## v0.7 — Engenharia e CAM Inicial

Objetivo: criar a primeira camada de planejamento de manufatura.

Estado da primeira entrega:

* fundação de regras determinísticas para fresamento implementada;
* rotação, avanço e tempo de corte respeitam limites informados da máquina;
* resultados são preliminares e exigem revisão humana;
* cadastros persistentes e sugestões de processo completas permanecem pendentes
  dentro da própria v0.7.

Entregas:

* cadastro de materiais;
* cadastro de máquinas;
* cadastro de ferramentas;
* regras iniciais de parâmetros de corte;
* sugestões básicas de processo;
* estimativa inicial de tempo;
* documentação dos cálculos.

Critério de conclusão:

* sistema consegue sugerir parâmetros iniciais com base em material, ferramenta e máquina.

---

## v0.8 — CNC Inicial

Objetivo: preparar geração assistida de processo CNC.

Estado da primeira entrega:

* estrutura neutra de operações e parâmetros implementada;
* perfis Fanuc Oi/Romi D1250 são somente placeholders planejados;
* nenhuma saída executável ou G-code é gerada.

Entregas:

* estrutura para operações CNC;
* estratégia inicial para Fanuc Oi;
* compatibilidade planejada com Romi D1250;
* geração preliminar de blocos G-code;
* validações básicas;
* documentação de limitações.

Critério de conclusão:

* sistema consegue gerar um exemplo controlado de G-code para operação simples.

---

## v0.9 — Pesquisa Científica

Objetivo: estruturar o módulo de pesquisa e suporte acadêmico.

Status: publicada em `v0.9.0`. A entrega reutiliza upload/processamento/RAG
existentes e não duplica armazenamento de PDF, texto, chunks ou embeddings.

Entregas:

* biblioteca de artigos;
* ingestão de PDFs científicos;
* extração de referências;
* análise assistida por IA;
* estrutura para DOE;
* estrutura para ANOVA;
* relatórios técnicos e acadêmicos.

Limites desta versão:

* referências e metadados extraídos por heurística são preliminares;
* sínteses exigem grounding e revisão humana;
* DOE não afirma validade, potência ou tamanho amostral;
* ANOVA prepara e resume dados, sem teste inferencial, estatística F ou valor-p;
* relatórios são rascunhos e não equivalem a publicação, laudo ou revisão sistemática.

Critério de conclusão:

* usuário consegue organizar documentos científicos e gerar sínteses técnicas relacionadas ao projeto.

---

## v1.0 — MVP Vena_IA

Objetivo: entregar a primeira versão funcional da plataforma.

Status: publicado como `v1.0.0` após aprovação nos gates locais, no CI e na
validação pós-merge. Evidências estão em `docs/MVP_AUDIT_MATRIX.md`.

Entregas:

* login;
* dashboard;
* criação de projetos;
* upload de arquivos;
* chat com IA;
* base de conhecimento RAG;
* histórico de interações;
* relatórios técnicos iniciais;
* documentação de instalação;
* testes essenciais;
* pipeline básico de CI.

Critério de conclusão:

* usuário consegue criar conta, criar projeto, enviar arquivos, conversar com IA, consultar conhecimento técnico e gerar relatório inicial.

---

## v1.1 — Stabilization

Objetivo: auditar o MVP publicado e corrigir o menor conjunto de falhas reais de
maior impacto, preservando arquitetura, segurança e contratos públicos.

Status: publicada como `v1.1.0` após três pacotes na PR #11, Squash Merge e
aprovação dos gates locais, do CI, pós-merge e diretamente da tag. Nenhum deploy
foi executado.

Escopo do pacote 1:

* recuperação idempotente de documentos em `FAILED`;
* retry de processamento e indexação visível no frontend;
* validação das evidências de relatórios contra documentos e chunks persistidos;
* testes de regressão, validação integral e atualização da documentação afetada.

Escopo do pacote 2:

* cliente HTTP único e timeout para impedir carregamento indefinido;
* mensagens consistentes e falhas de logout/chat visíveis;
* abertura do fluxo principal preservada quando apenas relatórios falham;
* remoção de controles de navegação sem ação;
* nova auditoria integral de API, frontend, Docker, PostgreSQL, OpenAPI e CI.

Escopo do pacote 3:

* eliminar recargas de quatro endpoints após operações que já retornam o recurso;
* sincronizar somente documentos ou histórico quando uma operação falhar;
* cancelar requests iniciais quando dashboard/projeto forem desmontados;
* remover tipos não consumidos e o warning legado do `TestClient` com HTTPX2;
* preservar contratos públicos, arquitetura, migrations e escopo da v1.1.

Critério de conclusão:

* release `v1.1.0` publicada, tag validada, 165 testes sem warnings e fluxo
  estabilizado sem reduzir segurança nem alterar contratos públicos.

---

## Diagnóstico pós-v1.1

### Capacidades concluídas

* autenticação, autorização e isolamento por proprietário estão em
  `apps/api/app/modules/auth`, cobertos por `test_auth.py` e pelo E2E
  cross-user, conforme ADR-0009;
* projeto, PDF, MinIO, chunks, embeddings, pgvector, RAG, chat persistente e
  relatório formam o MVP integrado em `apps/api`, `packages/ai` e `apps/web`,
  coberto por 165 testes e ADR-0010/ADR-0015;
* CAD textual preliminar, recomendação de fresamento, plano CNC neutro e
  fundação científica existem com limites explícitos em `cad`,
  `manufacturing`, `cnc` e `research`.

### Capacidades parciais

* CAD não possui kernel geométrico, topologia, volume robusto ou reconhecimento
  de features (ADR-0011, R-019);
* CAM não possui catálogos persistentes de materiais, máquinas e ferramentas,
  nem custo completo; as regras atuais são preliminares (ADR-0012, R-020);
* CNC permanece neutro, não executável e sem transmissão (ADR-0013, R-021);
* pesquisa oferece organização e preparação, não revisão sistemática,
  ANOVA inferencial ou publicação (ADR-0014, R-022 a R-029).

### Ausências e dívida real

* rate limiting, revogação imediata de JWT e recuperação auditável de senha
  para contas legadas (R-030, R-013 e R-014);
* backup/restore de PostgreSQL e MinIO (R-031);
* logging estruturado, correlação, auditoria, métricas e tracing (R-010/R-032);
* fila/worker, processamento assíncrono e OCR seguro (R-016/R-017);
* capacidade, escalabilidade, versões de runtime/imagens fixadas e resiliência
  completa de provedores (R-008/R-009/R-018/R-033/R-034);
* `packages/auth`, `packages/database`, `packages/engineering`, `packages/ui` e
  `services/parser-*` continuam reservas documentais, não implementações.

### Dependências de avanço

```text
Segurança e proteção de dados
  → backup/restore
  → observabilidade e auditoria
  → processamento assíncrono
  → confiabilidade e escalabilidade
  → engenharia/CAM
  → CAD e features
  → piloto controlado
  → consolidação v2.0
```

---

## v1.2 — Security and Data Protection

Objetivo: reduzir primeiro os riscos de abuso, sessão e proteção de dados que
bloqueiam exposição externa.

Primeiro pacote autorizado:

* rate limiting configurável, determinístico e testável para cadastro e login;
* chave por cliente sem confiar em identidade fornecida por `X-User-ID`;
* resposta `429` com `Retry-After`, falha controlada e contratos públicos
  existentes preservados fora do limite;
* testes unitários e de integração, configuração e documentação;
* limite local explicitamente classificado como primeira camada; gateway ou
  armazenamento distribuído continua obrigatório antes de produção horizontal.

Estado do Package 1: implementado na branch `codex/v1.2-auth-rate-limiting` e
publicado na Draft PR [#13](https://github.com/VenancioMarcos/vena-ia-platform/pull/13),
com Ruff, mypy, 172 testes e Backend CI aprovados. Nenhuma entrega posterior da
v1.2 foi iniciada.

Estado do Package 2: auditoria de autenticação/sessão aprovada pelo CTO e em
execução na mesma Draft PR #13. A invalidação local no logout e a rejeição de
tokens emitidos no futuro não encerram o gate de revogação distribuída R-013.
Ruff, mypy, 177 testes, frontend, Docker, PostgreSQL, OpenAPI e CI final de
backend/frontend estão aprovados; o pacote aguarda revisão do CTO.

Estado do Package 3: fluxo administrativo para credencial legada, invalidação
por versão de autenticação e auditoria persistente de eventos sensíveis foram
implementados na mesma Draft PR #13. Ruff, mypy, 182 testes, migration
PostgreSQL reversível, OpenAPI e CI final de backend/frontend estão aprovados;
o pacote aguarda revisão do CTO.

Estado do Package 4: rate limiting e revogação usam o Redis já adotado, com
estado compartilhado entre réplicas, incremento/expiração atômicos, TTL até a
expiração do JWT e chaves sem origem, token ou PII em texto puro. Indisponibilidade
falha fechada e auditável; memória é modo explícito de desenvolvimento/teste.
Integrado pela PR #13, aprovado pelo CTO e validado na `main` para a Release
`v1.2.0`.

Entregas posteriores da v1.2:

* política operacional automatizada de retenção/proteção da auditoria;
* validação de fronteira de proxy/gateway para exposição externa.

Fora do escopo: SSO, provedor de identidade externo, deploy e mudança de
arquitetura.

Riscos/dependências: R-030, R-013, R-014; autenticação da ADR-0009.

Testes obrigatórios: janelas/limites, isolamento de clientes, `Retry-After`,
cadastro/login normal, autenticação, E2E e regressão cross-user.

Critérios de segurança e aceite: abuso é limitado sem aceitar identidade do
cliente; sessões podem ser encerradas antes da expiração; contas legadas recebem
credencial somente por fluxo administrativo auditável; nenhum segredo é logado.

Condição de avanço: R-030/R-013/R-014 mitigados ou com gate externo testado e
documentado; CI e matriz de autorização aprovados.

---

## v1.3 — Backup and Recovery

Objetivo: tornar PostgreSQL e MinIO recuperáveis antes de qualquer piloto com
dados reais.

Entregas: scripts versionados de backup/restore, manifesto e checksums, política
de retenção e criptografia, restore em ambiente descartável, runbook e teste de
consistência entre metadados e objetos.

Fora do escopo: compra de storage, backup de produção ou envio de dados a nuvem.

Dependências/riscos: v1.2 concluída; R-031 e R-011.

Testes obrigatórios: backup → perda simulada → restore, checksums, migrations,
arquivos MinIO e isolamento de dados.

Critérios de segurança e aceite: nenhum segredo/backup entra no Git; restauração
reproduzível em ambiente descartável com RPO/RTO documentados.

Condição de avanço: R-031 deixa de bloquear piloto controlado.

Estado do Package 1: contrato versionado, manifesto SHA-256, scripts seguros de
backup/restore PostgreSQL e round trip em banco descartável implementados na
branch `codex/v1.3-backup-recovery`.

Estado do Package 2: a mesma branch e Draft PR #14 incluem contrato versionado
MinIO, checksums de conteúdo, restauração em bucket/prefixo vazio explicitamente
permitido, manifesto compartilhado de backup-set e teste real combinado. A
consistência cruzada falha sem reparo automático diante de objeto ausente, órfão
ou divergência de projeto/documento. Automação de retenção, agendamento, storage
externo e gestão de chaves permanecem para decisão/pacote posterior.

---

## v1.4 — Observability and Auditability

Objetivo: tornar falhas e operações sensíveis rastreáveis sem expor dados.

Entregas: logging estruturado, correlation/request ID, trilha de auditoria para
autenticação e mutações sensíveis, readiness de dependências, métricas e
tracing por contratos substituíveis, runbooks e alertas definidos.

Fora do escopo: contratar SaaS, monitorar usuários ou publicar telemetria externa.

Dependências/riscos: v1.3; R-010, R-032 e R-033.

Testes obrigatórios: correlação, redaction, falhas de dependência, auditoria,
health/readiness e regressão de desempenho.

Critérios de segurança e aceite: nenhum token, senha, documento ou prompt é
registrado; eventos críticos são correlacionáveis e acionáveis.

Condição de avanço: operação local/piloto diagnosticável por evidência.

---

## v1.5 — Asynchronous Processing

Objetivo: retirar ingestão, OCR futuro e indexação longa da requisição HTTP.

Entregas: contrato de job, fila/worker reutilizando Redis, estados e progresso,
idempotência, retry/backoff, timeout, cancelamento, recuperação após reinício e
avaliação segura de OCR para PDF sem texto.

Fora do escopo: serviço distribuído independente sem ADR, GPU paga ou OCR sem
validação de qualidade/segurança.

Dependências/riscos: v1.4; R-016, R-017 e R-033. Worker separado exige ADR se
alterar a fronteira do Modular Monolith.

Testes obrigatórios: idempotência, retries, reinício, concorrência, autorização,
falhas de MinIO/PostgreSQL/IA e documentos extensos.

Critérios de segurança e aceite: jobs preservam proprietário/projeto, não
executam conteúdo e nunca criam resposta falsa.

Condição de avanço: processamento longo resiliente e observável fora do ciclo HTTP.

---

## v1.6 — Reliability and Scalability

Objetivo: medir e fortalecer a plataforma antes de ampliar funções de engenharia.

Entregas: imagens/runtime fixados, matriz Python suportada, budgets de timeout e
retry, resiliência do provedor, limites de concorrência, testes de carga/capacidade,
estado compartilhado seguro e runbook de degradação.

Fora do escopo: deploy, autoscaling externo ou compra de infraestrutura.

Dependências/riscos: v1.5; R-008, R-009, R-018, R-033 e R-034.

Testes obrigatórios: carga controlada, soak curto, falha/retorno de dependências,
compatibilidade Python, imagens reproduzíveis e regressão E2E.

Critérios de segurança e aceite: limites medidos, falha segura, sem resposta
fabricada e sem dependência de estado apenas em processo.

Condição de avanço: capacidade e gargalos documentados para um piloto definido.

---

## v1.7 — Engineering Catalogs and CAM

Objetivo: concluir a base CAM prevista com dados de engenharia rastreáveis.

Entregas: catálogos persistentes de materiais, máquinas e ferramentas; versão e
fonte dos dados; regras por operação; seleção preliminar; tempo/custo; relatório
de hipóteses e revisão humana.

Fora do escopo: toolpath, G-code executável ou envio a máquina.

Dependências/riscos: v1.6; ADR-0012, R-020 e `packages/engineering` reservado.

Testes obrigatórios: unidades, limites de máquina, origem/versão de dados,
autorização, cálculos determinísticos e casos de borda.

Critérios de segurança e aceite: toda recomendação é preliminar, rastreável e
`REQUIRES_HUMAN_REVIEW`.

Condição de avanço: processo preliminar reproduzível sem alegar liberação CNC.

---

## v1.8 — CAD Interoperability and Feature Recognition

Objetivo: evoluir do parser textual para geometria validada e formatos previstos.

Entregas: ADR de kernel/licença/portabilidade; STEP topológico com unidade,
bounding box, área/volume e validade; features iniciais rastreáveis; fundações
seguras para STL/DXF/IGES; relatório de tolerância e incerteza.

Fora do escopo: executar macros/referências externas, afirmar manufaturabilidade
automática ou substituir validação metrológica.

Dependências/riscos: v1.7; ADR-0011, R-019 e `services/parser-*` reservados.

Testes obrigatórios: corpus conhecido e malformado, unidades, topologia,
propriedades contra referências verificadas, fuzzing limitado e isolamento.

Critérios de segurança e aceite: parser não executa conteúdo; resultados incluem
origem, tolerância, limitação e nível de confiança.

Condição de avanço: features alimentam planejamento sem remover revisão humana.

---

## v1.9 — Controlled Pilot Readiness

Objetivo: integrar os gates técnicos em um piloto controlado e reversível.

Entregas: empresas/equipes e papéis mínimos, onboarding, runbooks, restore drill,
SLOs, capacidade, checklist de privacidade, suporte/incidente e validação virtual
de planos CNC neutros. Qualquer G-code futuro permanece em missão separada,
`SIMULATION_ONLY` e sob aprovação humana explícita.

Fora do escopo: deploy sem autorização, publicação comercial, produção real ou
transmissão CNC.

Dependências/riscos: v1.2 a v1.8; R-021, riscos científicos R-022 a R-029 e
gates de produção ainda abertos.

Testes obrigatórios: jornada piloto, isolamento organizacional, restore,
incidente, carga-alvo, acessibilidade e validação virtual sem máquina.

Critérios de segurança e aceite: piloto usa dados autorizados, rollback/runbooks
testados e zero saída liberada para máquina.

Condição de avanço: aceite humano do piloto e riscos de produção tratados.

---

## v2.0 — Integrated Engineering Platform

Objetivo: consolidar a plataforma integrada de engenharia, conhecimento e
pesquisa com base operacional pronta para decisão de produção.

Entregas: fluxo CAD → features → CAM preliminar → plano CNC neutro → relatório;
agentes especializados usando contratos existentes; pesquisa fundamentada;
dashboard operacional; segurança, backup, observabilidade, processamento
assíncrono e capacidade comprovados; documentação técnica/científica/comercial.

Fora do escopo automático: deploy, compra, compromisso comercial, decisão
científica autônoma, G-code aprovado para produção ou transmissão CNC.

Dependências/riscos: conclusão e aceite das v1.2–v1.9; riscos residuais com dono,
prazo e controle aprovados.

Testes obrigatórios: regressão integral, E2E de engenharia, isolamento, segurança,
restore, observabilidade, resiliência, carga, validação científica e simulação
controlada.

Critérios de segurança e aceite: gates de piloto/produção verificáveis, revisão
humana preservada e nenhuma ação irreversível automática.

Condição de conclusão: release v2.0 validada e decisão de deploy tratada como
missão externa separada com autorização do proprietário.

---

# 4. Fases Operacionais

## Fase 0 — Fundação Documental

Status: concluída parcialmente.

Entregas:

* `PROJECT.md`: concluído;
* ADR-001: concluído;
* `ROADMAP.md`: este documento;
* `DECISIONS.md`: previsto na mesma etapa.

---

## Fase 1 — Governança Técnica

Status: em execução.

Entregas:

* arquitetura técnica inicial;
* roadmap executivo;
* registro de decisões;
* critérios de execução;
* preparação para repositório.

---

## Fase 2 — Repositório GitHub

Status: próxima fase.

Entregas:

* criação do repositório;
* branch principal;
* estrutura de diretórios;
* README;
* licença;
* `.gitignore`;
* templates de issues;
* milestones iniciais.

---

## Fase 3 — Infraestrutura Base

Entregas:

* Docker Compose;
* PostgreSQL;
* pgvector;
* Redis;
* MinIO;
* API;
* Web.

---

## Fase 4 — Backend Base

Entregas:

* FastAPI;
* SQLAlchemy;
* Alembic;
* Pydantic;
* `/health`;
* rotas iniciais de usuários, projetos, arquivos e chat.

---

## Fase 5 — Frontend Base

Entregas:

* Next.js;
* React;
* TypeScript;
* Tailwind CSS;
* shadcn/ui;
* layout principal;
* dashboard;
* navegação.

---

## Fase 6 — Autenticação

Entregas:

* usuários;
* login;
* JWT;
* permissões;
* papéis iniciais.

---

## Fase 7 — Projetos

Entregas:

* conceito de Projeto Engenharia;
* arquivos por projeto;
* conversas por projeto;
* análises;
* relatórios.

---

## Fase 8 — Upload

Entregas:

* suporte a PDF, STEP, STL, DXF e IGES;
* MinIO;
* metadados;
* validações;
* histórico.

---

## Fase 9 — Chat IA

Entregas:

* assistente Vena_IA;
* integração OpenAI;
* histórico;
* contexto de projeto.

---

## Fase 10 — RAG

Entregas:

* extração;
* fragmentação;
* embeddings;
* pgvector;
* busca;
* resposta contextual.

---

## Fase 11 — Agentes Especializados

Entregas:

* Engineering Agent;
* CAD Agent;
* CAM Agent;
* CNC Agent;
* Research Agent;
* Simulation Agent;
* Lean Agent.

---

## Fase 12 — CAD

Entregas:

* parser STEP;
* metadados geométricos;
* dimensões;
* volume;
* identificação inicial de features.

---

## Fase 13 — CAM

Entregas:

* planejador de usinagem;
* seleção de ferramentas;
* estratégia;
* parâmetros.

---

## Fase 14 — CNC

Entregas:

* geração de G-code;
* perfil Fanuc Oi;
* compatibilidade Romi D1250;
* validações.

---

## Fase 15 — Simulação

Entregas:

* arquitetura para FEA;
* análise estrutural futura;
* validação técnica.

---

## Fase 16 — Pesquisa Científica

Entregas:

* biblioteca científica;
* análise de artigos;
* DOE;
* ANOVA;
* relatórios;
* vínculo metodológico com pesquisa de mestrado.

---

## Fase 17 — Enterprise

Entregas:

* Lean;
* OEE;
* VSM;
* SMED;
* PCP;
* ERP;
* custos.

---

## Fase 18 — Segurança

Entregas:

* controle de acesso;
* logs;
* backups;
* auditoria;
* revisão de permissões.

---

## Fase 19 — Qualidade

Entregas:

* GitHub Actions;
* testes;
* build;
* análise estática;
* validação de documentação.

---

## Fase 20 — Documentação Comercial

Entregas:

* documento de produto;
* documento técnico;
* documento científico;
* materiais para apresentação.

---

## Fase 21 — MVP Vena_IA v1.0

Entregas:

* versão integrada;
* fluxo principal funcional;
* documentação de instalação;
* documentação de uso;
* validação final.

---

## Fase 22 — Evolução Comercial

Entregas:

* planos comerciais;
* multiusuário;
* empresas;
* dashboards;
* integrações industriais.

---

# 5. Marcos Principais

## Marco A — Base Documental

Condição:

* `PROJECT.md`, ADR-001, `ROADMAP.md` e `DECISIONS.md` concluídos.

## Marco B — Repositório Operacional

Condição:

* repositório criado com estrutura inicial e documentação versionada.

## Marco C — Ambiente Local Executável

Condição:

* API, Web, PostgreSQL, Redis e MinIO sobem localmente.

## Marco D — Core Funcional

Condição:

* usuários, projetos, arquivos e chat possuem fluxo básico.

## Marco E — IA com Contexto

Condição:

* chat responde usando documentos do projeto via RAG.

## Marco F — Engenharia Inicial

Condição:

* sistema interpreta arquivo CAD e gera análise técnica inicial.

## Marco G — MVP v1.0

Condição:

* fluxo principal completo validado.

---

# 6. Prioridades Imediatas

Ordem recomendada de execução:

1. Finalizar documentação de governança.
2. Criar plano de repositório.
3. Criar repositório GitHub.
4. Criar estrutura de pastas.
5. Configurar Docker Compose.
6. Criar backend mínimo.
7. Criar frontend mínimo.
8. Criar banco e migrations.
9. Criar autenticação.
10. Criar projetos.
11. Criar upload.
12. Criar chat IA.
13. Criar RAG.
14. Criar agentes.
15. Evoluir CAD, CAM e CNC.

---

# 7. Riscos e Controles

## Risco: escopo amplo demais para o MVP

Controle:

* manter foco em login, projetos, upload, chat, RAG e relatório inicial.

## Risco: arquitetura virar monolito acoplado

Controle:

* aplicar Modular Monolith com limites de domínio e revisões arquiteturais.

## Risco: CAD/CAM/CNC exigir complexidade científica alta

Controle:

* evoluir em protótipos progressivos e registrar limitações.

## Risco: dependência externa de IA

Controle:

* criar camada de abstração em `packages/ai` e registrar provedores.

## Risco: dados e arquivos sensíveis

Controle:

* segurança desde a base, validação de upload e não versionamento de segredos.

---

# 8. Registro de Entrega

## Objetivo

Criar o roadmap executivo oficial da Vena_IA Platform.

## Escopo

Inclui versões, fases operacionais, marcos, prioridades, riscos e critérios de conclusão.

## Arquivos Criados

* `outputs/ROADMAP.md`

## Arquivos Modificados

* Nenhum.

## Testes Realizados

* Validação de consistência com `PROJECT.md`.
* Validação de consistência com ADR-001.

## Critérios de Aceitação

* Roadmap em Markdown.
* Versões definidas.
* Fases organizadas.
* Marcos objetivos documentados.
* Próximas prioridades estabelecidas.

## Próximos Passos

Criar e manter o `DECISIONS.md` como registro vivo de decisões técnicas e estratégicas.

---

# 9. Registro de Entrega — Consolidação pós-v1.1

## Objetivo

Definir a progressão necessária de v1.2 até v2.0 a partir do estado real,
backlog, decisões, riscos e limites oficiais.

## Escopo

Diagnóstico de capacidades, gates por versão, dependências, riscos, itens fora
do escopo, testes, critérios de segurança/aceite e condição de avanço.

## Arquivos Modificados

Roadmaps, contexto, changelog, decisões, riscos e controles CTO oficiais.

## Testes Realizados

Consistência com `PROJECT.md`, arquitetura/ADRs, código/testes existentes,
registro de riscos e limites operacionais.

## Critérios de Aceitação

Versões não artificiais, riscos tratados antes da ampliação funcional, escopo
v1.2 Package 1 explícito e nenhuma autorização implícita de deploy ou CNC real.

## Próximos Passos

Revisar a Draft PR do primeiro pacote v1.2; não iniciar entregas posteriores ou
v1.3 sem nova ordem oficial.

---

**Fim do Documento 03 — Roadmap Executivo Vena_IA até v2.0**
