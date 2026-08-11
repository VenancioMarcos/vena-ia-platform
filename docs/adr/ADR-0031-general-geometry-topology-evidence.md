# ADR-0031 — General Geometry Topology Evidence

**Status:** Approved for implementation — TASK-V22-001

## Contexto

`geometry-analysis/v1` fornece propriedades globais e `geometry-features/v1` aplica
uma rule fechada. Nenhum deles é uma fonte geral, versionada e reproduzível de
topologia para evolução segura do planning.

## Decisão

Adicionar `vena-ia.geometry-topology-evidence/v1` como read model efêmero dentro do
módulo CAD. O builder reutiliza o shape carregado uma única vez pelo adapter OCCT e
expõe entidades, relações, métricas, classificações, unidades, transformação,
tolerâncias, provenance, ambiguity e limitations.

IDs estáveis derivam de descritor canônico e incluem a versão do kernel/algoritmo
como fronteira de identidade. Empates não são ocultos: recebem grupo de ambiguidade.
Unidade desconhecida e topologia inválida falham fechado sem lista de elementos.

## Alternativas rejeitadas

* ampliar somente a lista fixa de features: confunde cobertura com verdade geral;
* usar `HashCode`/endereço/índice incidental do OCCT: não é estável entre processos;
* criar segundo kernel ou microserviço: duplica parsing e fronteira operacional;
* inferir tolerance/manufacturing intent: transforma evidência em claim inseguro.

## Consequências

O endpoint CAD recebe um campo aditivo; contratos v1 existentes permanecem. Não há
persistência ou migration. Canonicalização é kernel-version-scoped e ambiguidades
continuam explícitas. Crash nativo/preempção permanecem risco residual R-039.

## Limites de segurança

Sem Package 2, toolpath, postprocessor, G/M-code, NC/DNC ou controle físico. Revisão
humana obrigatória; manufacturing tolerance não é inventada.
