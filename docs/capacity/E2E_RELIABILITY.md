# Regressão E2E e confiabilidade

O E2E determinístico existente cria dois usuários, autentica, cria projeto, envia
PDF sintético, extrai/chunka, indexa com provider local, faz pergunta fundamentada,
valida fonte, cria/reabre relatório, confirma isolamento cross-user e logout/401.

As suítes de jobs complementam a jornada com enqueue, claim, heartbeat, progresso,
retry, lease perdido, cancelamento, restart e recovery Redis/PostgreSQL. Drills de
incidente/resiliência cobrem lentidão, indisponibilidade e retorno das dependências.

O Controlled Capacity CI executa E2E e harness com PostgreSQL/pgvector e Redis reais;
o Backend CI continua validando também MinIO, backup/restore e round trip criptografado.
OpenAI real não é chamada e saída determinística nunca é apresentada como externa.

Limitação: duas APIs são instâncias lógicas no harness, não dois containers/deploys.
Dois workers exercitam claim compartilhado; a prova Redis real permanece nos testes
de integração do Backend CI. Isso é suficiente somente para o perfil versionado.
