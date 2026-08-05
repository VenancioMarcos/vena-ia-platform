# ADR-0026 — Runtimes oficiais e imagens imutáveis

**Status:** Aprovada
**Data:** 2026-08-05
**Decisão relacionada:** DEC-027
**Riscos relacionados:** R-008, R-009, R-018, R-033, R-034, R-038

## Contexto

CI, Dockerfiles e ambiente local usavam versões por major/minor, imagens flutuantes
e `minio/minio:latest`. O frontend construía com npm apesar do lockfile pnpm. A
máquina local validava Python 3.14 enquanto o projeto declarava 3.13.

## Decisão

Adotar `runtime-policy.json` como manifesto executável. Python 3.13.11 é oficial;
3.14.6 permanece experimental após regressão local. Node 22.20.0 e pnpm 11.9.0 são
exatos. Todas as imagens externas usam tag explícita e digest imutável. Actions são
fixadas por commit. Dockerfiles usam build determinístico disponível, usuário não
privilegiado e processo de produção; API e worker continuam na mesma imagem e no
mesmo Modular Monolith.

Um policy check fail-closed alinha manifesto, CI, Dockerfiles, Compose, lockfile,
worker e rollback. Atualizações são trimestrais ou orientadas por advisory, sempre
em branch e com revisão humana.

## Consequências

R-008 e R-009 podem ser mitigados no escopo do Package 1. R-018 e R-033 continuam
monitorados; fixação não remove o provedor ou dependências externas. R-034 não muda
porque capacidade/escalabilidade não foram medidas. R-038 continua aberto porque
timeout de biblioteca síncrona permanece cooperativo.

Não há migration, mudança de banco/storage, deploy ou autoscaling. Ausência de lock
transitive Python e scanner dedicado permanece limitação explícita; não se afirma
build byte a byte nem ausência de vulnerabilidades.
