# Registro de Riscos

**Data da revisão:** 2026-07-29

| ID | Severidade | Risco e evidência | Mitigação recomendada | Estado |
|---|---|---|---|---|
| R-001 | CRÍTICO | Identidade era aceita pelo header `X-User-ID`. | Substituído por JWT assinado, cookie HttpOnly/Bearer e identidade carregada do banco. | MITIGADO v0.4.1 |
| R-002 | CRÍTICO | Cadastro permitia autoatribuição de `admin`. | Cadastro rejeita `role`, força `member` e não expõe promoção pública. | MITIGADO v0.4.1 |
| R-003 | ALTO | Rotas não aplicavam autorização uniforme por proprietário. | Autorização centralizada protege usuários, projetos, arquivos, documentos, chats e IA. | MITIGADO v0.4.1 |
| R-004 | ALTO | Upload confiava em extensão/MIME controlados pelo cliente. | Allowlist exclusiva de PDF, MIME exato, `%PDF-`, tamanho e caminho interno seguro. | MITIGADO v0.4.1 |
| R-005 | ALTO | Respostas RAG poderiam não ter vínculo verificável com a origem documental. | Busca retorna documento, página, chunk e score; geração recebe apenas trechos recuperados e os trata como dados não confiáveis. | MITIGADO v0.5 |
| R-018 | MÉDIO | Embeddings dependem de provedor externo e dimensão fixa compatível com a coluna vetorial. | Configuração explícita, validação de contagem/dimensão e falha segura antes da persistência. | MONITORAR |
| R-019 | ALTO | Envelope calculado por pontos STEP pode divergir da bounding box topológica e volume não é confiável sem kernel geométrico. | Rotular análise como preliminar, não inferir volume e adotar OpenCascade somente após validação dedicada. | MONITORAR v0.6 |
| R-020 | ALTO | Parâmetros de corte genéricos podem ser inadequados para ferramenta, material, fixação ou máquina reais. | Rotular como preliminar, aplicar limites informados e exigir revisão humana; nunca enviar para máquina. | MONITORAR v0.7 |
| R-006 | MÉDIO | O frontend apresenta versões e estados antigos (`v0.1`/`v0.2`) enquanto backend e contexto estão em `v0.4.0`. | Atualizar textos e estados a partir de uma fonte única de versão. | ABERTO |
| R-007 | MÉDIO | Não havia lockfile frontend; o CI usava instalação não congelada. | `pnpm-lock.yaml` versionado e CI usa `pnpm install --frozen-lockfile`. | MITIGADO v0.4.1 |
| R-008 | MÉDIO | O ambiente local auditado usa Python 3.14.6, enquanto o projeto e o CI exigem Python 3.13. | Validar também em Python 3.13 e manter matriz explícita de versões suportadas. | ABERTO |
| R-009 | MÉDIO | `minio/minio:latest` não está fixado por versão ou digest. | Fixar imagem validada e estabelecer rotina de atualização. | ABERTO |
| R-010 | MÉDIO | Observabilidade é limitada a health check e mensagens de erro; não há métricas, tracing ou auditoria de acesso. | Adicionar logging estruturado, correlação e trilha de operações sensíveis. | ABERTO |
| R-011 | BAIXO | Existe `.env` local real, embora ignorado e sem segredo detectado na auditoria. | Manter ignorado, limitar permissões e revisar antes de qualquer empacotamento. | MONITORAR |
| R-012 | BAIXO | A suíte gera aviso de depreciação de `TestClient`/HTTPX. | Planejar atualização compatível antes que a dependência remova o comportamento. | ABERTO |
| R-013 | MÉDIO | JWT stateless não possui revogação imediata antes da expiração. | Adicionar rotação/revogação de sessão antes de produção multiusuário. | ABERTO |
| R-014 | MÉDIO | Usuários legados preservados pela migration não possuem hash de senha. | Criar fluxo administrativo auditável de definição ou recuperação de credencial. | ABERTO |
| R-015 | BAIXO | O contexto Docker do Web incluía artefatos locais (`node_modules` e `.next`), ampliando o build para centenas de MB. | `.dockerignore` dedicado reduz o contexto a arquivos-fonte e exclui ambientes, dependências, builds e logs locais. | MITIGADO v0.4.1 |
| R-016 | MÉDIO | A ingestão de PDF da fundação v0.5 ocorre de forma síncrona na requisição HTTP. | Introduzir fila, worker, timeout e retomada antes de processar documentos extensos em produção. | ABERTO |
| R-017 | MÉDIO | PDFs criptografados ou sem camada textual não geram chunks. | Manter falha explícita e adicionar OCR somente após avaliação de segurança, recursos e qualidade. | ABERTO |

## Segurança de segredos

- `.env` está ignorado pelo Git e não aparece no histórico.
- Nenhum padrão conhecido de chave OpenAI, token GitHub, chave AWS ou chave privada
  foi encontrado nos arquivos rastreados nem no histórico Git local.
- `.env.example` contém somente placeholders; `OPENAI_API_KEY` e
  `AUTH_SECRET_KEY` estão vazios.
- Nenhum arquivo de credencial, cookie, chave privada ou dado pessoal foi localizado.
- A verificação por padrões não substitui secret scanning dedicado no CI.

## Classificação CNC

CAD, CAM, CNC, geração de G-code e simulação estão ausentes ou apenas reservados
em documentação. Não existe saída CNC para validar. Qualquer implementação futura
permanece `REQUIRES_HUMAN_REVIEW` até aprovação de um processo completo de
validação e simulação.
