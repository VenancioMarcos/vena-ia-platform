# Guia rápido do usuário — Vena_IA Platform v1.0

1. Abra `http://localhost:3000/login`, selecione **Criar uma conta** e entre.
2. No dashboard, crie um projeto e abra-o pela lista.
3. Envie um PDF válido na área **Documentos PDF**.
4. Selecione **Processar e indexar** e aguarde o estado `READY`.
5. Faça uma pergunta na área **Conhecimento e histórico**.
6. Confira documento, página, chunk e score exibidos como fontes.
7. Reabra a página para confirmar que o histórico persistiu.
8. Gere um relatório do último resultado e reabra o rascunho.
9. Use **Sair** no dashboard para encerrar a sessão.

## Limitações obrigatórias

IA pode errar; confira sempre as fontes e submeta respostas/relatórios à revisão
humana. CAD e CAM são preliminares. CNC é estrutura não executável e não envia
dados para máquina. DOE exige revisão estatística. ANOVA v0.9 é somente preparação
descritiva. Relatórios são rascunhos. OCR, recuperação de senha, revogação imediata
de JWT, rate limiting, backup e deploy de produção não fazem parte desta release.
