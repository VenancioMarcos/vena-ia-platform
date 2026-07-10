# Vena_IA Platform

# Documento 03 — Roadmap Executivo Vena_IA v1.0

**Status:** Documento Oficial de Planejamento  
**Data:** 2026-07-10  
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

## v0.5 — RAG

Objetivo: criar a base de conhecimento semântica.

Entregas:

* chunking de documentos;
* geração de embeddings;
* armazenamento em pgvector;
* busca semântica;
* respostas com contexto recuperado;
* documentação do pipeline RAG.

Critério de conclusão:

* usuário consegue fazer perguntas sobre documentos carregados no projeto.

---

## v0.6 — CAD Inicial

Objetivo: iniciar interpretação técnica de arquivos CAD.

Entregas:

* serviço `parser-step`;
* leitura inicial de STEP;
* extração de metadados geométricos;
* dimensões básicas;
* volume quando tecnicamente viável;
* relatório técnico preliminar;
* avaliação de OpenCascade ou pythonOCC.

Critério de conclusão:

* usuário consegue carregar um STEP e obter uma análise geométrica inicial.

---

## v0.7 — Engenharia e CAM Inicial

Objetivo: criar a primeira camada de planejamento de manufatura.

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

Entregas:

* biblioteca de artigos;
* ingestão de PDFs científicos;
* extração de referências;
* análise assistida por IA;
* estrutura para DOE;
* estrutura para ANOVA;
* relatórios técnicos e acadêmicos.

Critério de conclusão:

* usuário consegue organizar documentos científicos e gerar sínteses técnicas relacionadas ao projeto.

---

## v1.0 — MVP Vena_IA

Objetivo: entregar a primeira versão funcional da plataforma.

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

**Fim do Documento 03 — Roadmap Executivo Vena_IA v1.0**
