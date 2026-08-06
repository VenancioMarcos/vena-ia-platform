# E2E cross-instance e confiabilidade

O gate R1 usa HTTP real e alterna API A/API B. Cadastro/login, projeto, PDFs
sintéticos, jobs, polling, cancelamento, retry a partir de falha terminal injetada
no PostgreSQL descartável com transporte reconhecido, RAG determinístico, histórico,
logout/revogação, rate limit e isolamento cross-user atravessam as duas instâncias.

Worker A e Worker B são processos oficiais independentes. PostgreSQL é a fonte
durável; Redis transporta jobs, claims, leases e heartbeats próprios. Um worker é
interrompido durante claim real; o lease expira, o outro recupera o job, a fila
chega a zero e o worker interrompido é reiniciado. Idempotência cruzada deve retornar
o mesmo job e o gate falha com qualquer claim duplicado ou job não terminal.

MinIO armazena e entrega o PDF sintético ao worker. O container é pausado durante o
cenário: readiness deve falhar com segurança, o serviço retorna, o processamento
recupera e os objetos descartáveis são removidos. Nenhum documento real é usado.

O soak faz requisições autenticadas reais por pelo menos 30 segundos. Valores não
coletados, como memória por processo ou total de conexões PostgreSQL, são
`NOT_MEASURED`; nunca recebem zero inventado. O provider determinístico existe
somente no ambiente `capacity-ci` e não realiza rede externa.
