# Registro de Riscos

**Data da revisão:** 2026-08-01

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
| R-021 | CRÍTICO | Estruturas CNC preliminares poderiam ser confundidas com saída liberada para máquina. | Não gerar G-code; marcar simulação/revisão humana e `executable_output=false`; proibir transmissão e produção. | MONITORAR v0.8 |
| R-022 | ALTO | Referências heurísticas podem ser separadas ou interpretadas incorretamente. | Preservar texto bruto, página, método e estado preliminar; exigir revisão humana. | MONITORAR v0.9 |
| R-023 | MÉDIO | Metadados bibliográficos podem estar incompletos ou incorretos. | Registrar origem; manter ausentes como nulos; não consultar ou inventar DOI/autores/título. | MONITORAR v0.9 |
| R-024 | ALTO | Sínteses podem alucinar ou extrapolar evidências recuperadas. | Grounding obrigatório no RAG, evidências por documento/página/chunk e revisão humana. | MONITORAR v0.9 |
| R-025 | ALTO | Artigos podem conter prompt injection. | Tratar chunks como dados não confiáveis, reforçar prompt do sistema e testar instruções maliciosas. | MONITORAR v0.9 |
| R-026 | ALTO | Saídas preliminares podem ser usadas como conclusão científica. | Estados explícitos de revisão e limitações em sínteses, DOE, ANOVA e relatórios. | MONITORAR v0.9 |
| R-027 | ALTO | Preparação ANOVA pode ser confundida com inferência validada. | Não calcular F, valor-p ou significância; expor somente resumo descritivo e checklist. | MONITORAR v0.9 |
| R-028 | CRÍTICO | Recursos científicos poderiam vazar entre projetos. | AuthorizationService em todos os recursos; identidade somente do JWT; acesso negado como 404. | MONITORAR v0.9 |
| R-029 | ALTO | Biblioteca preliminar pode ser apresentada como revisão sistemática. | Documentar exclusão de PRISMA, bases externas, meta-análise e publicação. | MONITORAR v0.9 |
| R-030 | ALTO | A API não possui rate limiting. | Aceito para código MVP local; exigir proxy/gateway e limites antes de exposição pública. | ACEITO v1.0 / BLOQUEIA PRODUÇÃO |
| R-031 | ALTO | Não há backup/restore automatizado para PostgreSQL e MinIO. | Aceito para ambiente local; definir e testar política antes de piloto com dados reais. | ACEITO v1.0 / BLOQUEIA PRODUÇÃO |
| R-032 | MÉDIO | Observabilidade limita-se a health, erros controlados e CI. | Adotar métricas/tracing antes de operação externa. | MONITORAR v1.0 |
| R-033 | ALTO | Chat/RAG depende de PostgreSQL, MinIO, pgvector e provedor de IA. | Falhar sem resposta falsa; v1.1 permite retry de processamento/indexação; documentar dependências. | MITIGADO PARCIALMENTE v1.1 / MONITORAR |
| R-035 | ALTO | Relatórios aceitavam evidência declarada sem verificar correspondência com o chunk persistido. | Validar documento, página, índice e trecho antes de persistir o relatório. | MITIGADO v1.1 |
| R-036 | MÉDIO | Requisições sem timeout, falhas silenciosas e dependência da listagem de relatórios podiam bloquear ou confundir o fluxo principal do frontend. | Cliente API único com timeout; erros de logout/chat visíveis; relatórios carregados sem impedir projeto, documentos e histórico. | MITIGADO v1.1 |
| R-034 | MÉDIO | Não há deploy, capacidade ou escalabilidade validados. | Release limita-se ao código e ambiente local; medir antes de piloto/deploy. | ACEITO v1.0 |
| R-006 | MÉDIO | O frontend apresentava textos históricos enquanto backend e roadmap avançavam. | Textos operacionais foram atualizados e as versões de API/frontend unificadas em 1.0.0. | MITIGADO v1.0 |
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
