# PROMPT_TEMPLATE.md — Template Oficial de Missão para Agentes de IA

**Status:** Especificação Oficial
**Versão:** 1.0
**Documento relacionado:** `.ai/ACP.md`, `.ai/CONTEXT_TEMPLATE.md`

---

## 1. Objetivo

Padronizar como uma missão é entregue a qualquer agente de IA trabalhando no Vena_IA Platform, garantindo que a tarefa venha com escopo, contexto e critérios de aceitação claros — independentemente de qual modelo a executa.

---

## 2. Template

```markdown
# MISSÃO DE [TIPO: IMPLEMENTAÇÃO | DOCUMENTAÇÃO | PESQUISA | REVISÃO]

## Projeto
Vena_IA Platform

## Papel
[Papel esperado, conforme .ai/ROLES.md]

## Contexto
[Resumo do estado atual relevante para esta tarefa — pode referenciar CONTEXT.md]

## Objetivo
[O que deve ser alcançado ao final desta missão]

## Escopo
[O que está incluído]

## Fora de Escopo
[O que NÃO deve ser feito nesta missão]

## Tarefas
1. [Tarefa objetiva e verificável]
2. ...

## Regras
[Restrições explícitas: ex. "não implementar backend", "não instalar dependências"]

## Critérios de Aceitação
[Como validar que a missão foi cumprida]

## Resultado Esperado
[Descrição do entregável final]
```

---

## 3. Regras de Preenchimento

* **Objetivo** deve ser uma frase, não um parágrafo.
* **Escopo** e **Fora de Escopo** devem ser explícitos sempre que houver risco de ambiguidade — a ausência de "Fora de Escopo" não autoriza expansão de escopo.
* **Tarefas** devem ser verificáveis (um agente ou humano deve conseguir confirmar objetivamente se foram cumpridas).
* **Critérios de Aceitação** são obrigatórios para qualquer missão que gere artefato versionado.

---

## 4. Relação com o Registro de Entrega

Toda missão criada com este template deve ser respondida com um Registro de Entrega, no formato definido em `.ai/ACP.md`, Seção 4.
