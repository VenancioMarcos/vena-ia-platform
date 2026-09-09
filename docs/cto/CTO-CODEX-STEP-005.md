# Registro de entrega — CTO-CODEX-STEP-005

## Objetivo

Extrair o perfil externo radial/Z de cilindros simples e escalonados e fornecer
quatro peças STEP sintéticas reproduzíveis, conforme ordem recebida do Gemini
após revisão AR de IMPL-004. Execução iniciada em 2026-09-08, continuada em 2026-09-09.

## Escopo

Extrator isolado, gerador/fixtures e testes. Sem integração ao pipeline, mudança
de fresamento, CAM, NC, push, merge, tag ou deploy. Datum explicitamente fornecido;
geometria permanece em raio. Nenhum contrato desta missão solicita saída programada,
portanto nenhuma conversão implícita ou opção de diâmetro será adicionada.

A checagem de eixos é pré-condição somente. Para o primeiro subconjunto cilíndrico,
obter intervalos axiais pelas superfícies analíticas, ordenar com continuidade C0,
reconstruir o sólido a partir desses intervalos e comparar diferenças booleanas
nos dois sentidos. Qualquer face residual ou erro bloqueia; igualdade de volume
sozinha não basta. Cones, interiores, múltiplos sólidos e perfis ambíguos são
rejeitados neste incremento. Isso delimita o algoritmo candidato do ADR, sem
declarar suporte a qualquer sólido de revolução ou autoridade física.

## Arquivos criados

- [profile_extractor.py](../../apps/api/app/modules/cad/profile_extractor.py)
- [generate_turning_step.py](../../apps/api/tests/fixtures/cad/generate_turning_step.py)
- [Corpus e README](../../apps/api/tests/fixtures/cad/turning/README.md): quatro STEP sintéticos.
- [test_turning_profile_extractor.py](../../apps/api/tests/modules/cad/test_turning_profile_extractor.py)
- Este registro.

## Arquivos modificados

Documentação ADR/decisões, CONTEXT, CHANGELOG, arquivos de continuidade CTO e
.gitattributes (LF apenas no corpus STEP novo).

## Testes realizados

Primeira suíte: 14 testes específicos PASS em 4.52 s, suíte completa
469 passed/2 skipped em 144.26 s. Ruff PASS; mypy PASS em 188 fontes.
Revisão final acrescentou os segmentos radiais frontal/traseiro aos perfis.
**Regressão final: 469 passed, 2 skipped, 0 failed em 127.00 s.**
Ruff/mypy novamente PASS; 16 links relativos e diff check PASS.
Log final ignorado: `.pytest_cache/step005-final-pytest.log`. Python local 3.14.6 experimental, sem CI remoto.
Skips Redis real de auth/jobs. Não existe novo teste físico.

A primeira checagem de reprodutibilidade falhou por horário AP203 fora do header.
Corrigida normalização dos metadados sintéticos de data/hora; regeneração passou
em comparação byte a byte. Dados geométricos não foram reescritos artificialmente.

Cobertura: leitura real AP203/AP214, perfil radial esperado/ordenado e replay,
chaveta/prisma, furo coaxial que passa no teste preliminar e falha no extrator,
datum incorreto/invertido, unidades desconhecidas, direção inválida, gaps/overlap
C0, cone excluído, datum rotacionado/transladado e vazio esférico rejeitado pela
reconstrução mesmo com classificação preliminar forçada a PASS.

## Critérios de aceitação

Cilindro D50/L100 e escalonado D30/L40+D60/L60 em Z negativo, perfil em raio
ordenado de Z=0 para trás; chaveta/prisma rejeitados; extrator não promove
AXISYMMETRY_PRELIMINARY_PASS a perfil sem verificação adicional.

## Próximos passos

Testes concluídos; criar commit local, enviar relatório ao CTO, solicitar e aguardar
parecer e próxima ordem. NON_PRODUCTION e G9 pendente; autoridade física false.

## Forma exata do perfil

Cilindro: (0,0), (25,0), (25,-100), (0,-100).
Escalonado: (0,0), (15,0), (15,-40), (30,-40), (30,-100), (0,-100).
Pares são (raio_mm,Z_mm), polyline aberta sem segmento de fechamento no eixo.
Faces radiais possuem Z repetido; a monotonicidade de Z é não estrita. Não é
trajetória de corte e não possui semântica de entrada/saída de ferramenta.

## Identidade do corpus

- `asymmetric_keyway.stp`: SHA-256 `468864cf469161d79e73310cae74ee85a26a23e2e8b6745fc79be320740977d9`.
- `cylinder_d50_l100.stp`: SHA-256 `6bbfbf28e9fb1fad43e2cfc80b2f6346a633086de4107ae3384ca77b8a6c0c7b`.
- `pure_prism.stp`: SHA-256 `83cd228c301bbcdc890519d83d499093d9be60d2320ea6f724e13971cea439ac`.
- `stepped_d30_d60.stp`: SHA-256 `0d190563ddc29cc1d7f69096ffd9d0a89cdca368a4fdf618a34be576dc237b62`.


## Normalização final de fixtures

O diff staged detectou whitespace final emitido pelo OCCT; o gerador agora o
remove sem alterar tokens geométricos. `.gitattributes` fixa LF apenas nestas
fixtures para preservar os bytes após checkout Windows. Após regeneração:
14 testes específicos novamente PASS em 3.31 s. A suíte de 469 passou sobre o
código de produto final antes desta normalização textual; sem código de produto
alterado depois. Ruff e diff staged rechecados antes do commit.
