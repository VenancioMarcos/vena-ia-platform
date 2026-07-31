# ADR-0014 — Scientific Research Foundation

**Status:** Aprovado
**Data:** 2026-07-30

## Contexto

A v0.9 precisa organizar documentos científicos, produzir análises fundamentadas
e preparar DOE/ANOVA sem duplicar a infraestrutura documental/RAG nem apresentar
resultados preliminares como conclusões científicas.

## Decisão

Criar `apps/api/app/modules/research` dentro do monólito modular, com entidades,
schemas estritos, contrato/implementação de repository, serviços e API autenticada.

* `ResearchArticle` referencia um projeto e um `Document` existente e persiste
  somente metadados bibliográficos.
* `ResearchReference` preserva a referência bruta, página, método e campos
  heurísticos encontrados. Campos ausentes permanecem nulos.
* Sínteses reutilizam `KnowledgeService`; os trechos são dados não confiáveis,
  jamais instruções, e toda saída inclui evidências e
  `AI_ASSISTED_REQUIRES_HUMAN_REVIEW`.
* DOE persiste planos estruturados com
  `DOE_PLAN_PRELIMINARY_REQUIRES_STATISTICAL_REVIEW`.
* ANOVA limita-se a preparar observações, médias descritivas e checklist de
  pressupostos. Não calcula F, valor-p ou significância.
* Relatórios são sempre `DRAFT_REQUIRES_AUTHOR_REVIEW`.

## Consequências

A fundação reutiliza upload PDF, MinIO, extração, chunks, embeddings, RAG,
autenticação e autorização. Não há OCR, serviço externo de DOI, revisão
sistemática, meta-análise, submissão acadêmica, publicação ou decisão científica
automática. Extração heurística, sínteses e estatística preliminar podem conter
erros e exigem auditoria humana.
