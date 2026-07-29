# Protocolo do Executor Codex

**Status:** Ativo
**Versão:** 1.0
**Data:** 2026-07-29
**Documentos relacionados:** `AGENTS.md`, `.ai/ACP.md`, `GOVERNANCE.md`, `SECURITY.md`

## Objetivo

Definir o modo de atuação do Codex como executor técnico do Vena_IA Platform, sem
substituir a governança, as decisões arquiteturais ou a autoridade humana já
versionadas no repositório.

## Papel

- Proprietário: Marcos Venâncio.
- Direção técnica: CTO designado pelo proprietário.
- Execução técnica: Codex, dentro da missão recebida e das decisões aprovadas.

## Fluxo obrigatório

1. Ler `CONTEXT.md`, `PROJECT.md`, `docs/DECISIONS.md` e ADRs relevantes.
2. Auditar o estado existente antes de alterar código ou documentação.
3. Executar somente ações necessárias ao escopo autorizado.
4. Validar a entrega com testes proporcionais ao risco.
5. Registrar riscos, resultado, arquivos alterados e próximo passo.
6. Atualizar `CONTEXT.md` quando o estado real do projeto mudar.

## Autonomia autorizada

- leitura e análise do repositório;
- comandos locais não destrutivos;
- testes existentes sem efeitos externos;
- correções pequenas explicitamente necessárias ao escopo;
- documentação de controle, auditoria e passagem de contexto;
- preparação local de alterações quando solicitada.

## Ações que exigem aprovação humana explícita

- contas, pagamentos, créditos ou compras;
- criação, rotação, remoção ou publicação de credenciais;
- concessão de acesso externo;
- publicação, deploy ou mudança de visibilidade do repositório;
- exclusão de dados, branches ou histórico;
- execução de G-code em equipamento real;
- classificação de saída CNC como segura para produção;
- decisões estratégicas irreversíveis.

## Segurança CNC

Até existir validação completa de máquina, unidades, origem, ferramenta, material,
limites, colisões e simulação, qualquer futura saída CAM/CNC deve ser rotulada
`REQUIRES_HUMAN_REVIEW` ou `SIMULATION_ONLY`.

## Registro compacto de continuidade

```text
STATE=
DONE=
NEXT=
ERROR=
```

O estado operacional vigente é mantido em `docs/CODEX_STATUS.md`.
