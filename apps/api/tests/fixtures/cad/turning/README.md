# Corpus sintético de torneamento — STEP-005

Gerado com cadquery-ocp 7.9.3.1.1, sem dados de clientes ou máquina real.
Geometria e metadados fixos: os testes regeneram e comparam os bytes completos.

| Arquivo | Forma | Schema | Resultado esperado |
|---|---|---|---|
| cylinder_d50_l100.stp | D50, L100, Z=-100..0 | AP203 | r=25, Z=0..-100 |
| stepped_d30_d60.stp | D30 em Z=-40..0; D60 em Z=-100..-40 | AP214 | r=15/30, ombro em Z=-40 |
| asymmetric_keyway.stp | D50/L100 com chaveta excêntrica | AP203 | Rejeitar |
| pure_prism.stp | Bloco 30 x 40 x 100 | AP214 | Rejeitar |

Unidades métricas via `SI_UNIT(.MILLI.,.METRE.)`, admitindo whitespace da escrita
OCCT. Datum dos casos positivos: origem (0,0,0), direção axial (0,0,1), face
acabada em Z=0. São geometrias de teste, sem stock, ferramental ou tolerância de
fabricação. Os STEP não são arquivos NC nem autorizam processo físico.

Regenerar a partir da raiz do repositório:

```powershell
.\.venv\Scripts\python.exe apps/api/tests/fixtures/cad/generate_turning_step.py
```

O gerador preserva as configurações globais OCCT de schema/unidade após uso.
Normaliza apenas metadados sintéticos de data/hora e autoria; não altera entidades
geométricas para obter igualdade. Espaços finais são removidos e LF é fixado
por .gitattributes neste corpus. O determinismo é vinculado à versão do kernel.
Fontes: [gerador](../generate_turning_step.py) e
[testes](../../../modules/cad/test_turning_profile_extractor.py).
