# services/rag

Pipeline de recuperação aumentada por geração.

Fluxo previsto:

```text
Documento
  ↓
Extração
  ↓
Fragmentação
  ↓
Embedding
  ↓
pgvector
  ↓
Busca
  ↓
Resposta IA
```

