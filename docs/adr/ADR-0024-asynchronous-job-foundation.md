# ADR-0024 — Worker assíncrono dentro do Modular Monolith

**Status:** Aprovada
**Data:** 2026-08-05
**Decisão relacionada:** DEC-025
**Riscos relacionados:** R-016, R-017, R-033, R-038

## Contexto

A extração textual de PDFs era executada no ciclo HTTP. Documentos extensos,
interrupções de dependência e reinícios exigem estado durável, idempotência e
recuperação sem converter prematuramente o produto em microserviços.

## Decisão

Adotar o contrato `vena-ia.job/v1`, persistido no PostgreSQL, e uma fila Redis que
transporta somente identificadores e contexto de correlação. Um processo operacional
separado, iniciado por `python -m scripts.worker`, importa os mesmos módulos e usa o
mesmo banco, storage, regras e release da API. Portanto, continua sendo um Modular
Monolith e não estabelece API interna, ownership de dados ou deploy independente.

Claims usam lease atômico e heartbeat; jobs aplicam transições compare-and-set,
idempotência por proprietário/tipo/chave derivada, retry exponencial limitado,
timeout, cancelamento cooperativo e recuperação de lease abandonado. Somente tipos
allowlisted possuem handler. Conteúdo de documento, prompt, resposta, embedding,
credencial e código do usuário nunca integram a fila ou o registro de controle.

O Package 1 integra apenas `document.processing`, que extrai/chunka e executa a
indexação já existente. Os endpoints síncronos existentes
permanecem por compatibilidade, mas a interface passa a iniciar o fluxo assíncrono.
OCR não é adicionado: PDF sem texto falha explicitamente.

## Consequências

PostgreSQL e Redis tornam-se necessários para a durabilidade e coordenação do fluxo;
MinIO continua necessário ao handler. Métricas e tracing do worker continuam locais
e efêmeros, enquanto eventos de ciclo de vida são auditados no PostgreSQL. Timeout é
cooperativo: bibliotecas síncronas não são terminadas à força durante uma chamada;
o resultado é recusado ao fim do orçamento e o risco permanece documentado.

Busca vetorial, OCR, GPU, SaaS, microserviço, deploy e novos tipos de job permanecem
fora desta decisão.

## Complemento de resiliência — Package 2

O PostgreSQL permanece a fonte de verdade. Antes de consumir, o worker reconcilia
jobs não terminais e reconstrói no Redis somente identificadores/correlação. Um
`RUNNING` sem lease volta atomicamente a `QUEUED`, consumindo nova tentativa; um
lease válido nunca é tomado; limite esgotado termina em `JOB_RETRY_EXHAUSTED`.
Enqueue, recuperação e acknowledge são idempotentes e a recuperação Redis usa Lua
atômico para impedir dois recoverers de publicar o mesmo abandono.

O documento permanece `PROCESSING` durante extração, chunks, embeddings e
indexação, chegando a `READY` somente depois do efeito completo. Retry substitui
chunks e embeddings da mesma versão em vez de anexar efeitos. Renovação de lease e
cancelamento entre páginas reduzem janelas de abandono, mas timeout de chamada
síncrona continua cooperativo e não é apresentado como preemptivo.
