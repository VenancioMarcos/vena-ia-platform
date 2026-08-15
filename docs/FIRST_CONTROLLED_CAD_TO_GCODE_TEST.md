# First Controlled CAD-to-G-code Test Path

**Task:** TASK-V31-006

**Classification:** NON_PRODUCTION / REQUIRES_HUMAN_REVIEW

**Physical authority:** FALSE

## Objective and scope

Provide the first repeatable v3.1 test path from a valid CAD upload to a controlled
G-code candidate download while preserving the released safety boundary. The path
uses existing application contracts and does not add v3.2 scope, external deployment,
machine connectivity or physical authority.

## Gap check

- The backend already implemented the complete authenticated orchestration and
  controlled download, but route coverage mocked the CAD service.
- The web interface did not display Manufacturing Geometry, Process Plan, Toolpath,
  Level-2 and detailed Digital Thread artifact evidence.
- Candidate download displayed warnings but did not require an explicit
  non-production acknowledgement.
- The repository and GitHub metadata contain no deployment configuration,
  environments, deployments, action secrets or variables for an approved external
  web target. The existing local web boundary is therefore the shortest safe target.

## Controlled path

1. Generate a valid STEP cylindrical body at test runtime using the official OCCT
   kernel dependency; no expected features are supplied to the implementation.
2. Authenticate a database-backed user with active Organization/project membership.
3. Upload the STEP body through the real Documents API and in-memory test storage.
4. Execute the real CAD kernel, topology/manufacturing evidence, verified process
   planning, bounded toolpath, synthetic candidate generation, Level-1/Level-2,
   blind validation, G0-G8 and Digital Thread services.
5. Revalidate the controlled download proof and candidate content through the real
   download route.
6. In browser coverage, review each evidence group and explicitly acknowledge
   NON_PRODUCTION, required human review and absence of physical authority before
   enabling download.

## Evidence and acceptance

- The backend integration test proves actual upload-to-download service wiring with a
  valid CAD body and no mocked CAD result.
- Desktop and reduced-width browser tests prove reviewable evidence and guarded
  download UX.
- G9 remains `PENDING_AUTHORITATIVE_REVIEW`.
- `CAD_TO_GCODE_CONTROLLED_VALIDATION_READY=FALSE`.
- `PHYSICAL_USE_AUTHORIZED=FALSE`.
- No machine-send, DNC/NC transfer, cycle start, direct machine control or human-review
  bypass exists or was exercised.

## Known limitations and next evidence

- The first body is cylindrical but the released candidate path is 3-axis/2.5D
  milling; this test does not claim turning or facing validation.
- A representative corpus of prismatic, holes/pockets, contouring and turning parts
  remains required before broader controlled-validation readiness can be considered.
- The deterministic browser suite verifies the UI contract with API fixtures, while
  TESTE_01 additionally verified the complete authenticated path through the real
  rendered browser and local service stack.
- External hosted deployment and independent external simulation remain separate
  owner/CTO-authorized work.

## Relatório técnico de execução — TESTE_01

**Data:** 2026-08-15

**Resultado:** `TASK_SUCCESS`

**Entrada:** `TESTE_01_cube.stp`

**Projeto:** `TESTE_01 — Cubo STEP Controlado`

Este registro preserva a primeira execução ponta a ponta observada pela interface
real do navegador. Ele complementa os testes automatizados: nenhum atalho de API foi
usado para declarar sucesso do caminho visual.

### Evidência de entrada

- Fonte: `https://raw.githubusercontent.com/jeromerobert/jCAE/master/occjava/test/input/cube.stp`.
- Tamanho: `15,679` bytes.
- SHA-256: `3831666d50d58d79769d38d2730de02c91b9882e41be26980ee912ee5cd01b00`.
- Marcadores confirmados: `ISO-10303-21` e `END-ISO-10303-21;`.
- Documento: `5dfe6d38-4b98-4840-bc75-61be23afe54f`.
- Projeto: `8ddca5b4-31b9-4a9c-a0ac-67eb2c15aa99`.

### Diagnósticos e soluções aplicadas

1. **MIME genérico do navegador.** O Chrome enviou o STP como
   `application/octet-stream`, enquanto o servidor aceitava somente o MIME STEP
   oficial. A correção ficou restrita a `.step`/`.stp`: extensão permitida, tamanho
   limitado, cabeçalho e marcador terminal STEP válidos são obrigatórios antes de
   aceitar o MIME genérico e normalizá-lo para `application/step`. A validação global
   não foi enfraquecida.
2. **Kernel CAD indisponível no container.** O OCP falhava pela ausência de
   `libGL.so.1`. A imagem da API passou a instalar somente `libgl1` e foi recriada sem
   remover volumes. O runtime oficial confirmou `OCP_KERNEL=READY`.
3. **Timeout durante inicialização fria.** Somente a chamada do Controlled Test
   Environment recebeu limite de `120,000 ms`; os demais contratos conservaram o
   timeout anterior de 30 segundos.
4. **Stock no limite da tolerância.** A geometria calculada variava aproximadamente
   de `-1.0000001` a `1.0000001`, superando o stock `-1` a `1`. O formulário real foi
   corrigido para `[-2,-2,-2]` a `[2,2,2]`, sem alterar regras ou código de segurança.
5. **Confirmação objetiva do download.** A espera pelo evento do navegador expirou,
   mas o clique havia sido processado. O êxito foi comprovado pelo arquivo real no
   disco, seu tamanho, hash e conteúdo, evitando repetir o teste.

### Execução real concluída

- Sessão autenticada pela interface real com a conta local previamente salva pelo
  proprietário; nenhuma credencial foi registrada ou exposta.
- Organização, projeto, documento e catálogos de teste pertencentes à organização
  foram selecionados pela interface.
- Manufacturing Geometry: `READY_FOR_REVIEW`, topologia válida, unidade `mm`, stock
  contendo a geometria e seis regiões removíveis.
- Verified Process Plan: `PASS_REQUIRES_HUMAN_REVIEW`, coerente, com uma operação
  candidata `GEOMETRIC_ROUGHING_CANDIDATE` não executável.
- Toolpath: `CANDIDATE_FOR_VALIDATION`, 19 segmentos lineares, seis regiões-alvo e
  autoridade de produção falsa.
- Level-2: `PASS_REQUIRES_HUMAN_REVIEW`, cobertura completa, sem gouge nem violação
  de superfície protegida; validação física falsa.
- Gates `G0` a `G8`: `PASS` com evidência; `G9=PENDING_AUTHORITATIVE_REVIEW`.
- Digital Thread: `COMPLETE_NON_PRODUCTION`, nove artefatos imutáveis, thread
  `thread-757e1f583cadbf352e047017`.
- O candidato começa com `G21/G17/G90/G94`, termina em `M30` e não contém `M03`,
  `M04` ou `M06`.

### Artefato baixado

- Arquivo: `vena-ia-fd23a2b2dec85a45.candidate.nc`.
- Tamanho: `829` bytes.
- SHA-256: `fd23a2b2dec85a4522082e7992dfd5ab90171080fc736a28be9967387986cb49`.
- O reconhecimento explícito de `NON_PRODUCTION` e revisão humana obrigatória foi
  marcado na interface antes do download.

### Ambiente, testes e CI

- Docker, PostgreSQL, Redis, MinIO, API, worker e frontend operacionais.
- API `/ready`: HTTP `200`, versão `3.1.0`, dependências prontas.
- Frontend: HTTP `200`; build de produção e typecheck aprovados.
- Import do OCP no container oficial: aprovado.
- `apps/api/tests/test_first_controlled_cad_path.py`: `1 passed`.
- Validação focal de documentos: `35 passed`; Ruff e mypy aprovados.
- Docker Compose config: aprovado.
- Draft PR #31: aberta, mergeável; Backend CI, Frontend CI e Runtime Policy CI verdes.

### Commits da estabilização

- `534d2cf` — `fix(documents): accept validated browser STEP uploads`.
- `02ed0a0` — `fix(runtime): load CAD kernel dependencies`.
- `faf982b` — `fix(web): allow controlled CAD validation runtime`.
- `6e38175` — `docs(engineering): record TESTE_01 completion`.

### Limitações e divergências conhecidas

- O pipeline assíncrono historicamente orientado a PDF pode marcar um STEP como
  `FAILED` ao tentar interpretá-lo como PDF. O caminho CAD controlado lê o STEP
  armazenado diretamente e foi validado; a divergência permanece registrada.
- O rótulo visual legado `v1.5` diverge da API real `3.1.0` e não foi usado para
  inferir o estado do runtime.
- O healthcheck genérico do container worker pode divergir do estado autoritativo
  reportado por `/ready`; este teste usou o contrato da API.
- O resultado cobre um único cubo STEP controlado; não autoriza uso físico, CNC, um
  segundo CAD ou generalização industrial.

### Estratégia operacional adotada

O projeto passa a reutilizar, quando compatível com a missão autorizada, o fluxo
**ponta a ponta orientado por evidências**:

1. ler contexto, decisões e limites oficiais;
2. confirmar o estado real do repositório e do runtime;
3. reproduzir a jornada pela interface renderizada do navegador;
4. usar abas separadas para aplicação local, diagnóstico, runtime e validação remota,
   sem confundir evidências entre ambientes;
5. localizar a camada exata da falha antes de editar código;
6. aplicar a menor correção segura e especificamente delimitada;
7. reconstruir somente o serviço afetado, preservando dados e volumes;
8. retomar o mesmo projeto e a mesma entrada, evitando duplicação e falso sucesso;
9. verificar artefatos no disco por tamanho, hash e conteúdo;
10. executar testes proporcionais, CI e registrar o handoff objetivo.

O controle do navegador não substitui contratos, autenticação ou validação
server-side; ele comprova a experiência real do usuário. O método permanece sujeito
a autorizações protegidas, disponibilidade das ferramentas e gates de segurança.

### Estado terminal e segurança

- `FIRST_BROWSER_CAD_TO_GCODE_TEST_EXECUTABLE=TRUE`.
- `TESTE_01=PASS`.
- `OWNER_MANUAL_VALIDATION_READY=TRUE`.
- `CTO_EXECUTION_PHASE_CLOSED=TRUE`.
- `CAD_TO_GCODE_CONTROLLED_VALIDATION_READY=FALSE`.
- `PHYSICAL_USE_AUTHORIZED=FALSE`.
- `MACHINE_SEND=DNC=NC_TRANSFER=CYCLE_START=DIRECT_MACHINE_CONTROL=FALSE`.
- `NO_HUMAN_REVIEW_BYPASS=TRUE`.
- `V3_2=NOT_STARTED`.
- Nenhum deploy, envio CNC ou uso físico ocorreu.

## Delivery record

- **Objective:** first controlled CAD-to-G-code test path.
- **Files:** backend integration test, web evidence/review controls, contracts,
  browser tests and project governance documents.
- **Tests:** focal backend integration, frontend typecheck/build and browser coverage;
  full regression is the release gate for the Draft PR.
- **Acceptance:** repeatable real backend chain, reviewable browser evidence and all
  safety invariants preserved.
- **Next step:** CTO review of the Draft PR; no new phase starts automatically.
