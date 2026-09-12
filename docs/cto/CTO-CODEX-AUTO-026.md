# CTO-CODEX-AUTO-026 — Projeção planar RZ

## Objetivo

AUTO-025 aprovada pelo Gemini em 0a744a78. Implementar utilitários puros de
apresentação RZ, sem conexão a API, Canvas/DOM, backend ou emissor NC.

## Escopo

Bounding box inclui perfil e todos os endpoints dos planos fornecidos. R é raio,
Z é horizontal crescente; R crescente sobe na tela. Uma escala px/mm para ambos
os eixos, centralização e padding em pixels. Vazio usa janela unitária; ponto
isolado centralizado; linha usa sua extensão não nula. Dados não finitos, R
negativo, limites invertidos, viewport inválido ou overflow numérico geram RangeError.
Cores âmbar/ciano/magenta distinguem movimento, sem interpretação de comando NC.

## Arquivos Criados

- apps/web/lib/rz-projection.ts
- apps/web/tests/rz-projection.test.ts
- Este registro.

## Arquivos Modificados

Continuidade CTO/CONTEXT e incremento do ADR-0037 documentam apresentação apenas.

## Testes Realizados

Runner:25 passed,0 failed,0 skipped em177.0605ms. TypeScript completo PASS,
Ruff PASS, lint exit0 com apenas WEB-LINT-001. Regressão Python:658 passed,2 skipped,0 failed em124.69s. Diff PASS.
Comandos reproduzíveis a partir de apps/web (somente ferramentas instaladas):

```powershell
node node_modules/typescript/bin/tsc tests/turning-contracts.test.ts tests/rz-projection.test.ts --outDir ../../temp/auto026-web-tests --module commonjs --target ES2020 --moduleResolution node --esModuleInterop --strict --skipLibCheck --noEmitOnError --typeRoots node_modules/@types --types node
if ($LASTEXITCODE -eq 0) { node --test ../../temp/auto026-web-tests/tests/turning-contracts.test.js ../../temp/auto026-web-tests/tests/rz-projection.test.js }
```

Node24.19.0 instalado diverge de engines22.20.x; Python3.14.6 experimental.
Sem CI remoto. Projeção não recorta pontos fora dos limites e não valida segurança
geométrica/física. next-env.d.ts gerado pelo lint restaurado ao HEAD original.

## Critérios de Aceitação

Extremos do cilindro, escala1:1, inversão radial, perfil complexo, movimentos,
degeneração e erros cobertos. Sem alteração de contratos/backend/manifests.

## Próximos Passos

Validações concluídas. Commit local, relatar ao CTO e aguardar próxima instrução real.
G9 pendente, autoridade física e envio a máquina false; sem Git de rede/publicação.
