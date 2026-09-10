# Checklist de sincronização upstream — AUTO-022

Data: 2026-09-10. Preparação local; nenhum comando de rede abaixo foi executado.

## Estado e limites

Última visibilidade remota observada na DIAG-001: PUBLIC. Estado atual não
reconsultado. Recomenda-se PRIVADO antes do push, mediante decisão explícita do
proprietário. Tornar privado não desfaz exposição histórica. SECURITY.md continua
aplicável; o estado READY_FOR_UPSTREAM_SYNC significa prontidão documental local,
não autorização para publicar ou operar máquinas.

Origin local configurado: https://github.com/VenancioMarcos/vena-ia-platform.git.
Branch: codex/v3.1-first-controlled-test-path. PR #31 Draft é referência histórica,
não prova de estado remoto atual. API 3.1.0, contrato synthetic-turning/v3.

## Inventário do pacote congelado

19 commits em d798417c11b2ce4f751d81cf1252250ed20fd030..6eecfa6330709379e203d18b5dfc517516989a2f.
O commit desta checklist é adicional (20º) e não pertence ao bundle congelado.
Autores abaixo reproduzem metadados Git; não atestam identidade ou assinatura.

| SHA | Autor | Mensagem |
| --- | --- | --- |
| 052cb8ecf40b7ceb9cbc7346d9eadb579e488db6 | Vena_IA Work | fix(cad): accept whitespace in STEP units |
| 08569ff728b5b9ae2421e9cbcd2adfc47f649ecc | Vena_IA Work | fix(engineering): ensure strict compatibility check and harden gitignore |
| b86f51e1bb567e1973e3be19cec2599cd068d311 | Vena_IA Work | docs(cto): record fix approval and next specification mission |
| 9b5a83b4c199b4a2e51426adc371e700e98aaa8f | Vena_IA Work | docs(turning): propose architecture and contracts for 2-axis turning foundation |
| b5b04b7a1a000ad1dc6ff6c18fe980218989897d | Vena_IA Work | feat(turning): implement ADR-0037 turning schemas and axisymmetry validator |
| 57a0fcfd1fc2c11d376c726b78063e469fdbaac0 | Vena_IA Work | feat(cad): implement turning profile extractor and synthetic STEP fixtures |
| d3785d3bffa16189ff1e478957307988127ea0c4 | Vena_IA Work | feat(cam): implement synthetic 2D linear turning planner and schemas |
| f55534a27b0ad59e7a6a7f18c23c43ac28638b2b | Vena_IA Work | feat(cam): implement synthetic boundary and exclusion zone verifier |
| 5f50559c39d18fdf5c8c526080de9ad72bf1bd9a | Vena_IA Work | feat(engineering): implement deterministic synthetic turning E2E orchestrator |
| f3fb048b79bffd35782207e4de00cf620546003b | Vena_IA Work | docs(turning): document controller prerequisites and postprocessor gap matrix |
| dc75997938c4cdbbf0a264b1a8d5596c1b5b02b5 | Vena_IA Work | chore(release): consolidate v3.2.0-turning-synthetic-alpha baseline and documentation |
| 70e4d13e39e1063348cf8de148ff4aa6b9fd8b33 | Vena_IA Work | feat(cam): add numerical quantization check schema contracts |
| ebbe37e980c06e18bcf3a1efe75b34ef41905645 | Vena_IA Work | feat(cam): implement diameter quantization mathematical evaluator |
| 770ac7bc46228e93b657b6aa29de4be7c82d80ac | Vena_IA Work | feat(cam): implement toolpath plan diameter quantization evaluator |
| 6d4665ab1d2089ab2b00f5b440cc4cd10987cad6 | Vena_IA Work | feat(engineering): integrate plan diameter quantization into E2E orchestrator |
| c28405d7f2af941c46c5123ce0480386b7e08ab1 | Vena_IA Work | feat(cam): implement boundary reverification for quantized toolpath plans |
| 84492a5548d1911ccada07dc512d3e700e7075b2 | Vena_IA Work | feat(engineering): integrate robust quantized boundary verification into E2E pipeline |
| bcf3313fdb2e67db91ae18fb9c3002a4f5c5b399 | Vena_IA Work | chore(engineering): consolidate v3.2.0-turning-synthetic-alpha baseline documentation |
| 6eecfa6330709379e203d18b5dfc517516989a2f | Vena_IA Work | chore(governance): transition execution status to standby awaiting sync |

## Bundle e recuperação local

Arquivo ignorado: temp/turning_synthetic_alpha_v3.2.bundle.
SHA-256: b54987f3d6559ad8444ebab200d7e9e04fea31e9d764537eda5d29ed00ec29d8.
Criado com `git bundle create temp/turning_synthetic_alpha_v3.2.bundle d798417..HEAD`
quando HEAD era 6eecfa6; `git bundle verify` PASS.
Contém ref HEAD em 6eecfa6 e exige objeto-base d798417c11b2ce4f751d81cf1252250ed20fd030.
É incremental, não backup autossuficiente do repositório inteiro, de objetos LFS,
arquivos ignorados, banco de dados ou infraestrutura. Preservar também uma cópia
confiável do repositório-base. SHA-256 verifica bytes; não é assinatura.

Em cópia de recuperação que já contenha a base, verificar e importar em nova branch:

```powershell
git cat-file -e 'd798417c11b2ce4f751d81cf1252250ed20fd030^{commit}'
git bundle verify 'C:\CAMINHO-LOCAL\turning_synthetic_alpha_v3.2.bundle'
git fetch 'C:\CAMINHO-LOCAL\turning_synthetic_alpha_v3.2.bundle' 'HEAD:refs/heads/recovery/turning-alpha-6eecfa6'
git rev-parse refs/heads/recovery/turning-alpha-6eecfa6
```

Procedimento documental de recuperação; não executado nesta missão. Ajustar apenas
o caminho real e usar nome de branch de recuperação ainda inexistente. Conferir
SHA resultante contra 6eecfa6330709379e203d18b5dfc517516989a2f.

## Procedimento do proprietário para sincronização via SSH

1. Decidir a privacidade na interface do GitHub e confirmar colaboradores/acessos.
   Aprovar explicitamente a publicação da branch. Revisar a auditoria desta missão,
   inclusive suas limitações. Não inserir tokens ou chaves em comandos/documentos.
2. Usar credencial SSH já configurada pelo proprietário e host GitHub verificado.
   Interromper diante de alerta de host ou falha de autenticação; não desativar
   StrictHostKeyChecking nem criar credenciais como parte desta checklist.
3. No checkout local aprovado, executar as verificações abaixo. Exigir árvore
   limpa e branch correta. Registrar `git rev-parse HEAD` como SHA aprovado,
   incluindo o commit documental AUTO-022. Se houver novos commits, reauditar.

```powershell
git status --porcelain
git branch --show-current
git rev-parse HEAD
git diff --check d798417..HEAD
git log --oneline d798417..HEAD
```

4. Somente após autorização, consultar o remoto. Estes comandos usam URL SSH
   explícita e não alteram a configuração origin existente.

```powershell
git ls-remote 'git@github.com:VenancioMarcos/vena-ia-platform.git' 'refs/heads/main' 'refs/heads/codex/v3.1-first-controlled-test-path'
git fetch 'git@github.com:VenancioMarcos/vena-ia-platform.git' 'refs/heads/codex/v3.1-first-controlled-test-path'
git merge-base --is-ancestor FETCH_HEAD HEAD
```

Se a branch remota existir, exigir exit code 0 da verificação de ancestralidade.
Se não existir, o fetch específico falha: confirmar ausência no ls-remote antes de
criar a branch por push. Qualquer divergência inesperada exige nova revisão; não
usar force, reset, rebase ou merge automático para contornar rejeição.

5. Conferir destino e escopo no dry-run, depois enviar exatamente a branch revisada:

```powershell
git push --dry-run 'git@github.com:VenancioMarcos/vena-ia-platform.git' 'HEAD:refs/heads/codex/v3.1-first-controlled-test-path'
git push 'git@github.com:VenancioMarcos/vena-ia-platform.git' 'HEAD:refs/heads/codex/v3.1-first-controlled-test-path'
git ls-remote 'git@github.com:VenancioMarcos/vena-ia-platform.git' 'refs/heads/codex/v3.1-first-controlled-test-path'
```

Exigir sucesso de cada comando antes do seguinte. Conferir SHA remoto igual ao
HEAD aprovado. Não enviar tags, todas as branches, main ou o arquivo bundle.

## Pull Request

Com GitHub CLI já autenticada, consultar PR existente antes de criar duplicata:

```powershell
gh pr list --repo VenancioMarcos/vena-ia-platform --state open --head codex/v3.1-first-controlled-test-path --json number,url,isDraft,baseRefName,headRefName
```

Se PR #31 ainda existir na mesma branch/base, o push atualiza sua branch: revisar
sua descrição e manter Draft. Se não houver PR aberto correspondente, criar Draft
pela interface Compare & pull request, base main, compare
codex/v3.1-first-controlled-test-path. Conferir o diff completo contra main,
que pode incluir commits anteriores a d798417 e requer sua própria revisão.

Descrição deve informar cinco estágios sintéticos, contrato v3, evidências locais,
limites da auditoria e do bundle, ausência de NC de torno/homologação física,
658 passed/2 skipped e ausência de CI remoto novo nesta missão. Observar template
do repositório. Solicitar revisão e aguardar CI remoto; não fazer merge automático.

## Gates preservados

G9 pendente; PHYSICAL_USE_AUTHORIZED=false; machine-send/DNC/NC-transfer/cycle-start
false; CONTROLLER_PROFILE_UNRESOLVED. Preparação Git não autoriza manufatura.
Resultados da execução local em [registro AUTO-022](CTO-CODEX-AUTO-022.md).
