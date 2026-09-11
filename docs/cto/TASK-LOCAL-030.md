# TASK-LOCAL-030 — Página de demonstração local

## Objetivo

Após aceite029 em49a8320, integrar /cam/turning com título e aviso exatos do CTO.

## Escopo

Página Next.js monta o contêiner029, layout centrado/responsivo. Sem API/fetch,
backend/manifests. Rota local de demonstração, sem autenticação adicional; não
é barreira de segurança nem autorização de publicação. Fixtures são sintéticas.

## Arquivos Criados

- apps/web/app/cam/turning/page.tsx
- apps/web/tests/turning-page.test.ts
- Este registro.

## Arquivos Modificados

CONTEXT, continuidade CTO e ADR-0037.

## Testes Realizados

38 testes web PASS,0 failed/0 skipped em734.3181ms. Ruff PASS;lint exit0 apenas
WEB-LINT-001. Python658 passed,2 skipped,0 failed em354.71s;tsc final e diff PASS.
next-env.d.ts restaurado byte a byte após execução das ferramentas Next.
Reprodução conforme029 incluindo turning-page.test.ts/.js e temp/local030-web-tests.

Prévia Next.js local127.0.0.1:3107, GET200. Navegador confirmou cenário inicial
SUCCESS_SYNTHETIC (8 passadas/32 movimentos), mudança para reconstrução falha
sem SVG/metadados indisponíveis, e violação com SVG/motivo DECLARED_ZONE_INTERFERENCE.
Screenshot desktop conferido: título,aviso,metadados e trajetórias legíveis.
Inicialização/compilação demoradas exigiram recuperar aba após timeout, sem
alterar implementação. Servidor temporário e aba de teste encerrados após QA.
Não realizada varredura completa de acessibilidade ou viewports móveis.
Node24.19.0 versus engines22.20.x;Python3.14.6 experimental;sem CI remoto.

## Critérios de Aceitação

Título,disclaimer,container e SVG presentes em SSR; baseline preservado.

## Próximos Passos

Validações concluídas;commit local,VTP ao CTO e aguardar próxima ordem real.
G9 pendente;autoridade física false;sem Git de rede/publicação.
