# GOVERNANCE.md — Governança do Projeto Vena_IA Platform

**Status:** Documento Oficial
**Versão:** 1.0
**Documentos relacionados:** `PROJECT.md`, `AGENTS.md`, `.ai/ACP.md`, `CONTRIBUTING.md`, `SECURITY.md`

---

## 1. Princípio Fundamental

O repositório Git é a **única fonte oficial da verdade** do projeto Vena_IA Platform.

Nenhuma decisão técnica, arquitetural ou estratégica relevante é considerada válida enquanto existir apenas em uma conversa, chat, e-mail ou memória de sessão de qualquer agente — humano ou de IA. Toda decisão relevante deve ser versionada.

---

## 2. Hierarquia de Fontes de Verdade

Em caso de conflito entre fontes de informação, a ordem de prioridade é:

1. Conteúdo versionado no repositório (código e documentação commitados).
2. ADRs em `docs/adr/`.
3. `docs/DECISIONS.md`.
4. `PROJECT.md`.
5. Qualquer instrução dada em conversa não versionada.

Uma instrução em conversa que contradiga um ADR aprovado não deve ser executada sem antes registrar a mudança formalmente (nova decisão ou ADR de substituição).

---

## 3. Estratégia de Documentação

* Toda funcionalidade relevante deve ter: objetivo, escopo, implementação, testes e critérios de aceitação documentados (`PROJECT.md`, Seção 19).
* Toda decisão arquitetural significativa gera um ADR (`docs/adr/`).
* Decisões operacionais menores são registradas em `docs/DECISIONS.md`.
* Documentos institucionais (este, `AGENTS.md`, `ACP.md` etc.) são atualizados por Pull Request, nunca editados silenciosamente.

---

## 4. Política de Segurança

Regras completas em `SECURITY.md`. Resumo:

* Nenhum segredo (API keys, tokens, credenciais, `.env`) é versionado.
* Dados de clientes, prompts proprietários e estratégias de RAG não são publicados no repositório público.
* Toda dependência nova passa por avaliação mínima de risco antes de ser adicionada.

---

## 5. Política de Propriedade Intelectual

* O código e a documentação deste repositório são propriedade da Vena_IA Platform, sob a licença registrada em `LICENSE`.
* Repositório público não implica licença de uso aberta — ver `LICENSE` para os termos exatos.
* Contribuições de terceiros (humanos ou IAs operando em nome de terceiros) exigem concordância explícita com os termos de `CONTRIBUTING.md`.

---

## 6. Colaboração entre IAs

Este projeto é construído com apoio de múltiplos agentes de IA (ChatGPT, Claude, Codex, GitHub Copilot, Gemini e agentes próprios). As regras de colaboração entre eles estão formalizadas em:

* `AGENTS.md` — papéis, responsabilidades e fluxo de trabalho.
* `.ai/ACP.md` — protocolo técnico de comunicação entre agentes.
* `.ai/ROLES.md` — matriz de responsabilidades por tipo de tarefa.

Nenhum agente de IA tem autonomia para: criar contas, gerenciar credenciais, realizar pagamentos, conceder acessos externos, publicar o repositório ou tomar decisões estratégicas irreversíveis sem aprovação humana explícita (`PROJECT.md`, Seção 5).

---

## 7. Processo de Tomada de Decisão

1. Identificar a necessidade de decisão (técnica, arquitetural ou de produto).
2. Avaliar alternativas com trade-offs explícitos.
3. Registrar a decisão:
   * ADR, se for arquitetural, estrutural ou de longo prazo;
   * `docs/DECISIONS.md`, se for operacional ou de acompanhamento.
4. Comunicar a decisão via Pull Request, permitindo revisão antes do merge quando houver mais de um colaborador ativo.
5. Atualizar `CONTEXT.md` se a decisão alterar o estado atual do projeto.

---

## 8. Versionamento

* O projeto segue **Semantic Versioning** (`MAJOR.MINOR.PATCH`) para releases da plataforma.
* A versão atual do produto é rastreada em `CHANGELOG.md`.
* Milestones do GitHub seguem as versões executivas definidas em `docs/ROADMAP.md` (v0.1 Foundation, v0.2 Core, ...).

---

## 9. Padrão de Commits

Este projeto segue **Conventional Commits**:

```text
<tipo>(<escopo opcional>): <descrição curta>

[corpo opcional]

[rodapé opcional]
```

Tipos permitidos: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `ci`, `build`, `revert`.

Exemplo real deste projeto:

```text
docs(foundation): establish governance, AI collaboration protocol and project documentation
```

Detalhes completos em `CONTRIBUTING.md`.

---

## 10. Padrão de Pull Requests

* Todo PR deve preencher o template em `.github/pull_request_template.md`.
* Todo PR deve indicar: resumo da mudança, arquivos alterados, testes realizados, documentação atualizada, riscos e checklist de verificação.
* Mudanças que envolvam decisão arquitetural devem referenciar o ADR correspondente no corpo do PR.
* Merge direto na `main` é aceitável apenas na fase de desenvolvimento individual (`docs/Documento-05-Plano-Repositorio-GitHub-Vena-IA-v1.0.md`, Seção 4); proteção de branch será ativada quando o CI estiver operacional.
