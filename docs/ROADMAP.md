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

Estado do Package 3: retenção executável e atômica por set completo, job agendável
com lock/timeout, bundle autenticado AES-256-GCM e recovery drill mensurável são
implementados na mesma Draft PR #14. Chaves permanecem externas e rotacionadas por
identificador; KMS/nuvem/agendamento real e qualquer SLO de produção ficam fora.

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

Estado do Package 1: logging estruturado versionado, request/correlation ID,
redaction allowlisted, exceção interna correlacionada, health versionado e
readiness preliminar de PostgreSQL/Redis/MinIO são implementados na branch
`codex/v1.4-observability-auditability`. Métricas, tracing, alertas e backend
externo permanecem para pacotes posteriores.

Estado do Package 2: métricas agregadas com contrato e cardinalidade fechados,
endpoint admin opt-in, request/correlation ID persistidos na auditoria, contratos
de alertas com provider no-op/local e tracing interno sem exportação são
implementados na mesma Draft PR #15. Backend externo, SaaS, webhook, entrega de
alertas e telemetria fora do processo permanecem fora; o Package 3 deve concluir
os gates restantes de operação/auditoria antes da integração da v1.4.

Itens restantes para definição/autorização do Package 3: critérios operacionais
e drill de incidente ponta a ponta; decisão sobre retenção/backend de métricas;
limiares calibrados com evidência; entrega real de alertas somente se aprovada;
e fechamento formal dos riscos R-010/R-032/R-033. Nenhum desses itens está
implícito ou implementado pelo contrato local do Package 2.

Estado do Package 3: drill reproduzível para onze cenários controlados, contrato
`vena-ia.incident-drill/v1`, bundle determinístico com SHA-256 e limiares
configuráveis/validados foram implementados na mesma Draft PR #15. A auditoria
sensível mantém retenção persistente de 90 dias; métricas e tracing permanecem
efêmeros por processo. Não há backend histórico, SaaS, exportador ou transporte
externo de alertas. R-010 foi mitigado; R-032 e R-033 permanecem monitorados como
riscos residuais e não bloqueiam a revisão técnica do pacote.

---

## v1.5 — Asynchronous Processing

**Estado:** concluída e publicada como v1.5.0 em 2026-08-05 pela PR #16. R-016 está
parcialmente mitigado, R-017 permanece aberto com OCR adiado, R-033 é residual e
R-038 permanece monitorado. A v1.6 não foi iniciada.

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

Estado do Package 1: `vena-ia.job/v1`, persistência PostgreSQL, fila Redis com
lease/heartbeat, worker do Modular Monolith, idempotência, retry/backoff, timeout,
cancelamento, recuperação e interface mínima foram implementados na branch
`codex/v1.5-asynchronous-processing`. O primeiro handler executa extração, chunking
e indexação já existente do PDF; endpoints síncronos permanecem compatíveis. OCR,
novos tipos de busca, microserviço e deploy continuam fora. PDF sem texto mantém
  falha explícita.

  Estado do Package 2: recovery automático recompõe o Redis pela fonte durável,
  renova leases, resolve concorrência/duplicatas e preserva efeitos idempotentes.
  Drills cobrem reinícios, dependências, cancelamento, timeout e PDFs sintéticos de
  500 páginas. OCR foi formalmente classificado como adiado (B), sem implementação;
  R-017 segue aberto e timeout preemptivo/capacidade permanecem gates futuros.
  A decisão final encerra a v1.5 sem Package 3 e sem implementar OCR.

---

## v1.6 — Reliability and Scalability

**Estado:** concluída em 2026-08-06 pela PR #17; a publicação da tag e Release
v1.6.0 encerra os três packages sem autorizar piloto ou deploy.

**Estado do Package 1:** Runtime and Container Reproducibility implementa matriz
oficial, manifesto/policy check, Python 3.13.11 oficial com 3.14.6 experimental,
Node 22.20.0, pnpm 11.9.0, imagens/digests e CI de builds. Budgets, carga,
capacidade, escalabilidade horizontal e packages posteriores não foram iniciados.

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

O Package 1 não satisfaz essa condição de avanço: ele reduz deriva de runtime e
imagens, mas não mede capacidade nem altera R-034.

**Estado do Package 2:** budgets e degradação implementam o contrato
`vena-ia.resilience-policy/v1`, classificação de falhas, retries limitados,
backoff/jitter, deadline global, backpressure de IA por processo, budgets de
PostgreSQL/Redis/MinIO/worker, observabilidade bounded e drill sintético. Não mede
carga/capacidade, não resolve timeout preemptivo e não satisfaz a condição de avanço.

**Estado do Package 3 R1:** o baseline em processo foi reclassificado como
`HARNESS_ONLY_BASELINE`. O gate corrigido inicia API A/API B e Worker A/Worker B,
PostgreSQL/pgvector, Redis e MinIO descartáveis; usa HTTP real, providers Redis,
claims/leases, recuperação de worker/MinIO, backpressure e soak integrado de 30 s.
O resultado continua sendo guardrail de CI, não capacidade produtiva. A conclusão
da v1.6 depende da revisão do CTO e não autoriza piloto/deploy.

---

## v1.7 — Engineering Catalogs and CAM

**Estado do Package 1:** fundação implementada na branch
`codex/v1.7-intelligent-engineering`: contratos versionados, catálogo persistente
de materiais, máquinas e ferramentas, fonte/versão rastreáveis, repository,
service, APIs autenticadas e seleção preliminar. Não há toolpath, G-code ou
integração com máquina; revisão humana permanece obrigatória.

**Estado do Package 2:** regras determinísticas para milling, drilling e turning,
compatibilidade preliminar, parâmetros, tempo/custo opcionais e contrato versionado
foram adicionados à mesma Draft PR #18. Ausência de dados é explícita; nenhuma
saída executável ou liberação de processo foi introduzida.

**Estado do Package 3:** relatório técnico reproduzível, checklist humano,
incerteza informacional e consolidação de itens indisponíveis concluem a fundação
v1.7 na mesma Draft PR #18, sem persistência automática ou saída CNC.

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

**Estado do Package 1:** ADR-0015 seleciona OpenCascade com restrições e o contrato
`vena-ia.geometry-analysis/v1` é validado sem instalar o kernel. Área, volume,
topologia e tolerância permanecem `NOT_AVAILABLE` até gates controlados.

**Estado do Package 2:** `GO_CONTROLLED_INTEGRATION` comprovado com
cadquery-ocp 7.9.3.1.1/OCCT 7.9.3 em adapter lazy. Box analítico valida envelope,
área, volume e topologia; tolerância de fabricação e feature recognition continuam fora.

**Estado do Package 3:** contrato `vena-ia.geometry-features/v1` e rule `1.0.0`
reconhecem faces planares/cilíndricas e furo passante estrito sobre corpus sintético.
Furo cego e slot foram adiados por evidência insuficiente; revisão humana permanece
obrigatória e nenhuma integração de produção com engineering/CAM foi ativada.

**Estado do Package 4:** `vena-ia.feature-planning/v1` rule `1.0.0` comprova a
ponte rastreável de through hole a `DRILLING_CANDIDATE` não executável. Catálogos
explícitos reutilizam Engineering v1.7; missing inputs falham fechados. O gate
“features alimentam planejamento sem remover revisão humana” está `SATISFIED` por evidência,
sem antecipar encerramento da v1.8, CAM ou liberação CNC.

**Release v1.8.0:** Packages 1–4 foram integrados pela PR #19 e publicados por tag
anotada/GitHub Release após autorização direta do proprietário. Validação final
preservou revisão humana e ausência de saída CNC executável; nenhum deploy foi realizado.

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

### Decomposição oficial — TASK-V19-001

Estado do Package 1: `COMPLETE / RELEASED v1.9.0`. O CTO aprovou a baseline de
dois Packages e a implementação foi integrada pela PR #21.

#### Package 1 — Controlled Pilot Governance and Organizational Foundation

Objetivo: criar a fronteira mínima de organização/equipe, papéis e contexto de
piloto necessária para que qualquer ensaio posterior possua dono, escopo,
isolamento e aceite rastreáveis.

Escopo: organization e team mínimos no Modular Monolith; membership/papéis
allowlisted; ownership organizacional sem substituir a identidade JWT; onboarding
controlado; contexto de piloto com estado e responsável; checklist de readiness e
privacidade; autorização e isolamento cross-organization/cross-team.

Dependências: v1.2 autenticação/Redis; matriz de autorização; v1.3 recovery; v1.4
auditoria/observabilidade; v1.6 runtime/resiliência/capacidade; v1.7–v1.8 contratos
Engineering/CAD; `SECURITY.md` e limites operacionais permanentes.

Entregáveis: decisão/ADR de tenancy mínima; modelos/repositories/services/API
autenticada; contratos versionados de organization, membership, pilot context e
readiness checklist; migration única quando comprovadamente necessária; onboarding
sem convite externo automático; matriz de autorização atualizada; evidência sintética.

Contratos implementados: `vena-ia.organization/v1`, `vena-ia.team/v1`,
`vena-ia.membership/v1`, `vena-ia.pilot-context/v1` e
`vena-ia.pilot-readiness-checklist/v1`. Mudança semântica futura exige nova versão.

Dados: somente IDs técnicos, nomes operacionais mínimos, papel allowlisted, estado,
responsável, timestamps e evidência/checklist categorizada. Não coletar dados de
cliente real, documento pessoal, credencial, conteúdo CAD/PDF/IA ou dado sensível
desnecessário. Retenção/exclusão de contexto de piloto deve ser decidida antes de uso real.

Riscos: R-001–R-004/R-013/R-014/R-030 de identidade e autorização, R-028 de
isolamento, R-031/R-034 residuais e R-042 de isolamento organizacional. Nenhum risco
é considerado resolvido por criar o contrato.

Testes implementados: contrato/migration; auth; matriz completa de papéis; membership;
owner/admin/member; cross-organization e cross-team 404; mass assignment; papel
forjado por body/header; `X-User-ID`; onboarding/revogação; estados/checklist;
privacidade e logs; concorrência/idempotência; regressão dos recursos próprios existentes.

Critérios de aceite: nenhuma identidade fora do token/banco; isolamento fail-closed;
papéis de menor privilégio; onboarding reversível e auditável; checklist não pode
declarar piloto aprovado; dados allowlisted; zero deploy, piloto real ou saída CNC.

Condição de avanço: modelo organizacional e contexto sintético aprovados no CI,
matriz/risco/documentação revisados e autorização específica do CTO para Package 2.

Fora do escopo: empresa/cliente real, convite por e-mail, billing, SSO/SCIM, domínio,
integração externa, deploy, SLO produtivo, piloto real, dado pessoal, CAM executável,
toolpath, G-code ou máquina CNC.

#### Package 2 — Controlled Operational Rehearsal and Virtual Pilot Evidence

Estado: `COMPLETE / RELEASED v1.9.0` pela PR #21. O CTO aprovou o Package 2 e o
proprietário aprovou o Owner Release Gate. Não existe Package 3.

Objetivo: compor, somente sobre o contexto sintético autorizado do Package 1, a
jornada piloto reversível e as evidências operacionais já existentes.

Escopo: onboarding walkthrough; runbooks integrados; restore/incident drills;
objetivos SLO propostos com janela/fonte/dono (não compromisso produtivo); aceite do
perfil de capacidade descartável; checklist de privacidade; suporte/escalonamento;
jornada E2E e validação virtual de plano CNC neutro sem execução.

Dependências: Package 1 aprovado; contratos de backup/restore, observabilidade,
incidente, runtime, resiliência e capacidade; planos CNC neutros v0.8; riscos
R-021–R-041 e autorização específica para qualquer ambiente externo.

Entregáveis: contrato versionado de evidence bundle do piloto; matriz runbook/gate;
restore e incident evidence sintéticas; proposta SLO explicitamente não produtiva;
capacity acceptance; checklist de privacidade/suporte; jornada E2E; relatório de
validação virtual com `SIMULATION_ONLY`/revisão humana.

Contratos propostos: `vena-ia.pilot-evidence/v1` e
`vena-ia.virtual-cnc-plan-validation/v1`, reutilizando os contratos existentes sem
duplicar backup, observabilidade, capacidade, Engineering, CAD ou CNC.

Dados: exclusivamente fixtures sintéticas e evidência agregada/allowlisted fora do
repositório quando aplicável; nenhum dado real de cliente ou máquina.

Riscos: R-021–R-029, R-031–R-034, R-038–R-041 e R-042; simulação não elimina
risco de produção, e métricas descartáveis não constituem SLA/SLO produtivo.

Testes implementados: jornada piloto sintética; isolamento organizacional; restore;
incidente; readiness/degradação; carga-alvo bounded; acessibilidade; privacidade;
rollback; evidência/checksum; plano CNC neutro virtual sem G/M-code, transmissão ou máquina.

Critérios de aceite: todos os gates possuem dono/evidência/rollback; falha é explícita;
zero dado real e zero liberação CNC; aceite humano registrado; nenhuma afirmação de
capacidade produtiva, deploy, SLA ou segurança de máquina.

Condição de avanço: CTO e proprietário aceitam formalmente a evidência do piloto
sintético e tratam riscos residuais; qualquer piloto externo/deploy continua missão separada.

Fora do escopo: deploy, empresa/usuário real, publicação comercial, monitoramento
externo, serviço pago, produção, pós-processador, G-code/M-code, DNC, toolpath ou controle CNC.

Package 3: não proposto. Os dois Packages acima cobrem as entregas oficiais sem
fragmentação artificial; nova decomposição exige decisão registrada.

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

### Decomposição oficial — TASK-V20-001

**Estado:** `APROVADA — CTO`. A menor decomposição sustentada pelas dependências
reais possui três Packages sequenciais; nenhum pode pular o aceite do anterior.
Package 1 está `APPROVED_FOR_IMPLEMENTATION`; Packages 2 e 3 estão `NOT_STARTED`.

#### Dependências reutilizáveis v1.2–v1.9

| Versão | Evidência real reutilizada na v2.0 | Lacuna que não deve gerar duplicação |
|---|---|---|
| v1.2 | auth, Redis security store, revogação/rate limit e audit events | manter token+banco como autoridade; não criar auth paralela |
| v1.3 | contratos PostgreSQL/MinIO/backup-set/encrypted set, restore e retenção | custódia/ambiente produtivo continuam externos |
| v1.4 | observability/metrics, correlation, audit e incident drill | métricas/tracing seguem locais sem backend externo aprovado |
| v1.5 | `vena-ia.job/v1`, worker/recovery/idempotência | novos trabalhos longos devem reutilizar jobs; OCR continua adiado |
| v1.6 | runtime/resilience/capacity policies e evidence descartável | capacidade não é SLO/SLA produtivo |
| v1.7 | catalogs, selection, recommendation e engineering review report | regras são preliminares e não selecionam processo produtivo |
| v1.8 | geometry analysis/features e feature planning | corpus/cobertura conservadores; nenhum intent/manufaturabilidade implícitos |
| v1.9 | Organization/Team, readiness, pilot evidence/integrity/rollback e CNC virtual validation | isolamento/evidence continuam sintéticos e R-042/R-043 monitorados |

Inconsistências registradas naquele gate: o Package 1 resolveu de forma aditiva a
ausência de `schema_version`/traceability do `CNCPlanPreview`; Packages 2–3 resolveram
a fronteira Research e dashboard/evidence. Após a release, permanece pendente a
tenancy organization-scoped dos catálogos Engineering.

#### Auditoria do fluxo integrado

| Elo | Contrato/implementação existente | Entrada → saída e revisão | Lacuna real para v2.0 |
|---|---|---|---|
| CAD | `vena-ia.geometry-analysis/v1`; análise STEP autenticada com parser textual + OCCT controlado | documento STEP autorizado → geometria, rastreabilidade, limitações; revisão humana | resultado existe isoladamente, sem execução integrada persistida/composta |
| Feature recognition | `vena-ia.geometry-features/v1`; rule `1.0.0` | topologia válida → primitivas e through hole estrito; revisão humana | cobertura conservadora é limitada e o resultado ainda precisa ser encadeado sem inferir intenção |
| Engineering recommendation | `vena-ia.engineering-catalog/v1`, `engineering-selection/v1`, `engineering-recommendation/v1` | material/máquina/ferramenta versionados → compatibilidade, parâmetros, tempo/custo preliminares; revisão humana | catálogos são globais autenticados e a recomendação não representa processo liberado |
| CAM preliminar / process planning | `vena-ia.feature-planning/v1`; `FeaturePlanningBridge` | feature suportada + catálogos explícitos → `DRILLING_CANDIDATE`, assumptions, missing inputs e recommendation opcional | somente through hole; não há orquestração E2E nem contrato agregado de workflow; setup/fixture/tolerância permanecem ausentes |
| Plano CNC neutro | preview `/cnc/plan/preview`; contrato aditivo `vena-ia.cnc-neutral-plan/v1`; validação `vena-ia.virtual-cnc-plan-validation/v1` | planning/recommendation refs + parâmetros allowlisted → preview `SIMULATION_ONLY_REQUIRES_HUMAN_REVIEW`, `executable_output=false` | Package 1 resolveu versionamento/traceability; validação física e produção continuam proibidas |
| Relatório | `vena-ia.engineering-review-report/v1` e Research Report separado | recommendation ou síntese RAG → conclusão limitada, evidências/checklist e revisão humana | nenhum relatório único referencia CAD, feature, planning, CNC neutro e evidência científica como uma cadeia |

**CAM preliminar na v2.0** significa exclusivamente process planning: candidatos de
operação, assumptions de setup, compatibilidade material–máquina–ferramenta,
parâmetros determinísticos e estimativas de tempo/custo. Não contém coordenadas,
toolpath, pós-processador, G-code, M-code, NC/DNC ou execução.

#### Package 1 — Integrated Engineering Workflow Foundation

**Estado:** `COMPLETE / RELEASED v2.0.0`.

Objetivo: compor o núcleo determinístico CAD → features → engineering → CAM
preliminar → plano CNC neutro → relatório, reutilizando serviços e regras existentes.

Escopo aprovado:

* contrato aditivo `vena-ia.integrated-engineering-workflow/v1`, com referências às
  versões upstream, inputs/outputs, assumptions, limitations, uncertainty,
  traceability e review status;
* formalização aditiva de `vena-ia.cnc-neutral-plan/v1` sobre o preview existente,
  sempre `SIMULATION_ONLY`, `executable_output=false` e human review;
* orquestração no Modular Monolith, sem duplicar parser, feature recognizer,
  catálogo, rules, fórmulas, CNC preview ou report builder;
* falha explícita/partial quando feature, catálogo, tolerância, fixture, setup ou
  evidence necessária estiver ausente;
* nenhuma persistência/migration presumida; qualquer necessidade deve ser provada na
  ordem funcional e registrada antes da implementação.

Gate de saída: cadeia rastreável e determinística, isolamento/autorização preservados,
relatório integrado não executável e nenhum salto de lacuna como sucesso.

Evidência Package 1: `POST /engineering/workflows` compõe uma única análise CAD com
os contratos existentes, usa ID determinístico derivado do input, preserva estados
fechados e formaliza `vena-ia.cnc-neutral-plan/v1` sobre o serviço existente. Nenhuma
persistência, fila ou migration foi necessária. Catálogos Engineering permanecem
globais autenticados; o workflow não concede escopo organizacional e o acesso ao
documento continua fail-closed por ownership. R-044 está mitigado parcialmente e
monitorado; R-045 permanece aberto/gate.

#### Package 2 — Specialized Assistance and Grounded Research Integration

**Estado:** `COMPLETE / RELEASED v2.0.0`. Package 1 também está `COMPLETE`.

Objetivo: acrescentar assistência especializada somente sobre o núcleo determinístico
aprovado e conectar pesquisa fundamentada sem permitir que IA substitua regra ou
revisão humana.

Perfis conceituais mínimos: CAD analysis, manufacturing/engineering, research e
documentation/reporting. São perfis allowlisted sobre `AIService` e contratos
existentes, não processos autônomos, swarm, novo provider ou microserviços. Toda
saída deve citar o contrato determinístico/evidence consumido, expor limitações e
permanecer sugestão revisável.

Research reutiliza Documents/RAG, chunks, evidência documento/página/chunk,
referências heurísticas, síntese grounded, DOE preliminar, ANOVA apenas descritiva e
Research Report. O Package 2 resolve de forma aditiva a versão pública comum e o
bridge rastreável ao workflow. Validação científica autônoma continua inexistente;
grounding insuficiente falha fechado e nunca produz decisão científica.

Gate de saída: agentes não alteram resultados determinísticos, fontes continuam
autorizadas/rastreáveis, prompt injection permanece tratado como dado não confiável
e overclaim científico é bloqueado.

Evidência Package 2: `vena-ia.specialized-assistance/v1` expõe quatro perfis
allowlisted que somente explicam um snapshot determinístico reconstruído; o input
trace é separado da resposta generativa. O bridge
`vena-ia.grounded-research-assistance/v1` adiciona citations estruturadas e mapeia
aditivamente synthesis/evidence, DOE preliminar, ANOVA descritiva e Research Report.
Prompt injection é dado não confiável; provider failure preserva o workflow; output
com sintaxe CNC ou claim de autoridade é bloqueado. Nenhuma migration ou UI foi criada.

#### Package 3 — Operational Dashboard, Evidence and v2.0 Consolidation

Estado: `COMPLETE / RELEASED v2.0.0`. Packages 1–3 estão `COMPLETE`; não existe
Package 4.

Objetivo: expor o workflow já aprovado e fechar evidence/E2E/release sem criar lógica
de domínio no frontend.

O frontend atual cobre projeto, documentos, jobs, chat RAG e relatórios. Faltam
visões integradas de CAD/features, catálogo/recommendation/planning, plano CNC neutro,
Organization/readiness e pilot evidence/status. O Package propõe somente essas
lacunas funcionais, estados de falha/partial, revisão humana, acessibilidade e E2E;
redesign cosmético não é escopo.

Reutilizar auth, Organization/Team, audit, backup/recovery, observability, async jobs,
resilience, capacity e pilot evidence. Não criar subsistema operacional paralelo.

Gate de saída: regressão integral; E2E engineering; isolation/security;
restore/observability/resilience/load; validação científica; simulação controlada;
documentação técnica/científica/comercial e Release Candidate v2.0. Deploy continua
missão externa separada.

Estratégia de testes futura por gate: Package 1 cobre contratos, compatibilidade,
cadeia E2E determinística, partial/failure, ownership/isolation e neutralidade CNC;
Package 2 cobre grounding, citações, prompt injection, ausência de evidence,
não sobrescrita de rules e limites DOE/ANOVA; Package 3 cobre acessibilidade,
frontend/API E2E, restore, observability, resilience, carga sintética e regressão
integral. O Package 3 executa esses gates sem nova migration e prepara
`docs/RELEASE_NOTES_v2.0.0.md`; publicação depende de ordem posterior.

#### Riscos e limites absolutos

R-044–R-047 são gates abertos de integração, produção aparente, autoridade de agente
e overclaim científico. `base operacional pronta para decisão de produção` significa
somente evidência técnica organizada para decisão humana futura; nunca
`PRODUCTION_APPROVED`.

```text
NO_EXECUTABLE_GCODE
NO_EXECUTABLE_MCODE
NO_TOOLPATH
NO_POSTPROCESSOR
NO_NC_FILE
NO_DNC
NO_CNC_TRANSMISSION
NO_MACHINE_CONTROL
```

Após a Release v2.0, qualquer trabalho v2.x→v3.0 exige extensão formal do roadmap e
aprovação do CTO antes de código. `TODAY_TARGET=V3_0` não substitui esse gate.

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

# 10. Extensão proposta v2.0 → v3.0 — TASK-V30-000

**Estado:** `APROVADA — CTO`
**Baseline:** `v2.0.0 RELEASED_AND_FULLY_VERIFIED`
**Princípio:** menor quantidade sustentável de versões; nenhum código autorizado.

## 10.1 Diagnóstico da baseline

A v2.0 consolidou autenticação, ownership, Organization/Team/Membership, auditoria,
backup/recovery, observabilidade, jobs, resiliência, evidência de capacidade, CAD
STEP, geometria, reconhecimento conservador de features, catálogos e recomendações,
planning preliminar, plano CNC neutro, workflow integrado, assistência bounded,
Research grounded, dashboard, evidence sintética, acessibilidade e contratos
versionados. Essas capacidades devem ser evoluídas, não reimplementadas.

Dívidas a resolver: catálogos Engineering globais sem ownership organizacional;
cobertura geométrica restrita; planning limitado a features aprovadas; ausência de
evidência de simulação física/geométrica e de um digital thread persistente com
provenance integral. Limites intencionais: decisão científica autônoma, produção,
toolpath, postprocessor, G/M-code, NC/DNC, transmissão e controle de máquina continuam
proibidos até decisões e gates próprios do proprietário.

## 10.2 Estrutura mínima proposta

Foram rejeitados dois extremos: salto direto v2.0→v3.0, que mistura migration de
segurança, evolução geométrica e consolidação; e quatro ou mais versões, que criariam
gates cosméticos. Duas versões intermediárias separam dependências reais:

1. **v2.1 — Enterprise Engineering Governance:** fecha primeiro a fronteira de dados
   Engineering por organização, condição para ampliar conhecimento e automação.
2. **v2.2 — Advanced Engineering Planning & Verification:** amplia geometria/planning
   determinísticos e cria evidence de verificação não produtiva sobre a tenancy segura.
3. **v3.0 — Manufacturing Intelligence & Digital Thread:** consolida rastreabilidade
   integral, inteligência bounded e governança científica sobre artefatos aprovados.

## 10.3 v2.1 — Enterprise Engineering Governance

**Objetivo:** tornar dados e catálogos Engineering organization-scoped sem quebrar
contratos públicos ou permitir acesso cruzado.

**Package 1 — Ownership and compatibility — `COMPLETE / RELEASED v2.1.0`:** modelo de ownership organizacional,
política de leitura/escrita, estratégia de migration/backfill, compatibilidade para
dados legados, índices e contrato aditivo. Depende da fronteira Organization/Team
v1.9. Riscos: R-042 e R-048.

**Estado de execução:** `COMPLETE / RELEASED v2.1.0`. A implementação usa
Organization scope (sem Team scope), separa referências de sistema de registros
legados bloqueados, preserva schemas v1 por adição e introduz a migration reversível
`e61c4f8a2b90`.

**Package 2 — Governance evidence — `COMPLETE / RELEASED v2.1.0`:** autorização fail-closed, auditoria de lifecycle,
testes cross-org/cross-team, export/retention compatíveis, documentação e gate de
migration reversível. Depende do Package 1. Não inclui SSO/SCIM, billing, cliente real
ou deploy.

O Package 2 usa read model por recurso, sem ledger/persistência/migration/export em
massa. A PR #25, tag anotada e GitHub Release publicam a v2.1.0. v2.2 e v3.0
permanecem `NOT_STARTED` até nova ordem formal do CTO.

**Aceite:** zero authority em body/header; isolamento e backward compatibility
provados; migration upgrade/downgrade testada; catálogos globais legados não vazam
nem são silenciosamente promovidos; revisão humana preservada.

**Condição de avanço:** v2.1 integrada e riscos de tenancy aceitos antes de ampliar
features, planning ou agentes.

## 10.4 v2.2 — Advanced Engineering Planning & Verification

**Objetivo:** ampliar cobertura determinística e evidence de verificação mantendo
planning separado de execução.

**Package 1 — General Geometry Evidence — `COMPLETE / RELEASED v2.2.0`:** contrato
`vena-ia.geometry-topology-evidence/v1` geral e versionado para topologia B-Rep,
IDs canônicos/replay, unidades/transformação, tolerâncias separadas, relações e
classificação de superfícies/curvas. Corpus sintético e falhas fechadas cobrem
unidade ambígua, topologia inválida e limites. O evidence não é uma lista de features
nem implica intenção ou manufaturabilidade. Riscos: R-019, R-039 e R-040.

**Package 2 — Manufacturing Interpretation & Verified Process Planning —
`COMPLETE / RELEASED v2.2.0`:** manufacturing geometry model separa facts/intents, exige
stock provenanced, protege final surfaces, registra removal/unknown/accessibility e
propõe datum/WCS/setup 3-axis/2.5D. Plano versionado usa intent explícito, catálogos
organization-scoped, precedência e verification evidence de coerência/replay. Falha
e ausência permanecem explícitas. Não há toolpath, postprocessor, G/M-code, NC/DNC,
simulation física ou machine connectivity. Riscos: R-041, R-044, R-045 e R-049.

**Aceite:** corpus de falsos positivos/negativos; provenance de rules/catalogs;
planning reproduzível; simulation evidence marcada `NON_PRODUCTION` e insuficiente
para validação física; testes de boundary CNC; revisão humana obrigatória.

**Condição de avanço:** concluída pela PR #27, Squash Merge `28d592c` e release
v2.2.0. A próxima etapa autorizada é a fronteira controlada v2.3.

## 10.5 v2.3 — Controlled CAD-to-G-code Validation

**Objetivo:** validar de modo controlado e não produtivo a cadeia determinística
CAD→candidato→verificadores independentes, somente após aprovação integral da v2.2.

**Packages aprovados no roadmap:** candidato bounded 3-axis/2.5D com verifier
independente; postprocessor sintético versionado com verifier RS274 independente;
e verificação Level-2 de remoção/colisão com blind-test harness. Gates G0–G9 não
autorizam uso físico, produção, machine-send, DNC ou cycle start.

**Package 1 — Bounded 3-axis / 2.5D Toolpath — `READY_FOR_CTO_REVIEW`:** contrato
`vena-ia.toolpath-candidate/v1` e verificador independente v1 iniciam somente
segmentos lineares bounded para regiões do plano verificado. A saída mantém
`production_authority=false`, revisão humana e não inclui postprocessor ou G-code.

**Package 2 — Synthetic Postprocessor + RS274 Safe Subset — `READY_FOR_CTO_REVIEW`:** alvo
somente sintético `VENA_SYNTHETIC_3AXIS_MILL_V1` usa G21/G17/G90/G94, G0/G1 lineares
e M30. O parser independente rejeita macros, variáveis, arcos, ciclos, compensação,
offsets, extensões de fornecedor, turning e multi-axis.

**Package 3 — Level-2 + Controlled Blind Harness — `READY_FOR_CTO_REVIEW`:** o
verificador independente reconstrói segmentos e aplica evidência bounded de stock,
cobertura, sweep cilíndrico simplificado, envelope protegido, rapid e fixture
keep-out. O harness congela artifacts/hashes e G0–G9 antes da adjudicação do holdout
selado. Sem revisão humana real, G9 fica `PENDING_REVIEW` e readiness permanece
false. Não há B-Rep subtraction exata, holder collision, cinemática, machine-send,
uso físico ou autoridade produtiva.

## 10.6 v3.0 — Manufacturing Intelligence & Digital Thread

**Objetivo arquitetural:** transformar o workflow integrado em um digital thread
versionado e auditável que conecta CAD→features→engineering→planning→Research→
verification→review→report, sem promover IA, simulação ou planning a autoridade
produtiva.

**Package 1 — Versioned Digital Thread — `RELEASED v3.0.0`:** identidade e provenance de artefatos,
relações imutáveis/versionadas, lifecycle, retention e replay; ownership organizacional
herdado da v2.1 e evidence determinística herdada da v2.2.

**Package 2 — Bounded Manufacturing Intelligence — `RELEASED v3.0.0`:** perfis especializados continuam
bounded; eventual orchestration/tool calling é read-only, allowlisted, auditável e
incapaz de mutar fatos. Research evolui em qualidade de fontes, reprodutibilidade,
datasets, métodos estatísticos e relatórios sob revisão humana. Stateful agents,
swarm e execução são rejeitados sem nova decisão. Riscos: R-046, R-047 e R-050.

**Aceite:** trace integral e reproduzível; isolamento organizacional; separação visual
e contratual entre fato, evidence, sugestão e decisão humana; quality gates científicos;
falha segura; nenhuma saída executável ou alegação de production readiness.

**Fora do escopo:** deploy, piloto/cliente real, publicação comercial, billing,
SSO/SCIM, decisão científica autônoma, toolpath, postprocessor, G/M-code, NC/DNC,
machine connectivity e controle CNC. Cada item exige gate reservado ao proprietário.

## 10.6 Matriz de dependências e gates

| Capacidade atual | Dívida/limite | Versão | Package | Risco | Gate |
|---|---|---|---|---|---|
| Organization/Team + catálogos globais | ownership Engineering ausente | v2.1 | P1–P2 | R-042/R-048 | migration, auth e isolamento |
| STEP/OCCT + features conservadoras | cobertura limitada | v2.2 | P1 | R-019/R-039/R-040 | corpus e regra versionada |
| recommendation/planning preliminar | setup/sequência/evidence limitados | v2.2 | P2 | R-041/R-044 | determinismo e replay |
| CNC neutral e capacity sintética | simulação pode gerar falsa confiança | v2.2 | P2 | R-045/R-049 | non-production e revisão humana |
| workflow v2.0 | provenance entre artefatos não persistida | v3.0 | P1 | R-044 | digital thread versionado |
| assistance/Research grounded | risco de authority/overclaim | v3.0 | P2 | R-046/R-047/R-050 | tools read-only, evidence e revisão |

## 10.7 Gates de governança

Cada Package exige ordem formal do CTO. Deploy, dados pessoais, cliente real,
publicação comercial, custos, credenciais, production approval, machine connectivity,
CNC executável e ações externas irreversíveis continuam exclusivos do proprietário.
Esta proposta não autoriza código, migration ou criação de runtime contract.

## 10.8 Registro de entrega — TASK-V30-000

**Objetivo:** auditar a baseline v2.0 e propor evolução rastreável até v3.0.
**Escopo:** roadmap, dependências, riscos, decisão e controles CTO; somente docs.
**Testes:** diff/check, referências, sequências de IDs e consistência documental.
**Aceite:** duas versões intermediárias justificadas por dependências reais, Packages
mínimos, limites e gates explícitos.
**Próximo passo:** implementar somente v2.1 Package 1 na branch funcional autorizada;
todos os Packages posteriores permanecem `NOT_STARTED`.

---

## 11. v3.1 — Controlled Test Environment

**TASK-V31-002:** `IMPLEMENTED / READY_FOR_CTO_REVIEW`.

A v3.1 integra, sem duplicação e sem nova persistência, os contratos publicados de
CAD, topology, Manufacturing Geometry, verified process plan, toolpath candidate,
postprocessor sintético, Level-1/Level-2, blind validation e Digital Thread. A entrega
inclui orchestration autenticada, required-user-input explícito, display de G0–G9 e
download controlado com prova curta vinculada a identidade, tenancy e hashes.

**Gate:** G0–G8 com evidence determinística, G9 obrigatoriamente
`PENDING_AUTHORITATIVE_REVIEW`, `PHYSICAL_USE_AUTHORIZED=false`. Não inclui v3.2,
deploy, produção, teste físico, machine-send, DNC/NC transfer, cycle start ou controle
direto. Revisão da Draft PR/CI pelo CTO é o próximo passo.

**TASK-V31-003 — G9/external-validation preparation:** `IMPLEMENTED / READY_FOR_CTO_REVIEW`.
The evidence boundary now distinguishes automatic integrity evidence, authorized human
adjudication, independent external-simulation evidence and prerequisites that would
require a separate Owner-authorized physical-test protocol. This task creates no G9
transition, physical authority, machine connection or v3.2 scope.

---

**Fim do Documento 03 — Roadmap Executivo Vena_IA até v3.1**
