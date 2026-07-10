# ADR-0004 — Modelo de Governança do Projeto

**Status:** Aprovado
**Data:** 2026-07-10
**Responsável:** Documentation Engineer / Repository Architect

---

## Contexto

O projeto envolve um responsável humano (Product Owner / mantenedor) e múltiplos agentes de IA atuando com graus variados de autonomia técnica.

## Problema

Sem regras explícitas de governança, existe risco de um agente de IA tomar decisões irreversíveis (ex.: publicar credenciais, alterar visibilidade do repositório, assumir compromissos externos) sem aprovação humana.

## Alternativas Consideradas

1. **Autonomia total dos agentes de IA** — rejeitada: risco inaceitável para ações irreversíveis ou sensíveis (contas, credenciais, pagamentos, publicação).
2. **Aprovação humana para toda e qualquer ação** — rejeitada: inviabiliza a velocidade de desenvolvimento assistido por IA que é um objetivo central do projeto.
3. **Autonomia técnica ampla, com lista explícita de exceções que exigem aprovação humana** — **Escolhida**, conforme já estabelecido em `PROJECT.md`, Seção 5.

## Decisão

Formalizar em `GOVERNANCE.md` o modelo de governança já praticado: agentes de IA têm autonomia para decisões técnicas, mas devem obter aprovação humana explícita para criação de contas, gestão de credenciais, pagamentos, acessos externos, publicação e decisões estratégicas irreversíveis.

## Consequências

* Reduz risco operacional sem sacrificar velocidade de execução técnica.
* Exige que todo agente conheça e respeite essa lista de exceções (`AGENTS.md`, Seção 3).
* Violações devem ser tratadas como incidentes de governança, registrados em `docs/DECISIONS.md`.
