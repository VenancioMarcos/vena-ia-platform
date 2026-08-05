# Runbook — Controlled Incident Drill

**Contract:** `vena-ia.incident-drill/v1`
**Data:** doubles descartáveis e dados sintéticos somente
**External transport:** nenhum

## Cenários

O drill automatizado cobre indisponibilidade e recuperação de PostgreSQL, Redis e
MinIO; provedor de IA indisponível; readiness degradado; rate limit; falhas
repetidas de autenticação; processamento, backup e restore falhos; e erro interno
inesperado. Para cada cenário ele verifica request/correlation ID, evento
estruturado, métrica, alerta local/no-op, span, estado seguro e recuperação. O
campo de auditoria é preenchido somente quando o fluxo possui evento persistente.

## Execução

Use um diretório novo, protegido e fora do repositório:

```bash
python -m scripts.incident_drill \
  --output-directory /secure/vena-ia-incident-evidence/run-001 \
  --application-version 1.5.0 \
  --environment controlled-test
```

Saída `0` indica onze cenários aprovados. Erro de contrato, path, overwrite,
symlink, escrita ou validação encerra com código não zero. Verifique o JSON contra
o `.sha256` antes de usar a evidência. Nunca copie logs brutos para o bundle.

## Contrato e segurança

Campos permitidos: schema/versão/ambiente, tempos e duração, cenário,
request/correlation ID, dependência, estado esperado/observado, código de alerta,
métrica, evento de auditoria aplicável, resultado e limitações. São proibidos
tokens, cookies, senhas, chaves, URLs com credencial, IDs de usuário/projeto/
documento, conteúdo, prompts, respostas, embeddings e stack traces.

O gerador normaliza paths, exige artefato fora do repositório, rejeita nomes com
traversal, componentes symlink e overwrite, escreve por temporários e produz
SHA-256. Falha parcial remove somente os arquivos criados pela própria execução.
Os padrões de nome também estão no `.gitignore` como defesa adicional.

## Retenção e limitações

O bundle é evidência pontual local e deve seguir a retenção do processo de
incidente aprovado; ele não é trilha sensível nem backend de métricas. Auditoria
sensível permanece no PostgreSQL por 90 dias por padrão. Métricas/spans reiniciam
com o processo e não agregam réplicas. Nenhum resultado é SLO, SLA, capacidade de
produção ou autorização de piloto/deploy.

## Calibração reproduzível local

Em 2026-08-04, 100 execuções sintéticas dos onze cenários totalizaram 151,973 ms:
média 1,520 ms, p50 1,335 ms, p95 2,206 ms e p99 2,577 ms no workspace Windows
local. O bundle verificado teve 11 cenários e checksum SHA-256 válido. A amostra é
somente evidência do custo do runner sintético e não mede infraestrutura real.

O Backend CI run `30967191649` validou o pacote em Python 3.13 com PostgreSQL/
pgvector, Redis e MinIO descartáveis: 216 testes de API e 52 operacionais passaram,
incluindo os seis testes do contrato de drill. O ciclo Alembic chegou ao head
`a63d2f8c1b04`, realizou downgrade e retornou ao head. O probe criptografado de
1 objeto/27 bytes mediu backup 0,426 s, restore 0,418 s e RPO técnico 1,247 s;
esses números também não constituem SLO ou capacidade de produção.
