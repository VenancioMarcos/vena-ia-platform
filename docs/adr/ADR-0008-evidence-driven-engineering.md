# ADR-0008 — Engenharia Orientada a Evidência

**Status:** Aprovado
**Data:** 2026-07-10
**Responsável:** Líder Técnico / Arquiteto de Software

---

## Contexto

O projeto combina desenvolvimento de software, pesquisa científica (potencialmente vinculada a pesquisa de mestrado) e decisões de engenharia mecânica (parâmetros de corte, estratégias de usinagem, geração de G-code) que têm consequências técnicas reais.

## Problema

Decisões técnicas tomadas "por plausibilidade" — inclusive por agentes de IA, que podem gerar respostas convincentes porém incorretas — representam risco tanto para a integridade do software quanto para a validade de qualquer conclusão científica ou de engenharia derivada dele.

## Alternativas Consideradas

1. **Aceitar sugestões de IA sem validação explícita** — rejeitada: risco de propagar erros sutis (especialmente em cálculos de engenharia e resultados de pesquisa) sem detecção.
2. **Validação humana manual de tudo** — rejeitada: inviável em escala e contrária ao princípio AI-first (`ADR-0006`).
3. **Engenharia orientada a evidência: toda afirmação técnica relevante (cálculo, decisão de parâmetro, resultado de pesquisa) deve ser rastreável a uma fonte verificável — teste automatizado, documentação técnica, literatura científica ou validação explícita registrada** — **Escolhida**.

## Decisão

Toda decisão técnica com impacto em cálculos de engenharia, resultados de pesquisa ou comportamento de sistema deve ser acompanhada de evidência rastreável: teste automatizado, benchmark, citação de fonte técnica/científica, ou validação explícita documentada no Registro de Entrega correspondente.

## Consequências

* Aumenta a confiabilidade de módulos futuros de CAD/CAM/CNC e do componente de pesquisa científica.
* Exige que agentes de IA declarem explicitamente o nível de confiança e a fonte de qualquer afirmação técnica não trivial.
* Cria a expectativa de que "parece correto" não é critério de aceitação — apenas evidência verificável é.
