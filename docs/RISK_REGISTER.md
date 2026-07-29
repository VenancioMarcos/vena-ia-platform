# Registro de Riscos

**Data da revisão:** 2026-07-29

| ID | Severidade | Risco e evidência | Mitigação recomendada | Estado |
|---|---|---|---|---|
| R-001 | CRÍTICO | Não existe autenticação real. O identificador do usuário é aceito pelo header `X-User-ID`, que pode ser falsificado. | Implementar autenticação JWT/sessão, identidade verificada e autorização centralizada antes de exposição externa. | ABERTO |
| R-002 | CRÍTICO | `POST /users` aceita o campo `role`; um cliente pode criar usuário com papel `admin` e usar o ID no header para acessar o catálogo administrativo. | Remover `role` da criação pública, definir papel no servidor e restringir promoção a fluxo administrativo autenticado. | ABERTO |
| R-003 | ALTO | Rotas de usuários, projetos, metadados de arquivos e mensagens não exigem autenticação nem verificam proprietário. | Aplicar autenticação e autorização por recurso em todos os módulos. | ABERTO |
| R-004 | ALTO | Upload valida formato sintático do MIME e tamanho, mas não possui allowlist de extensões/MIME nem inspeção do conteúdo. | Definir tipos permitidos, validar assinatura do arquivo, quarentena e varredura antes de processamento. | ABERTO |
| R-005 | ALTO | O MVP não possui processamento documental, RAG ou vínculo automático entre respostas de IA e histórico do projeto. | Implementar pipeline seguro de extração, indexação e recuperação antes de declarar base de conhecimento pronta. | ABERTO |
| R-006 | MÉDIO | O frontend apresenta versões e estados antigos (`v0.1`/`v0.2`) enquanto backend e contexto estão em `v0.4.0`. | Atualizar textos e estados a partir de uma fonte única de versão. | ABERTO |
| R-007 | MÉDIO | Não há lockfile frontend; o CI usa `npm install`, reduzindo reprodutibilidade. Dependências locais também estão ausentes. | Gerar e versionar lockfile aprovado; migrar CI para instalação congelada. | ABERTO |
| R-008 | MÉDIO | O ambiente local auditado usa Python 3.14.6, enquanto o projeto e o CI exigem Python 3.13. | Validar também em Python 3.13 e manter matriz explícita de versões suportadas. | ABERTO |
| R-009 | MÉDIO | `minio/minio:latest` não está fixado por versão ou digest. | Fixar imagem validada e estabelecer rotina de atualização. | ABERTO |
| R-010 | MÉDIO | Observabilidade é limitada a health check e mensagens de erro; não há métricas, tracing ou auditoria de acesso. | Adicionar logging estruturado, correlação e trilha de operações sensíveis. | ABERTO |
| R-011 | BAIXO | Existe `.env` local real, embora ignorado e sem segredo detectado na auditoria. | Manter ignorado, limitar permissões e revisar antes de qualquer empacotamento. | MONITORAR |
| R-012 | BAIXO | A suíte gera aviso de depreciação de `TestClient`/HTTPX. | Planejar atualização compatível antes que a dependência remova o comportamento. | ABERTO |

## Segurança de segredos

- `.env` está ignorado pelo Git e não aparece no histórico.
- Nenhum padrão conhecido de chave OpenAI, token GitHub, chave AWS ou chave privada
  foi encontrado nos arquivos rastreados nem no histórico Git local.
- `.env.example` contém somente placeholders; `OPENAI_API_KEY` está vazio.
- Nenhum arquivo de credencial, cookie, chave privada ou dado pessoal foi localizado.
- A verificação por padrões não substitui secret scanning dedicado no CI.

## Classificação CNC

CAD, CAM, CNC, geração de G-code e simulação estão ausentes ou apenas reservados
em documentação. Não existe saída CNC para validar. Qualquer implementação futura
permanece `REQUIRES_HUMAN_REVIEW` até aprovação de um processo completo de
validação e simulação.
