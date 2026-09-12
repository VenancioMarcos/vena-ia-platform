# Ordem CTO atual

**Missão:** CTO-CODEX-AUTO-042
**Estado:** ROTA_2_STEP_GEOMETRY_ADAPTER_IN_PROGRESS
**Data:** 2026-09-12
**Baseline inicial sincronizado:** 400d18af8235d7cac67965e28ba3eaa6bab43413 (merge do PR #31 na `main`).
**Emissor técnico:** Gemini, conversa https://gemini.google.com/app/62dacc664840eafe

## Escopo vigente

AUTO-042 adiciona uma inspeção textual limitada de metadados STEP ao fluxo local de
`/cam/turning`. A interpretação de B-Rep permanece somente uma detecção defensiva
de tokens: não cria geometria, perfil, G-code ou despacho. São proibidos push,
alteração em backend/pacotes, dependências de rede e qualquer mudança nos limites.

## Rotas futuras para deliberação do proprietário

1. Sincronização upstream: revisão de destino/privacidade e uso de credencial
   existente ou configuração explicitamente aprovada,seguida de push controlado.
   Não executada;abrange HEAD que vier a ser aprovado,não contagem antiga fixa.
2. Ingestão dinâmica CAD no frontend: especificar upload/drag-and-drop STEP e
   integração backend com autenticação,limites e validação. Não implementada.
3. Perfil CNC real: coletar requisitos de comando/cinemática e revisão técnica
   para futura especificação do pós-processador. Não abre G9 nem autoriza máquina.

O proprietário concluiu a Rota 1 em 2026-09-12. A Rota 2 inicia apenas a
validação cliente de arquivo e interface local; não há upload remoto, integração
backend, geração NC ou autorização física.

## Continuidade obrigatória

Após executar: documentar, enviar relatório técnico ao CTO Gemini, pedir a próxima
ordem e aguardar resposta real. Ao receber ordem técnica local compatível com a
autorização do proprietário, continuar. Não encerrar apenas por receber nova missão.
Confirmar no histórico da conversa se o envio já ocorreu antes de repetir mensagem.
Atualizar este arquivo, CONTEXT e histórico após cada parecer/ordem.

O merge do PR #31 foi autorizado e concluído pelo proprietário. AUTO-042 autoriza
somente commit local na branch da Rota 2; sem push, tag, release ou deploy.
NON_PRODUCTION;
G9=PENDING_AUTHORITATIVE_REVIEW; PHYSICAL_USE_AUTHORIZED=false. Contas, credenciais,
custos, acessos externos e operação CNC não são delegados ao AI-CTO.
