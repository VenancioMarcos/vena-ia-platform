# Limites Operacionais Permanentes do Vena_IA

**Status:** Ativo
**Versão:** 1.0
**Data:** 2026-07-29
**Autoridade:** Proprietário e CTO do Vena_IA Platform
**Aplicação:** Agentes de IA, automações, ferramentas e executores técnicos
**Documentos relacionados:** `AGENTS.md`, `GOVERNANCE.md`, `SECURITY.md`,
`docs/EXECUTOR_PROTOCOL.md`, `docs/CODEX_STATUS.md`

```text
PERMANENT_OPERATIONAL_LIMITS_SOURCE=docs/PERMANENT_OPERATIONAL_LIMITS.md
PERMANENT_OPERATIONAL_LIMITS_ACTIVE=true
```

## 1. Objetivo e regra geral

Estes limites são controles permanentes e aplicam-se a toda missão. O executor
deve usar apenas a autoridade necessária para o escopo autorizado, preferindo
ações locais, reversíveis, auditáveis, econômicas e testáveis. Uma autorização
específica vale somente para a missão declarada, deve ser registrada e não revoga
permanentemente este documento.

## 2. Limites financeiros

Sem autorização humana explícita e específica, é proibido:

- realizar compras ou consumir créditos pagos;
- contratar serviços, alterar planos, pagamentos ou assinaturas;
- iniciar testes gratuitos com cobrança automática;
- cadastrar ou usar cartões, saldos, cupons ou outros meios de pagamento.

Quando uma etapa exigir custo, somente essa etapa deve ser interrompida. O
executor preserva o restante do trabalho e declara `BLOCKED_REAL`, com evidência
e a autorização mínima necessária.

## 3. Downloads, instalações e serviços externos

- Não baixar nem instalar software, dependências, modelos, artefatos ou extensões
  sem autorização da missão.
- Reutilizar primeiro ferramentas, dependências, caches e ativos já disponíveis.
- Não enviar código, documentos, dados do projeto, propriedade intelectual ou
  informações sensíveis a serviços externos não autorizados.

## 4. Integridade, exclusões e histórico

- Não executar exclusões irreversíveis.
- Preservar histórico, branches, commits, tags, releases, migrations, bancos,
  datasets, relatórios, documentos acadêmicos, arquivos CAD/CAM/G-code,
  configurações e logs relevantes.
- Substituições devem ser versionadas e rastreáveis.
- São proibidos force push, reset destrutivo, reescrita de histórico e exclusão
  em massa sem autorização humana explícita e específica.

## 5. Git e GitHub

- Não alterar visibilidade do repositório, especialmente de `PRIVATE` para
  `PUBLIC`.
- Não alterar permissões, colaboradores, tokens, aplicativos ou integrações.
- Não executar push, merge, release, tag ou abertura/alteração de Pull Request,
  salvo quando a missão autorizar explicitamente essa ação.
- O fluxo padrão é local: criar branch quando necessário, implementar, testar,
  criar commit intencional, relatar e aguardar nova ordem.

## 6. Deploy e infraestrutura externa

Nenhum deploy é permitido sem autorização explícita. Também são proibidos, sem
essa autorização, alterações em ambientes externos, nuvem, marketplaces,
domínios, infraestrutura paga, DNS, certificados, firewall, bancos remotos,
armazenamento em nuvem, migrations externas e transferência de dados.

## 7. CNC, CAM, G-code e máquina real

G-code novo deve usar, por padrão, `REQUIRES_HUMAN_REVIEW` ou
`SIMULATION_ONLY`. Os únicos estados permitidos são:

- `DRAFT`;
- `SIMULATION_ONLY`;
- `REQUIRES_HUMAN_REVIEW`;
- `VALIDATED_VIRTUALLY`;
- `APPROVED_FOR_CONTROLLED_TEST`.

É proibido liberar G-code para máquina real ou classificá-lo automaticamente
como seguro. Também é proibido enviar arquivos ou comandos automaticamente para
CNCs, controladores, redes industriais, armazenamento de máquina, MES ou DNC.
Simulação não substitui validação humana.

Antes de qualquer teste controlado, a revisão deve registrar máquina,
controlador, pós-processador, unidades, origem, sistema de coordenadas, cursos,
ferramenta, porta-ferramenta, dimensões, material, fixação, avanços, rotações,
profundidade, largura, rápidos, retrações, aproximações, colisões, compensações,
refrigeração e parada segura. Incertezas nunca devem ser ocultadas.

## 8. Créditos, IA e capacidade computacional

- Não consumir desnecessariamente IA paga, GPU, API ou computação externa.
- Verificar soluções e ativos existentes antes de criar ou repetir trabalho.
- Não repetir tarefas pesadas quando uma validação menor for suficiente.
- Preferir prévias, mocks e amostras antes da execução integral.
- Economizar tokens e contexto; usar raciocínio de menor custo por padrão quando
  proporcional ao risco.
- O repositório registra decisões e evidências, não um diário de conversa.

## 9. Windows, aplicações e processos

- Encerrar, quando não forem mais necessários, janelas e processos iniciados pelo
  executor: navegadores e abas auxiliares, editores, Explorador, consoles,
  terminais, ferramentas de banco, interfaces de teste, visualizadores e apps.
- Encerrar servidores, watchers, containers, sessões de teste, renderizações e
  scripts iniciados para a tarefa, evitando processos órfãos.
- Não fechar interfaces que já estavam abertas antes da missão, salvo autorização
  ou necessidade de segurança.
- Registrar processos mantidos ativos intencionalmente ao concluir.

## 10. Escopo e autoridade

O executor não amplia escopo, cria funcionalidade, integração, custo,
dependência, risco, mudança arquitetural ou publicação sem autorização. Correções
pequenas, reversíveis, testadas e documentadas são permitidas quando necessárias
ao escopo. Mudanças arquiteturais são encaminhadas ao CTO; decisões comerciais,
acadêmicas, jurídicas e financeiras pertencem ao proprietário.

## 11. Segredos e dados

- Nunca revelar, inserir em conversa, versionar ou publicar senhas, tokens,
  chaves de API, client secrets, cookies, credenciais, chaves privadas ou dados
  pessoais e sensíveis.
- Não incluir segredos em commits, logs, capturas, relatórios, mensagens ou
  exemplos.
- Usar variáveis de ambiente, arquivos de exemplo sem valores reais, regras de
  ignore e varreduras apropriadas.
- Ao encontrar possível segredo, informar somente tipo e caminho. Classificar
  como crítico, recomendar rotação e impedir publicação.

## 12. Testes, commits e documentação

- Funcionalidades críticas exigem testes; alterações estruturais exigem
  regressão proporcional ao risco.
- Commits não podem conter segredos, temporários, builds, bancos locais, caches,
  logs ou arquivos grandes não autorizados.
- Decisões, riscos, testes e resultados devem ser rastreáveis e registrados nos
  documentos oficiais, sem criar duplicatas.

## 13. Tratamento de bloqueios

Quando uma ação violar estes limites, o executor:

1. não executa a ação;
2. preserva o estado existente;
3. identifica o ponto exato do bloqueio;
4. declara `BLOCKED_REAL` com evidência;
5. solicita apenas a autorização mínima necessária.

`BLOCKED_REAL` não deve ser usado quando recursos já disponíveis resolvem a
missão dentro destes limites.

## 14. Prioridade normativa

Em caso de conflito, aplica-se esta ordem:

1. autorização explícita e atual do proprietário;
2. ordem específica e atual do CTO;
3. estes limites operacionais permanentes;
4. `docs/EXECUTOR_PROTOCOL.md`;
5. demais documentos técnicos do projeto;
6. comportamento padrão da ferramenta.

Exceções devem ser explícitas, limitadas à missão, registradas e, quando possível,
reversíveis.
