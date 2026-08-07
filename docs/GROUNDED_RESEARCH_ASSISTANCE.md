# Grounded Research Assistance v1

`vena-ia.grounded-research-assistance/v1` é a menor fronteira pública comum entre
Documents/RAG, Research e assistência especializada. Ela é aditiva: endpoints e
payloads Research existentes permanecem compatíveis.

Cada citation preserva `document_id`, página, `chunk_id`, evidence reference,
retrieval method, source quality e limitações. `fonte: IA` nunca é aceita. Sem chunk
autorizado recuperado, o status é `BLOCKED_MISSING_EVIDENCE` e nenhuma geração ocorre.

Excerpts são `UNTRUSTED_EVIDENCE`. Conteúdo que tente ignorar regras, revelar prompt/
segredos, liberar produção, gerar CNC ou alterar resultado determinístico continua
dado e gera warning; nunca é instrução.

## Limites científicos

* referência heurística não é referência bibliográfica validada;
* synthesis não é revisão sistemática nem conclusão científica;
* DOE permanece `DOE_PLAN_PRELIMINARY_REQUIRES_STATISTICAL_REVIEW`;
* ANOVA permanece descritiva, sem F-test, p-value ou inferência;
* Research Report permanece draft sob revisão do autor;
* causalidade, comprovação e validação científica autônoma são proibidas.

O bridge pode incluir snapshots allowlisted de DOE, ANOVA e report já autorizados,
mas não recalcula estatística nem persiste prompts/respostas. Auth/ownership existentes
protegem projeto/documento; cross-user/cross-org falha fechado como 404.

O Package 3 apresenta cada citation com documento, página, chunk, método, qualidade e
limitações, mantendo visíveis `DOE = PRELIMINARY` e `ANOVA = DESCRIPTIVE ONLY`.
Ausência de evidence permanece `BLOCKED_MISSING_EVIDENCE`, sem resposta substituta.
