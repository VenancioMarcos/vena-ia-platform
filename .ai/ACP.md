# ACP.md — Artificial Collaboration Protocol (Vena_IA)

**Status:** Especificação Oficial
**Versão:** 1.0
**Documentos relacionados:** `AGENTS.md`, `GOVERNANCE.md`, `.ai/ROLES.md`, `.ai/CONTEXT_TEMPLATE.md`

---

## 1. Objetivo

O ACP define como agentes de IA (ChatGPT, Claude, Codex, GitHub Copilot, Gemini e agentes próprios) trocam contexto, propõem mudanças e registram decisões dentro do repositório Vena_IA Platform, sem depender de memória compartilhada entre sessões ou entre modelos diferentes.

O repositório é o meio de comunicação. O ACP é o formato dessa comunicação.

---

## 2. Princípios do Protocolo

1. **Estado explícito, não implícito.** O estado do projeto vive em `CONTEXT.md`, não na memória de nenhum agente.
2. **Rastreabilidade.** Toda mudança relevante deve poder ser rastreada até uma decisão documentada.
3. **Idempotência de leitura.** Qualquer agente, em qualquer momento, deve conseguir reconstruir o contexto necessário lendo apenas o repositório.
4. **Sem autoridade implícita.** Nenhum agente assume que uma decisão de outro agente é final sem que esteja registrada como `Aprovada` em `docs/DECISIONS.md` ou em um ADR.
5. **Escopo explícito.** Todo agente opera dentro do escopo definido na missão recebida; expandir escopo sem registrar a mudança é uma violação do protocolo.

---

## 3. Ciclo de Trabalho ACP

```text
[1] RECEBER missão (ver .ai/PROMPT_TEMPLATE.md)
[2] CARREGAR contexto (CONTEXT.md, PROJECT.md, DECISIONS.md, ADRs relevantes)
[3] VALIDAR compatibilidade da missão com o estado atual
[4] EXECUTAR dentro do escopo definido
[5] DOCUMENTAR a entrega (Registro de Entrega — PROJECT.md, Seção 19)
[6] REGISTRAR decisões novas (ADR ou DECISIONS.md), se houver
[7] ATUALIZAR CONTEXT.md com o novo estado
[8] ENTREGAR usando .ai/CONTEXT_TEMPLATE.md para o próximo agente, se aplicável
```

---

## 4. Formato de Entrega (Registro de Entrega)

Toda entrega de um agente de IA neste repositório deve conter:

```markdown
## Objetivo
## Escopo
## Arquivos Criados
## Arquivos Modificados
## Testes Realizados
## Critérios de Aceitação
## Próximos Passos
```

Este formato é obrigatório e vem de `PROJECT.md`, Seção 19.

---

## 5. Resolução de Conflitos Entre Agentes

Se dois agentes propuserem soluções conflitantes para o mesmo problema:

1. Nenhuma das duas é aplicada automaticamente.
2. O conflito é registrado como `Em revisão` em `docs/DECISIONS.md`.
3. A resolução exige aprovação humana ou um ADR que formalize qual alternativa prevalece.

---

## 6. Limites de Autonomia

Nenhum agente de IA, sob este protocolo, tem autonomia para:

* criar contas ou serviços externos;
* gerenciar credenciais, tokens ou segredos;
* realizar pagamentos ou assumir compromissos financeiros;
* conceder acesso externo ao repositório ou à infraestrutura;
* publicar o repositório ou alterar sua visibilidade;
* tomar decisões estratégicas irreversíveis.

Essas ações exigem aprovação humana explícita, conforme `PROJECT.md`, Seção 5.

---

## 7. Versionamento do Protocolo

Mudanças neste protocolo são, elas mesmas, decisões arquiteturais e devem gerar um ADR (ver `docs/adr/ADR-0002-ai-collaboration-protocol.md`).
