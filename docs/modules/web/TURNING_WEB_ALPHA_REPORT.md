# Dossiê do módulo web de torneamento 2D

Marco documental: v3.2.0-turning-web-alpha. Estado: STANDBY_WEB_BASELINE_CONSOLIDATED.
Baseline funcional: 103dd0ec96ca809882d279885790781cdfa86caf (TASK-LOCAL-031).
Data: 2026-09-11. Não é tag, release, deploy ou alteração da versão runtime/API3.1.0.

## Arquitetura e inventário

| Camada | Arquivo sob apps/web | Responsabilidade |
| --- | --- | --- |
| Contrato | lib/turning-contracts.ts | Espelho readonly de synthetic-turning/v3, sete estados discriminados e nulos explícitos |
| Projeção | lib/rz-projection.ts | Bounds de endpoints e projeção uniforme de raio R/axial Z; cores por movimento |
| SVG | components/cam/TurningProfile2D.tsx | Renderização pura de plano, eixos direcionais, fallback neutro e texto acessível |
| Estado | components/cam/TurningViewerContainer.tsx | Seletor de três fixtures locais, metadados, motivos, flags e plano quantizado |
| Página | app/cam/turning/page.tsx | Título, aviso de uso sintético e montagem do contêiner |

O fluxo usa fixtures geradas a partir de E2E Python; não chama API nem recebe
arquivos externos. Falha de reconstrução deixa o plano quantizado ausente e não
substitui silenciosamente pelo nominal. Escala R:Z uniforme; canvas640x400 reduz
proporcionalmente. R representa raio, não diâmetro; eixos indicam direção e não
origem. Cores distinguem movimentos e não aprovação. Tipos não validam JSON
externo, readonly não congela objetos e hashes não são verificados criptograficamente
pelo visualizador. Bounds são de endpoints, não certificação geométrica completa.

## Evidência e conformidade

41 testes web node:test:14 contratos/fixtures,15 projeção,5 SVG SSR,3 contêiner
SSR,1 página SSR e3 cleanup. Reexecução032:41 passed/0 failed/0 skipped em2925.277ms.
Os JS da compilação031 foram reutilizados, pois nenhum código mudou desde103dd0e.
Typecheck PASS;lint exit0 ZERO warnings/errors;Ruff/diff PASS.
Python658 passed,2 skipped (Redis opcional),0 failed em195.53s. Ver TASK-LOCAL-032.md.
Cleanup executa o corpo real do efeito em harness controlado; não monta React nem
simula HTTP. Não cobre jobs criados por operações pendentes somente após cleanup.

QA031:375x667,390x844,768x1024, cada tamanho com os três cenários;sem overflow
horizontal. SVG presente no sucesso/violação e ausente na falha, badges legíveis.
Proporção métrica preservada. Não houve nova sessão visual em032, somente documentos.
Reprodução da suíte descrita em TASK-LOCAL-031.md; fonte dos testes em tests/.
Ambiente: Node24.19.0 versus engines22.20.x;Python3.14.6 experimental.
Testes locais não equivalem a CI remoto, auditoria completa ou validação em máquina.

## Limites de segurança

| Controle | Estado |
| --- | --- |
| Classificação | NON_PRODUCTION, dados sintéticos/sandbox |
| PHYSICAL_USE_AUTHORIZED | FALSE |
| G9 | PENDING_AUTHORITATIVE_REVIEW |
| NO_HUMAN_REVIEW_BYPASS | TRUE |
| MACHINE_SEND / DNC / NC_TRANSFER / CYCLE_START | FALSE |
| emission_status | CONTROLLER_PROFILE_UNRESOLVED |
| NC de torneamento / envio a máquina | Ausentes nesta frente |
| API nova / backend alterado / dependências novas | Nenhum |
| Git de rede / merge / tag / publicação / deploy | Não realizados |

A rota não introduz barreira de autenticação: "interna" descreve seu propósito
local e não controle de acesso. Este marco é documental e não autoriza uso físico,
produção ou sincronização remota. A sincronização depende de ordem autorizada.

## Rastreabilidade

AUTO023 contratos/fixtures;AUTO025 testes;AUTO026/LOCAL027 projeção;LOCAL028 SVG;
LOCAL029 seletor;LOCAL030 página;LOCAL031 lint/mobile;LOCAL032 consolidação.
Consultar registros docs/cto e ADR-0037. Congelamento significa referência estável
no commit local, não proteção imutável da branch. Nenhum bundle novo foi criado.
