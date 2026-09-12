# CTO-CODEX-AUTO-049 — Ciclo visual de despacho assíncrono

Integra o serviço cliente de despacho ao card STEP e à rota `/cam/turning`, com
estados explícitos, feedback acessível, polling limitado e cancelamento via
`AbortController`. O processamento permanece restrito à análise vetorial e à
visualização 2D; não existem controles de emissão NC ou operação física.

## Validação

- 59 testes web aprovados, incluindo envio, polling, falha, timeout e cancelamento.
- TypeScript e Next lint aprovados com zero erros e zero avisos.
- 727 testes Python aprovados e 9 ignorados.
- Ruff e `git diff --check` aprovados.

Parecer do CTO: **APROVADO (A)** no commit local `34e7c22`.
