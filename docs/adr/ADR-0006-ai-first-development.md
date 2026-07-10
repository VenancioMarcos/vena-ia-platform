# ADR-0006 — Desenvolvimento AI-First

**Status:** Aprovado
**Data:** 2026-07-10
**Responsável:** Líder Técnico / Arquiteto de Software

---

## Contexto

O Vena_IA Platform é projetado desde o início para ser majoritariamente implementado, revisado e mantido com apoio intensivo de agentes de IA, e não apenas por um time humano tradicional com IA como ferramenta auxiliar ocasional.

## Problema

Arquiteturas e processos pensados exclusivamente para times humanos (documentação mínima, contexto tácito, convenções não escritas) não escalam bem quando múltiplos agentes de IA, sem memória compartilhada, precisam operar no mesmo código-base.

## Alternativas Consideradas

1. **Processo tradicional de engenharia de software**, com IA usada apenas como autocomplete pontual — rejeitada: desperdiça o potencial de IAs atuarem como arquitetos, revisores e implementadores completos.
2. **AI-first**: arquitetura, documentação e processos desenhados assumindo que agentes de IA são colaboradores primários, com humanos em papel de revisão e aprovação estratégica — **Escolhida**.

## Decisão

Adotar desenvolvimento **AI-first**: toda decisão de processo (estrutura de repositório, granularidade de documentação, formato de commits, templates de missão) é otimizada para ser executável e compreensível por agentes de IA, mantendo o humano como aprovador final de decisões estratégicas e irreversíveis.

## Consequências

* Exige investimento maior em documentação estruturada (`.ai/`, ADRs, `CONTEXT.md`) do que um projeto tradicional exigiria.
* Permite que múltiplos agentes de IA contribuam de forma consistente sem supervisão humana constante.
* Cria dependência de disciplina de processo — se a documentação não for mantida atualizada, o modelo AI-first perde eficácia rapidamente.
