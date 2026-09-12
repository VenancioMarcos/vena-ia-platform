# CTO-CODEX-AUTO-015 — Avaliador numérico de diâmetro

**Data:** 2026-09-09
**Estado:** implementação validada; pronta para commit local e parecer do CTO.
**Base:** 70e4d13; árvore limpa; 569 passed/2 skipped em 128.86 s na EXEC-014.

## Objetivo

Avaliar numericamente arredondamento de diâmetro, sem formatter/emissor NC.

## Escopo e política antes de implementar

Função pura evaluate_diameter_quantization(R, decimal_places=3), 1..6 casas,
float finito não negativo e inteiro estrito para precisão. X_ideal=2*R em float,
rejeitando overflow. Decimal.from_float representa exatamente esse valor binário;
ROUND_HALF_UP em contexto local independente, depois conversão de volta para
float finito e relatório X/2/desvio conforme contrato existente. O desempate
incide sobre valor binário recebido, não sobre decimal ideal digitado pelo usuário.

Rejeitar quantização de X positivo para zero e reconstrução positiva perdida;
não classificar ausência de avaliação como segurança. Sem fonte textual NC,
controlador selecionado, fronteiras ou Digital Thread. Resultado não conserva
zeros textuais nem especificação de máquina; default 3 é escolha sintética.

## Arquivos criados

turning_quantization.py, test_turning_quantization_evaluator.py e este registro.

## Arquivos modificados

ADR/DEC, CONTEXT/CHANGELOG e documentos CTO de continuidade.

## Testes realizados

23 testes específicos passed em 2.14 s: sinais, empate binário e vizinhos,
precisão/entradas estritas, overflow, perda para zero, extremos e contexto global
com precisão/limites/traps hostis preservado.
Suíte completa: 592 passed (=569+23), 2 skipped, 0 failed em 136.68 s.
Skips Redis real auth/jobs inalterados. Ruff PASS; mypy PASS em 193 fontes.
Python local 3.14.6 experimental, nenhum novo CI remoto.
Log local ignorado .pytest_cache/auto015-pytest.log.

## Critérios de aceitação

Cálculo determinístico no domínio declarado, sem alterar contexto global;
regressão completa >=569 testes anteriores; nenhuma emissão NC.

## Próximos passos

Commit local, enviar relatório com SHA real e pedir/aguardar ordem real.
G9=PENDING_AUTHORITATIVE_REVIEW; PHYSICAL_USE_AUTHORIZED=false;
CONTROLLER_PROFILE_UNRESOLVED; sem Git de rede/publicação.

## Limitação de representação

O retorno é float: conversão final pode arredondar o decimal quantizado para
binário; magnitudes extremas não representam uma grade decimal fina. Não há
promessa de tokens com casas/zeros, exatidão decimal, tolerância física ou
proveniência de programa. Precisão/política estão na função e nesta decisão,
não são novos campos do schema. Critérios do escopo sintético atendidos.

## Parecer e continuidade

Commit ebbe37e980c06e18bcf3a1efe75b34ef41905645, árvore limpa; relatório
enviado e aprovado pelo Gemini por relatório, sem inspeção independente.
Recebida AUTO-016: agregar quantização dos extremos de planos sintéticos.
