# ADR-0017 — Auditoria persistente e versão de autenticação

**Status:** Aprovada
**Data:** 2026-08-02
**Decisão relacionada:** `DEC-017`

## Contexto

Contas legadas podem não ter senha utilizável, operações sensíveis precisam ser
auditáveis e tokens anteriores devem deixar de funcionar após uma definição
administrativa de credencial.

## Decisão

Adicionar `users.auth_version`, incluí-la no JWT com compatibilidade para tokens
anteriores (`0`) e compará-la com o usuário persistido. Incrementar a versão ao
definir a primeira credencial legada. Persistir eventos de segurança redigidos
em `security_audit_events`, com acesso administrativo limitado e ordenado.

## Consequências

Credenciais legadas podem ser ativadas sem rota pública, alteração de papel ou
exposição de segredo. A invalidação por versão funciona entre réplicas que usam
o mesmo banco. A trilha não substitui logging, métricas ou tracing e sua limpeza
continua uma operação controlada conforme a retenção configurada.
