# ADR-0010 — Fundação de ingestão documental para RAG

**Status:** Aprovado
**Data:** 2026-07-30
**Responsável:** CTO / Backend Engineer / AI-RAG Engineer

## Contexto

A v0.4.1 encerrou o Security Gate e liberou o início da v0.5. A fundação foi
entregue primeiro; a conclusão da versão exige indexação vetorial, recuperação
semântica e respostas fundamentadas sem reduzir os controles de autorização.

## Decisão

1. Manter a ingestão no domínio `documents` do monólito modular.
2. Extrair texto de PDFs permitidos com `pypdf`, rejeitando arquivos inválidos,
   criptografados ou sem texto extraível.
3. Fragmentar cada página separadamente com tamanho e sobreposição configuráveis.
4. Persistir chunks em `document_chunks`, com rastreabilidade para documento,
   página, índice global e offsets no texto extraído.
5. Reutilizar os estados `UPLOADED`, `PROCESSING`, `READY` e `FAILED`.
6. Expor contratos por `Protocol` para extractor, chunker, repository e service,
   permitindo substituir implementações sem acoplar o domínio.
7. Executar o processamento de forma síncrona nesta fundação.
8. Usar a AI Layer existente para embeddings e chat, sem acoplar o domínio a SDKs.
9. Persistir vetores de 1536 dimensões em pgvector e consultar similaridade por
   cosseno com índice HNSW.
10. Restringir respostas ao contexto recuperado, tratando trechos como dados não
    confiáveis e mantendo rastreabilidade por documento, página e chunk.

## Alternativas consideradas

- Criar imediatamente um microserviço `services/rag`: rejeitado por aumentar a
  complexidade operacional antes de existir recuperação semântica.
- Persistir embeddings na primeira entrega: adiado até a conclusão da fundação e
  incorporado na etapa final da v0.5.
- Adicionar OCR: rejeitado; PDFs sem camada textual são marcados como falha de
  processamento e exigirão uma entrega futura.

## Consequências

- A migration `b7f3c9d2e614` adiciona a tabela `document_chunks`.
- O processamento é idempotente no armazenamento de chunks por substituição,
  mas só inicia a partir do estado `UPLOADED`.
- PDFs extensos ainda são processados dentro da requisição HTTP; fila e workers
  permanecem risco conhecido para evolução posterior.
- A migration `c91e5a4f2d08` ativa pgvector e adiciona vetores aos chunks.
- Indexação e resposta continuam síncronas; filas permanecem evolução futura.
- A resposta não substitui validação humana e não recebe documentos como instruções.
