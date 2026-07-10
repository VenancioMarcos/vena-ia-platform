# ADR-0002 — Adoção do Artificial Collaboration Protocol (ACP)

**Status:** Aprovado
**Data:** 2026-07-10
**Responsável:** Documentation Engineer / Repository Architect

---

## Contexto

O Vena_IA Platform é desenvolvido com apoio de múltiplos agentes de IA (ChatGPT, Claude, Codex, GitHub Copilot, Gemini e agentes próprios), operando em sessões independentes e sem memória compartilhada entre si.

## Problema

Sem um protocolo explícito de comunicação, cada agente tende a reconstruir contexto de forma inconsistente, repetir trabalho, contradizer decisões anteriores ou expandir escopo sem registro — gerando perda de conhecimento e retrabalho.

## Alternativas Consideradas

1. **Sem protocolo formal** — cada agente decide como documentar seu trabalho. Rejeitada: gera inconsistência entre estilos de documentação e perda de rastreabilidade.
2. **Protocolo verbal/informal, apenas via instruções em cada sessão** — rejeitada: não é versionado, se perde entre sessões.
3. **Protocolo formal versionado (ACP)**, com ciclo de trabalho, formato de entrega e template de passagem de contexto padronizados. **Escolhida.**

## Decisão

Adotar o **Artificial Collaboration Protocol (ACP)**, especificado em `.ai/ACP.md`, como protocolo oficial de comunicação entre agentes de IA neste repositório.

## Consequências

* Todo agente deve seguir o ciclo de trabalho ACP (receber, carregar contexto, validar, executar, documentar, registrar, atualizar contexto, entregar).
* Toda entrega relevante segue o formato de Registro de Entrega.
* Mudanças no protocolo em si exigem um novo ADR.
* Custo adicional: agentes gastam parte do orçamento de contexto lendo documentos de protocolo antes de executar tarefas. Considerado aceitável dado o ganho em rastreabilidade.
