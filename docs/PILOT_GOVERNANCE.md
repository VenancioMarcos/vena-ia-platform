# Governança de preparação para piloto controlado

**Status:** Package 1 v1.9 — somente contexto sintético

## Limite

Esta fundação organiza evidência local e sintética para revisão humana. Ela não cria
piloto real, cliente, ambiente externo, compromisso SLO, deploy ou aprovação de CNC.
`READY_FOR_SYNTHETIC_REHEARSAL` significa apenas que os itens mínimos estão prontos
para análise humana.

## Fluxo controlado

1. Usuário autenticado cria uma Organization e recebe `OWNER` atomicamente.
2. OWNER ou ADMIN cria Team; MEMBER sempre é limitado a uma Team.
3. OWNER cria ADMIN/MEMBER; ADMIN cria somente MEMBER. Ninguém informa OWNER inicial
   ou eleva o próprio papel pelo request.
4. Um membro autorizado cria Pilot Context com owner derivado da sessão.
5. O checklist registra evidências sintéticas de identidade, autorização, recovery,
   observabilidade, capacidade, privacidade, incidentes e segurança Engineering/CNC.
6. Somente checklist completo resulta em `READY_FOR_HUMAN_REVIEW`; revisão humana
   continua obrigatória antes do estado sintético final.

## Privacidade

Somente IDs técnicos, nomes operacionais mínimos, papéis/estados fechados e
referências sintéticas de evidência são persistidos. Não cadastrar empresas,
clientes, emails externos, documentos, CADs, máquinas ou credenciais reais. O
checklist não declara conformidade jurídica ou LGPD.

## Segurança

- `TOKEN + DATABASE = AUTHORITY`; corpo e headers não são autoridade.
- Cross-organization/cross-team falha fechado e não revela existência.
- Membership revogada deixa de autorizar na consulta seguinte ao banco.
- Ownership não pode ser transferido neste Package.
- Nenhuma saída inclui CAM, toolpath, G-code, M-code ou comando de máquina.
