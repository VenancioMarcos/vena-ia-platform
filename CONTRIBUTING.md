# CONTRIBUTING.md — Guia de Contribuição

**Status:** Documento Oficial
**Versão:** 1.0
**Documento relacionado:** `GOVERNANCE.md`, `AGENTS.md`

---

## 1. Antes de Contribuir

Leia, nesta ordem:

1. `CONTEXT.md` — estado atual do projeto.
2. `PROJECT.md` — documento mestre.
3. `docs/DECISIONS.md` e `docs/adr/` — decisões já tomadas.
4. `GOVERNANCE.md` — regras do projeto.

Se você é um agente de IA, leia também `AGENTS.md` e `.ai/ACP.md`.

---

## 2. Branches

* `main` — branch de produção/estável. Protegida quando o CI estiver operacional.
* `feature/<escopo-curto>` — para novas funcionalidades (ex. `feature/upload-arquivos`).
* `fix/<escopo-curto>` — para correções (ex. `fix/cors-api`).
* `docs/<escopo-curto>` — para mudanças exclusivamente documentais (ex. `docs/foundation`).

Durante a fase de desenvolvimento individual, commits diretos em `main` são aceitáveis. Ao ganhar colaboradores, todo trabalho passa a exigir Pull Request.

---

## 3. Conventional Commits

Formato obrigatório:

```text
<tipo>(<escopo opcional>): <descrição curta em minúsculas>
```

Tipos: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `ci`, `build`, `revert`.

Exemplos:

```text
feat(api): add health check endpoint
fix(web): correct dashboard layout on mobile
docs(foundation): establish governance, AI collaboration protocol and project documentation
chore: add initial monorepo structure
```

---

## 4. Code Review

Todo Pull Request deve ser revisado quanto a:

* Consistência com `ARCHITECTURE.md` e ADRs vigentes.
* Presença de testes para lógica de negócio nova (`PROJECT.md`, Seção 16).
* Documentação atualizada, se a mudança afetar comportamento documentado.
* Ausência de segredos ou dados sensíveis (`SECURITY.md`).

---

## 5. Checklist de Pull Request

Use o template em `.github/pull_request_template.md`. No mínimo, todo PR deve responder:

* [ ] O que muda e por quê?
* [ ] Há testes cobrindo a mudança (quando aplicável)?
* [ ] A documentação correspondente foi atualizada?
* [ ] Existe ADR ou entrada em `DECISIONS.md` necessária para esta mudança?
* [ ] Nenhum segredo foi versionado?

---

## 6. Documentação Obrigatória por Tipo de Mudança

| Tipo de mudança | Documentação exigida |
|---|---|
| Nova decisão arquitetural | ADR em `docs/adr/` |
| Decisão operacional menor | Entrada em `docs/DECISIONS.md` |
| Nova funcionalidade | Objetivo, escopo, testes, critérios de aceitação (`PROJECT.md`, Seção 19) |
| Mudança de estado do projeto | Atualização de `CONTEXT.md` |
| Mudança de processo de colaboração entre IAs | Atualização de `.ai/ACP.md` ou `AGENTS.md` |

---

## 7. Fluxo Git Recomendado

```bash
git checkout -b feature/minha-mudanca
# ... trabalho ...
git add -A
git commit -m "feat(escopo): descrição da mudança"
git push -u origin feature/minha-mudanca
# abrir Pull Request para main
```

---

## 8. Contribuições de Agentes de IA

Agentes de IA seguem este mesmo guia, além das regras adicionais de `AGENTS.md` e `.ai/ACP.md`. Em caso de conflito de instrução entre uma missão recebida e este documento, este documento prevalece, salvo decisão humana explícita em contrário.
