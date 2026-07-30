# ADR-0011 — Parser STEP inicial sem kernel geométrico

**Status:** Aprovado  
**Data:** 2026-07-30  
**Responsável:** CTO / Backend Engineer / CAD Engineer

## Contexto

A v0.6 inicia análise CAD com arquivos STEP. OpenCascade/pythonOCC fornece
topologia e propriedades de massa robustas, mas introduz dependências nativas
pesadas, distribuição específica por plataforma e superfície operacional que
precisa de avaliação antes de entrar no monólito.

## Decisão

1. Aceitar somente STEP Part 21 com extensões `.step`/`.stp`, MIME permitido,
   assinatura `ISO-10303-21;`, limite de tamanho e isolamento existentes.
2. Introduzir `StepTextParser`, que lê apenas texto e nunca executa referências
   ou instruções contidas no arquivo.
3. Extrair cabeçalho, schema, contagem de entidades, tipos, pontos cartesianos,
   unidade declarada e envelope preliminar dos pontos.
4. Expor relatório técnico preliminar autenticado pelo domínio `cad`.
5. Declarar volume como indisponível até existir kernel geométrico validado.
6. Manter o parser atrás de serviço injetável para futura adoção de OpenCascade.

## Consequências

- As dimensões são o envelope dos `CARTESIAN_POINT` declarados, não uma garantia
  de bounding box topológica do sólido.
- Volume, área, validade B-Rep e tolerâncias geométricas não são inferidos.
- OpenCascade/pythonOCC permanece candidato para uma entrega posterior após
  validação de licença, imagens, segurança, desempenho e portabilidade.
