# RS274 Safe Subset v1

O pós-processador sintético v2.3 aceita exclusivamente um candidato de toolpath
verificado e gera o perfil `VENA_RS274_SAFE_SUBSET_V1`: `G21`, `G17`, `G90`, `G94`,
movimentos `G0`/`G1` lineares e `M30`.

O programa é classificado `CANDIDATE_FOR_VALIDATION`, tem manifest com hashes e
mantém `production_authority=false`, `human_review=REQUIRED` e
`executable_output=false`. Não pode ser enviado, baixado como NC de produção ou
associado a controlador real.

O parser independente valida a gramática e os modos sem reutilizar o gerador. Macros,
variáveis, subrotinas, probing, canned cycles, compensação, mutação de offset,
expressões, extensões de fornecedor, turning e multi-axis são rejeitados.
