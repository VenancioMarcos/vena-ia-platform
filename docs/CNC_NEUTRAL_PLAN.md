# CNC Neutral Plan v1

`vena-ia.cnc-neutral-plan/v1` formaliza de forma aditiva o preview CNC existente;
não cria um segundo engine. O contrato acrescenta referência ao planning e à
recommendation, operation candidates, assumptions neutras, warnings, traceability,
review status e flags de segurança.

Valores invariantes:

* `simulation_only=true`;
* `executable_output=false`;
* `review_status=REQUIRES_HUMAN_REVIEW`;
* `status=SIMULATION_ONLY_REQUIRES_HUMAN_REVIEW`.

Controller family e machine profile continuam placeholders. Clearance explícito é
somente input preliminar e não coordenada de toolpath. O contrato não contém blocos
de controlador, cutter-location data, pós-processador, G-code, M-code, NC/DNC,
destino de transmissão ou controle CNC. Nenhum resultado afirma compatibilidade
física, segurança, manufaturabilidade ou prontidão produtiva.

No Package 3, a UI mostra apenas os campos neutros permitidos e as invariantes de
segurança. Não existe editor, viewer de código/toolpath, download NC, botão de envio
ou controle de máquina; testes E2E verificam essas ausências.
