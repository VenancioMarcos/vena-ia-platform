# Vena_IA Platform

# Documento Mestre do Projeto — PROJECT.md

## Versão 1.0

**Status:** Documento Fundador  
**Projeto:** Vena_IA — Engenharia Inteligente para Manufatura CNC  
**Modelo de atuação:** Líder Técnico + Engenheiro de IA + Pesquisador de Engenharia  
**Modelo operacional:** GPT-5.5 (médio)

---

# 1. Identidade do Projeto

## Nome

**Vena_IA Platform**

## Objetivo

Desenvolver uma plataforma profissional baseada em Inteligência Artificial aplicada à Engenharia Mecânica, integrando:

* CAD;
* CAM;
* CNC;
* Simulação;
* Pesquisa científica;
* Manufatura inteligente;
* Gestão industrial.

O projeto possui três objetivos simultâneos:

1. Plataforma tecnológica de software.
2. Base científica para pesquisa de mestrado e publicações.
3. Produto comercial escalável para engenharia e indústria.

---

# 2. Missão

Criar um copiloto inteligente de engenharia capaz de auxiliar profissionais desde a interpretação de um modelo CAD até:

* planejamento de fabricação;
* definição de processos;
* cálculo de parâmetros;
* análise técnica;
* geração de documentação;
* apoio à programação CNC.

---

# 3. Visão

Ser uma referência em Inteligência Artificial aplicada à Engenharia Mecânica e Manufatura Inteligente.

---

# 4. Objetivos Estratégicos

A plataforma deverá evoluir para oferecer:

* Assistente de Engenharia Mecânica;
* Base de conhecimento técnica;
* Leitura de arquivos STEP, STL, DXF e IGES;
* Reconhecimento de características geométricas;
* Planejamento de usinagem;
* Seleção automática de ferramentas;
* Cálculo de parâmetros de corte;
* Estimativa de tempo e custo;
* Geração de G-code;
* Simulação;
* Relatórios técnicos;
* Dashboard industrial;
* Indicadores de manufatura.

---

# 5. Papel do ChatGPT Work

O ChatGPT Work será considerado o ambiente oficial de desenvolvimento e gestão técnica.

Atuação:

* Arquiteto de Software;
* Líder Técnico;
* Desenvolvedor Principal;
* Especialista em IA;
* Especialista CAD/CAM/CAE;
* Revisor de Código;
* Pesquisador Técnico.

## Autonomia

Executar decisões técnicas automaticamente quando possível.

Solicitar aprovação humana somente para:

* criação de contas;
* credenciais;
* pagamentos;
* acessos externos;
* publicação;
* decisões estratégicas irreversíveis.

---

# 6. Princípios do Projeto

Prioridades:

1. Qualidade.
2. Escalabilidade.
3. Manutenibilidade.
4. Documentação.
5. Testabilidade.
6. Performance.

Nunca sacrificar arquitetura por velocidade de implementação.

---

# 7. Arquitetura Oficial

## Estratégia

**Modular Monolith**

## Justificativa

Escolhida por permitir:

* desenvolvimento inicial mais simples;
* menor complexidade operacional;
* facilidade de testes;
* organização por domínio;
* futura migração para microsserviços.

---

# 8. Stack Tecnológica Oficial

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* shadcn/ui

## Backend

* Python 3.13
* FastAPI
* SQLAlchemy
* Alembic
* Pydantic v2

## Banco de Dados

* PostgreSQL

## Banco Vetorial

* pgvector

## Cache

* Redis

## Armazenamento

* MinIO

## Infraestrutura

* Docker
* Docker Compose

## Integração

* GitHub Actions

## Inteligência Artificial

* OpenAI API
* Embeddings
* RAG
* Agentes especializados

---

# 9. Estrutura Oficial do Projeto

```text
Vena_IA

apps/
├── api/
└── web/

packages/
├── ui/
├── auth/
├── engineering/
├── ai/
└── database/

services/
├── rag/
├── parser-step/
├── parser-dxf/
└── parser-stl/

docs/
tests/
docker/
scripts/
.github/
```

---

# 10. Módulos Principais

## Core

Responsável por:

* usuários;
* autenticação;
* projetos;
* dashboard;
* arquivos;
* chat.

## Engenharia

Responsável por:

* CAD;
* CAM;
* CNC;
* materiais;
* ferramentas;
* processos;
* simulação.

## Pesquisa

Responsável por:

* artigos científicos;
* PDFs;
* referências;
* DOE;
* ANOVA;
* relatórios.

## Enterprise

Responsável por:

* Lean Manufacturing;
* OEE;
* PCP;
* ERP;
* Analytics.

---

# 11. Agentes Especializados de IA

A arquitetura deverá evoluir para agentes especializados.

## Agente Engenharia

Conhecimento geral em engenharia mecânica.

## Agente CAD

Interpretação de modelos 3D.

## Agente CAM

Estratégias de fabricação e usinagem.

## Agente CNC

Programação CNC e G-code.

## Agente Pesquisa

Literatura científica e metodologia.

## Agente Simulação

FEA, elementos finitos e análise estrutural.

## Agente Lean

Manufatura enxuta e melhoria contínua.

---

# 12. Roadmap Oficial

## Fase 1 — Foundation

Infraestrutura:

* repositório;
* arquitetura;
* containers;
* banco;
* documentação.

## Fase 2 — Core

Sistema principal:

* usuários;
* projetos;
* dashboard.

## Fase 3 — Authentication

Controle de acesso.

## Fase 4 — Upload

Gerenciamento de arquivos.

## Fase 5 — Chat

Assistente IA.

## Fase 6 — RAG

Base de conhecimento.

## Fase 7 — CAD

Leitura e interpretação STEP.

## Fase 8 — CAM

Estratégias de usinagem.

## Fase 9 — CNC

G-code.

## Fase 10 — Simulation

FEA.

## Fase 11 — Research

Pesquisa científica.

## Fase 12 — Enterprise

Gestão industrial.

---

# 13. Banco de Dados Inicial

Entidades principais:

* Users;
* Projects;
* Files;
* Chats;
* Messages;
* Documents;
* Embeddings;
* Machines;
* Materials;
* Tools;
* Strategies;
* Operations;
* Experiments;
* Reports.

---

# 14. Padrões de Desenvolvimento

Todo código deverá seguir:

* Clean Architecture;
* SOLID;
* Clean Code;
* Domain Driven Design quando aplicável;
* API REST;
* OpenAPI;
* Testes automatizados;
* Conventional Commits;
* Semantic Versioning.

---

# 15. Documentação

Toda decisão arquitetural deverá gerar:

**ADR — Architecture Decision Record**

Toda funcionalidade deverá possuir:

* objetivo;
* escopo;
* implementação;
* testes;
* critérios de aceitação.

---

# 16. Estratégia de Testes

Todos os módulos deverão possuir testes automatizados.

Prioridades:

* regras de negócio;
* serviços;
* APIs;
* integrações críticas.

---

# 17. Objetivo do MVP

A primeira versão deverá permitir:

* Login;
* Dashboard;
* Criação de projetos;
* Upload de arquivos;
* Chat com IA;
* Base de conhecimento;
* Histórico de interações.

---

# 18. Objetivo de Longo Prazo

Fluxo completo desejado:

```text
Importar STEP
        ↓
Reconhecimento de features
        ↓
Sugestão de ferramentas
        ↓
Cálculo de parâmetros
        ↓
Estimativa de tempo
        ↓
Estimativa de custo
        ↓
Planejamento do processo
        ↓
Geração de G-code
        ↓
Relatório técnico
```

---

# 19. Forma Oficial de Trabalho

Cada entrega deverá conter:

* Objetivo;
* Escopo;
* Arquivos criados;
* Arquivos modificados;
* Testes realizados;
* Critérios de aceitação;
* Próximos passos.

Nunca gerar código sem atualizar a documentação correspondente.

---

# 20. Controle de Evolução

Toda alteração significativa deverá:

1. Apresentar justificativa técnica.
2. Avaliar impacto.
3. Registrar ADR.
4. Atualizar documentação.

---

# 21. Regra Final

Este documento é a **fonte oficial de verdade do projeto Vena_IA**.

Todas as decisões técnicas, arquiteturas, implementações e evoluções devem permanecer consistentes com este documento.

Caso uma solução superior seja identificada, ela deverá ser apresentada, justificada e registrada antes da alteração da direção arquitetural.

---

**Fim do Documento Mestre Vena_IA Platform v1.0**
