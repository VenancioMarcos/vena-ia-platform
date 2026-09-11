# TASK-LOCAL-028 — Componente SVG puro

## Objetivo

Após aceite027 em82228f7, CTO emitiu028 completa: componente React declarativo
com plan/width/height/className, movimentos coloridos e fallback. Sem rede/efeitos.

## Escopo

TurningProfile2D usa projeção026, todos os endpoints e uma escala px/mm.
Eixos são referências de direção na borda, não falsa origem física. Título e
descrição acessíveis registram inspeção sintética. Planos vazios/pontuais,
coordenadas inválidas e viewport insuficiente exibem indicação neutra sem trajetórias.
Linhas com extensão válida permanecem visíveis. Sem rota ou integração no produto.

## Arquivos Criados

- apps/web/components/cam/TurningProfile2D.tsx
- apps/web/tests/turning-profile-component.test.ts
- Este registro.

## Arquivos Modificados

CONTEXT e continuidade CTO; ADR-0037 registra apresentação isolada.

## Testes Realizados

34 testes web PASS (5 novos SSR),0 failed/0 skipped em710.4763ms. TypeScript e
Ruff PASS;lint exit0, apenas WEB-LINT-001;diff PASS. Python658 passed,2 skipped,0 failed em135.88s.
SSR via ReactDOM instalado, sem navegador/teste visual interativo nesta etapa.
SSR valida estrutura, cores, contagens e fallback. Node24.19.0 (engines22.20.x),
Python3.14.6 experimental. next-env.d.ts restaurado byte a byte após lint.
Compilação inicial exigiu explicitar TurningToolpathPlan no teste para evitar
inferência excessiva das tuplas literais; sem cast inseguro ou mudança de fixture.

Reprodução em apps/web:

```powershell
node node_modules/typescript/bin/tsc tests/turning-contracts.test.ts tests/rz-projection.test.ts tests/turning-profile-component.test.ts --outDir ../../temp/local028-web-tests --module commonjs --target ES2020 --moduleResolution node --esModuleInterop --strict --skipLibCheck --noEmitOnError --typeRoots node_modules/@types --types node --jsx react-jsx
if ($LASTEXITCODE -eq 0) {
  $env:NODE_PATH=(Join-Path (Get-Location) 'node_modules')
  node --test ../../temp/local028-web-tests/tests/turning-contracts.test.js ../../temp/local028-web-tests/tests/rz-projection.test.js ../../temp/local028-web-tests/tests/turning-profile-component.test.js
}
```

## Critérios de Aceitação

Suíte web acumulada,tsc,lint apenas WEB-LINT-001,Python,Ruff,diff PASS.
Sem manifests/backend/packages/rede Git. Autoridade física false e G9 pendente.

## Próximos Passos

Validações concluídas; commit local, emitir VTP e aguardar próxima ordem real.
