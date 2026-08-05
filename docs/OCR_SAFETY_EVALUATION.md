# Avaliação de segurança e viabilidade de OCR — v1.5 Package 2

**Decisão:** B — ADIADO POR RISCO OU AUSÊNCIA DE EVIDÊNCIA

**Data:** 2026-08-05

**Implementação nesta entrega:** nenhuma

## Estado e detecção

O parser atual valida `%PDF-`, usa `PdfReader(..., strict=True)`, recusa
`reader.is_encrypted`, converte erro de parsing em `PDF_INVALID` e recusa todas as
páginas sem texto como `PDF_NO_TEXT`. `pypdf` não é OCR e não extrai texto de
imagens, conforme sua [documentação oficial](https://pypdf.readthedocs.io/en/5.7.0/user/extract-text.html).
Esses sinais são confiáveis para decidir **não continuar**; não provam que uma
página mista possui qualidade textual suficiente.

## Alternativas

| Alternativa | Privacidade/isolamento | Portabilidade/custo | Qualidade e risco | Decisão |
|---|---|---|---|---|
| Falha explícita atual | nenhum envio; menor superfície | já funciona em Windows/Linux/Docker | não atende scan, mas não inventa texto | manter |
| OCR local no worker | arquivo fica local | CPU/RAM/duração não medidas; binários/modelos extras | bloqueio síncrono e parser de imagem no worker | não aprovar |
| Processo/container isolado | sem rede, limites e kill preemptivo possíveis | exige empacotamento reproduzível e operação | melhor contenção, ainda precisa corpus/gate | candidato futuro |
| Serviço externo | envia documento a terceiro | custo, residência, retenção e contrato | dependência/privacidade/auditoria adicionais | não aprovar |

Tesseract é Apache-2.0, suporta mais de 100 idiomas e imagens, mas não lê PDF
diretamente; PDF exige rasterização/conversão adicional, conforme o
[repositório oficial](https://github.com/tesseract-ocr/tesseract) e os
[formatos oficiais](https://tesseract-ocr.github.io/tessdoc/InputFormats.html).
OCRmyPDF recomenda container ou VM para PDFs não confiáveis e timeouts/limites;
isso confirma que executar no processo atual não é gate seguro
([documentação de segurança](https://ocrmypdf.readthedocs.io/en/latest/pdfsecurity.html)).

## Critérios não comprovados

- CPU, memória, duração e timeout preemptivo por página/documento;
- português/inglês e orientação/rotação em resoluções aprovadas;
- qualidade mínima por CER/WER e rejeição abaixo do limiar;
- tabelas, desenhos técnicos, símbolos, cotas e texto sobre geometria;
- PDF malformado, bombs, anexos, ações, imagens gigantes e cleanup;
- paridade Windows/Linux/Docker e licença de todas as dependências transitivas;
- observabilidade sem conteúdo, retenção e auditoria do artefato derivado;
- custo operacional e aprovação humana/jurídica de qualquer serviço externo.

## Gate futuro obrigatório

Somente um protótipo controlado futuro pode ser considerado, com corpus sintético
e autorizado, processo/container sem rede, usuário não privilegiado, filesystem
descartável, limites de CPU/RAM/tamanho/páginas, timeout preemptivo e kill, limpeza,
SBOM/licenças, métricas bounded e revisão humana. Comparar texto esperado por CER/WER
e amostras específicas de tabelas/desenhos/rotação. Nenhum dado real ou terceiro.

R-017 permanece aberto. R-038 permanece monitorado. A próxima versão/gate depende
de autorização específica e não é automaticamente v1.6.
