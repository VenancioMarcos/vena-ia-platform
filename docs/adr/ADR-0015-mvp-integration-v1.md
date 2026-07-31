# ADR-0015 — MVP Integration and Release v1.0

**Status:** Aprovado
**Data:** 2026-07-30

## Decisão

Consolidar o MVP em um fluxo integrado sem reimplementar os módulos publicados.
O frontend conecta sessão, projetos, PDF, processamento, indexação, chat RAG,
histórico e relatório. `ChatService` orquestra `KnowledgeService` e persiste:

* mensagem do usuário com status;
* resposta somente quando o provider retorna sucesso;
* evidências por documento, página, chunk, score e trecho;
* falha controlada sem resposta falsa.

`ResearchReport` é reutilizado como relatório técnico inicial. O E2E usa
dependências determinísticas, sem API paga, e comprova o caminho completo e o
isolamento entre dois usuários. A migration `e15a7c9d4f20` acrescenta autoria,
estado, evidências e erro às mensagens.

## Limites e riscos residuais

Não há deploy, rate limiting, recuperação de senha, revogação imediata de JWT,
OCR, backup automatizado ou observabilidade externa. O provedor real depende de
configuração. CAD/CAM/CNC/pesquisa preservam seus gates preliminares. Nenhuma
saída CNC executável foi criada.
