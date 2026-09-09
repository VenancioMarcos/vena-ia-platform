# CTO-CODEX-CAM-007 — Registro de execução

**Data:** 2026-09-09
**Estado:** CAM-007A concluída localmente com ressalvas de escopo sintético; validação PASS.
**Base:** d3785d3, CAM-006A aprovada AR por relatório, 485 passed/2 skipped.

## Objetivo

Fundar verificação independente de fronteiras do plano sintético de torneamento.

## Escopo e conflito documentado antes de implementar

A ordem CAM-007 pede colisão da haste com stock/ombro, mas a assinatura recebe
apenas plano, fixture e dimensões/ângulos de ferramenta. Não recebe geometria
ou material remanescente. Quadrante 1–9 não possui mapeamento universal no ADR.
Comprimento da haste menor que profundidade Z não prova colisão.

Proposta enviada diretamente ao CTO: CAM-007A, AABB local explícita relativamente
ao ponto ideal e zonas retangulares estáticas declaradas. Testar todos os tipos
de movimento (incluindo RETRACT) por interseção contínua segmento/retângulo
expandido pelos offsets, contato como violação e plano axial conservador.
Não inferir zonas de stock nem geometria de ferramenta a partir de metadados.
Resultado limitado a declared_boundaries_passed; is_verified=false,
collision_status=NOT_VALIDATED e autoridade false. Plano vazio NOT_EVALUATED.
Dados inválidos devem ser rejeitados por revalidação, sem relaxar R>=0.

## Arquivos criados

- apps/api/app/modules/engineering/turning_verifier.py: função independente de fronteiras.
- apps/api/tests/modules/engineering/test_turning_verifier.py: 29 casos.
- Este registro de entrega.

## Arquivos modificados

- turning_toolpath_schemas.py: fixture, envelope AABB, zonas e relatório.
- ADR-0037, DEC-047, CONTEXT, CHANGELOG e documentos CTO de continuidade.
- CTO-CODEX-CAM-006.md: confirmação do parecer da entrega anterior.

## Testes realizados

29 testes específicos passed em 5.56 s; Ruff PASS; mypy PASS em 191 fontes.
Suíte API completa: 514 passed (=485+29), 2 skipped em 130.95 s, zero falhas. Testes usam perfis
extraídos de STEP real canônico/escalonado e planos gerados por CAM-006A.
Cruzamentos com endpoints externos, tangência/nextafter, todos os tipos de movimento,
AABB com offsets negativos, ponto protegido apesar de envelope positivo, índices
entre operações, precedência, plano vazio, entradas forjadas, replay/JSON e imutabilidade.
Limites de recursos, NaN/Inf, zona degenerada e magnitude extrema também exercitados.

## Critérios de aceitação

Contrato corrigido confirmado pelo CTO. Implementação atende às fronteiras
sintéticas declaradas; regressão completa aprovada, commit/envio como próximos passos. Não declara
ausência de colisão física com entradas insuficientes.

## Próximos passos

Aguardar resposta real, registrar decisão técnica e implementar somente o escopo
local definido. Depois testar, commit local, enviar relatório, pedir/aguardar ordem.
NON_PRODUCTION; G9=PENDING_AUTHORITATIVE_REVIEW; PHYSICAL_USE_AUTHORIZED=false.
Sem NC, runtime, push, merge, tag ou deploy.

## Decisão recebida

Gemini confirmou integralmente a proposta e emitiu CAM-007A. AABB local
explícita, zonas estáticas, relatório sem autoridade. Commit solicitado:
feat(cam): implement synthetic boundary and exclusion zone verifier.

## Contrato implementado e limitações

Zonas são retângulos fechados R>=0, bounds ordenados, admitindo linhas/pontos.
Envelope não cortante é AABB de largura/comprimento positivos, offsets assinados
explicitamente declarados relativamente ao ponto ideal; não deriva de ferramenta
real. AABB não precisa conter o ponto ideal. Plano axial verifica AMBOS o ponto
e o envelope; diâmetro de fixação não limita a zona axial e é apenas metadado.

Interseção por intervalos paramétricos de segmento, t em [0,1], contra retângulo
[zone.r_min-tool.r_max, zone.r_max-tool.r_min] e análogo em Z. Implementação usa
Fraction sobre os floats finitos declarados, sem amostragem ou tolerância que
transforme tangência em PASS. Aritmética racional evita overflow das subtrações
finitas extremas; não atesta precisão da entrada ou metrologia do mundo real.

Todos os movimentos, incluindo RETRACT, recebem os mesmos testes. Retorna todos
os índices globais zero-based em ordem, únicos. Precedência CHUCK sobre ZONE.
R negativo é rejeitado pelo schema e revalidação profunda antes do laço, inclusive
model_copy forjado; CENTERLINE_VIOLATION fica reservado, não alcançável em entrada
válida. Não relaxar contrato para produzir esse status artificialmente.

is_verified/executable_output/physical_use_authorized são LiteralFalse;
collision_status=NOT_VALIDATED; limitations é tuple literal obrigatória de dois
valores. PASS apenas declared_boundaries_passed; plano vazio NOT_EVALUATED.
Relatório confere coerência status/índices, mas não constitui artefato assinado
ou Digital Thread. Não modifica o plano. Nenhum endpoint ou integração runtime.

Máximo 128 zonas e 200000 pares movimento/zona, além dos 10000 movimentos do
plano. Coleção deve ser tuple explícita com IDs únicos; entrada ausente/inválida
é rejeitada, incluindo em plano vazio. Sem stock/material remanescente, remoção,
compensação de pastilha, ferramenta/fixação reais, controlador resolvido ou NC.

## Validação final

Suíte 514 passed/2 skipped em 130.95 s; 29 específicos passed em 5.56 s.
Ruff PASS; mypy PASS em 191 fontes; git diff --cached --check PASS;
5 links relativos verificados, nenhum quebrado. Log local ignorado:
.pytest_cache/cam007a-pytest.log. Sem resumo de warnings.
Skips Redis real auth/jobs preservados. Python 3.14.6 local experimental;
nenhum novo CI remoto alegado. Nenhum código modificado após a suíte completa.

## Commit e envio

Commit f55534a27b0ad59e7a6a7f18c23c43ac28638b2b, 12 arquivos,
567 inserções/12 remoções. Árvore limpa após commit. Relatório enviado ao
Gemini CTO na conversa autorizada; solicitado parecer e próxima ordem.
Aguardando resposta real. Nenhum push/NC ou integração.

Parecer recebido: APROVADO TECNICAMENTE NO ESCOPO por relatório. CTO emitiu
CAM-008, posteriormente ajustada para CAM-008A. Ver CTO-CODEX-CAM-008.md.
