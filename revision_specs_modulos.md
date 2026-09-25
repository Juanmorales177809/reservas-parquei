# Revisión de consistencia — modelo, reglas y flujos por módulo

**Fecha:** 2026-09-22
**Rama:** `feature/v0.1.1`, commit `023bc5d`
**Alcance:** únicamente `data-model.md`, `business-rules.md` y `user-flow.md` / `user-flows.md` de los nueve módulos. 25 documentos, 4.878 líneas.
**Fuera de alcance:** contratos de API, `docs/`, `features/`. Se mencionan solo cuando un hallazgo los afecta.

**No se modificó ningún archivo.** Este informe propone correcciones para que se aprueben antes de aplicarlas.

---

## Resumen

Las comprobaciones mecánicas salen limpias: 0 enlaces rotos, 0 anclas rotas, 0 referencias a reglas o flujos inexistentes, 0 reglas duplicadas dentro de un mismo módulo y 0 archivos vacíos. Los cambios recientes resolvieron además varios puntos que en una revisión anterior estaban abiertos: `asistentes`, la prórroga del FGL 030, `reserva_datos_salida`, el traslado de equipos a `recursos.*` y la proyección `periodo` alineada con ADR-001.

Los 15 hallazgos que siguen son **semánticos**, no de formato, y se agrupan en **ocho causas raíz**. Ninguno bloquea por sí solo la implementación del primer feature, pero cinco de ellos —A, B, C, D y E— pueden producir implementaciones divergentes si dos personas leen documentos distintos.

| Grupo | Causa raíz | Hallazgos | ¿Decisión funcional? |
|---|---|---|---|
| A | Reglas de identidad duplicadas entre `usuarios` y `auth` | 3 | Sí |
| B | Perfiles académicos sin módulo propietario | 1 | Sí |
| C | Importación masiva fragmentada entre `administration` y `resources` | 3 | Sí |
| D | Reglas sin flujo que las realice | 3 | Parcial |
| E | Tablas documentadas solo en prosa | 1 | No |
| F | Nomenclatura inconsistente de tablas y columnas | 2 | No |
| G | Referencias obsoletas tras los cambios recientes | 1 | No |
| H | Ambigüedades menores | 1 | Parcial |

---

## Grupo A — Reglas de identidad duplicadas entre `usuarios` y `auth`

**Causa raíz.** `usuarios/business-rules.md` se titula «Identidad y autorización» y define cuatro familias completas —`RN-ID`, `RN-AUT`, `RN-AUTZ`, `RN-AUD`— sobre autenticación, sesiones, autorización y auditoría. Esos son los conceptos que `auth` declara como propios en su overview. El resultado es que la misma regla existe dos veces, con redacciones distintas, y nada garantiza que cambien juntas.

### A1 — Cuatro familias de `usuarios` duplican reglas de `auth` y de `administration`

**Hallazgo.** Correspondencias directas detectadas:

| Regla en `usuarios` | Duplica |
|---|---|
| `RN-ID-01` | `RN-AUTH-ID-01` de auth |
| `RN-ID-04`, `RN-ID-05` | `RN-AUTH-ID-03` de auth |
| `RN-ID-07` | `RN-AUTH-ID-05` de auth |
| `RN-AUT-03`, `RN-AUT-04` | `RN-AUTH-SES-01` de auth |
| `RN-AUT-06` | `RN-AUTH-SES-02` de auth |
| `RN-AUTZ-02`, `RN-AUTZ-03` | `RN-AUTH-ROL-05`, `RN-AUTH-ROL-07` de auth |
| `RN-AUD-01` a `RN-AUD-04` | `RN-AUD-01` a `RN-AUD-05` de administration |

**Impacto.** Alto. Un implementador que lea solo `usuarios` obtiene una versión menos precisa: por ejemplo `RN-AUTZ-01` dice que toda acción administrativa requiere cuenta vinculada a `personal.personal`, pero no exige el tipo de cuenta `PERSONAL` ni la asignación de permiso, que `RN-AUTH-ROL-02` y `RN-AUTH-ROL-07` sí detallan. Las dos versiones ya divergieron.

**Documentos afectados.** `usuarios/business-rules.md`, `auth/business-rules.md`, `administration/business-rules.md`.

**Corrección propuesta.** Retirar de `usuarios` las familias `RN-ID`, `RN-AUT`, `RN-AUTZ` y `RN-AUD`, y dejar en su lugar un párrafo que remita a `auth` y a `administration`, como ya se hizo con `RN-ESP` en `resources`. `usuarios` conserva lo que sí le pertenece: `RN-USR`, `RN-DAT` y `RN-PER` (personal). Antes de retirar, verificar una por una si alguna aporta algo que `auth` no diga; en ese caso, trasladar el matiz a `auth` en lugar de perderlo.

**¿Requiere decisión funcional?** Sí, para confirmar que `usuarios` deja de ser propietario de identidad y autorización.

### A2 — `RN-PER` significa dos cosas distintas

**Hallazgo.** `RN-PER` es «Permisos» en `administration` (RN-PER-01 a 09) y «Personal» en `usuarios` (RN-PER-01 a 11). Ambos módulos numeran desde 01. Una cita como `RN-PER-03` designa «asignar un permiso requiere autorización suficiente» o «el cargo determina únicamente la unidad organizacional», según dónde se lea.

**Impacto.** Alto. Es la colisión más peligrosa del repositorio porque ambas familias hablan de autorización y un lector no detecta que está leyendo la regla equivocada.

**Documentos afectados.** `administration/business-rules.md`, `usuarios/business-rules.md`, y toda cita cruzada.

**Corrección propuesta.** Renombrar la familia de `usuarios` a `RN-PRS` (personal), que no colisiona. Alternativamente, si se acepta A1 y el personal se documenta junto a su identidad, mantener el prefijo pero con un número de partida distinto no resuelve la ambigüedad: conviene renombrar.

**¿Requiere decisión funcional?** No; es una decisión de nomenclatura, pero afecta a muchas citas y conviene aprobarla antes de ejecutarla.

### A3 — Otras seis familias compartidas entre módulos

**Hallazgo.** Además de `RN-PER`, comparten prefijo con significados distintos: `RN-AUD` (administration, reservations histórico, usuarios), `RN-USR` (administration y usuarios), `RN-IMP` (administration y resources), `RN-EST`, `RN-HIS`, `RN-CON`, `RN-INT`, `RN-DES`, `RN-REC`, `RN-CAL`, `RN-CTX`, `RN-REP`. Son 13 familias en total.

**Impacto.** Medio. La convención vigente en `specs/README.md` —una cita sin calificar se refiere al módulo del propio documento— lo mitiga, pero no evita el error de lectura.

**Documentos afectados.** Los nueve `business-rules.md`.

**Corrección propuesta.** No renombrar las trece. Mantener la convención y aplicar A2 solo a `RN-PER`, que es la única donde ambas familias tratan del mismo tema y por tanto la confusión es plausible.

**¿Requiere decisión funcional?** No.

---

## Grupo B — Perfiles académicos sin módulo propietario

### B1 — Reglas en `administration`, modelo en `researchs`, flujo en `usuarios`

**Hallazgo.** El concepto «perfil académico o investigativo» está repartido en tres módulos y ninguno lo declara suyo:

| Pieza | Dónde está |
|---|---|
| Reglas `RN-PRF-01` a `RN-PRF-05` | `administration/business-rules.md` |
| Tablas `investigacion.perfiles` y `investigacion.usuario_perfiles` | `researchs/data-model.md` |
| Flujo `UF-USR-05 — Actualizar perfiles académicos o investigativos` | `usuarios/user-flow.md` |

`researchs/business-rules.md` no menciona los perfiles en ninguna de sus reglas `RN-INV` ni `RN-ACT`, pese a ser el dueño del schema. `administration/data-model.md` no tiene ninguna tabla de perfiles.

**Impacto.** Medio-alto. `UF-USR-05` es el único flujo que los administra y no cita ninguna regla; `RN-PRF-04` prohíbe asignar perfiles deshabilitados, pero ninguna regla de `researchs` define quién habilita un perfil ni con qué permiso. Quien implemente el flujo no tiene regla a la que atenerse.

**Documentos afectados.** `administration/business-rules.md`, `researchs/business-rules.md`, `researchs/data-model.md`, `usuarios/user-flow.md`.

**Corrección propuesta.** Trasladar `RN-PRF` a `researchs` como parte de `RN-INV`, dado que ahí vive el modelo, y dejar en `administration` una remisión. Añadir a `researchs` la regla que falta: quién administra el catálogo de perfiles y con qué permiso, por coherencia con `RN-INV-10` y `RN-ACT-04`, que ya reservan al Administrador global la gestión de vinculaciones ajenas y actividades.

**¿Requiere decisión funcional?** Sí: hay que decidir quién administra el catálogo de perfiles.

---

## Grupo C — Importación masiva fragmentada

**Causa raíz.** La importación de catálogos está partida entre dos módulos que no coinciden en su alcance, y el modelo admite un tercer caso que ninguna regla autoriza.

### C1 — `administration` autoriza solo proyectos y semilleros

**Hallazgo.** `RN-IMP-01` de administration dice «Solo el Administrador puede importar **proyectos y semilleros**». El bloque se titula «Importación de catálogos de investigación» y `UF-ADM-01` se llama «Importar proyectos o semilleros mediante Excel». No contempla equipos.

### C2 — `resources` tiene reglas de importación de equipos sin flujo

**Hallazgo.** `resources/business-rules.md` define `RN-IMP-01` a `RN-IMP-04` para importar equipos por placa, de forma idempotente. No existe ningún flujo `UF-REC-*` que describa esa importación, ni tabla propia que registre su resultado.

### C3 — El modelo admite `EQUIPOS` pero ninguna regla lo autoriza

**Hallazgo.** `administration/data-model.md` define `administration.importaciones.catalogo` con «CHECK sobre los catálogos importables, por ejemplo `PROYECTOS`, `SEMILLEROS`, `EQUIPOS`», y dice que la importación escribe en `investigacion` o `recursos`. Es decir, el modelo de administration ya contempla importar equipos, mientras sus reglas lo excluyen.

**Impacto (C1 a C3).** Alto. `docs/spec.md` exige que el Administrador pueda importar el inventario institucional de equipos desde una planilla. Hoy esa funcionalidad tiene reglas en un módulo, respaldo persistente en otro, ningún flujo, y una regla que parece prohibirla. Dos personas implementándola llegarían a diseños distintos.

**Documentos afectados.** `administration/business-rules.md`, `administration/data-model.md`, `administration/user-flow.md`, `resources/business-rules.md`, `resources/user-flow.md`.

**Corrección propuesta.** Unificar la importación en `administration`, que ya tiene el modelo, la auditoría y el flujo: ampliar `RN-IMP-01` para incluir equipos, extender `UF-ADM-01` o añadir `UF-ADM-04` con la variante de equipos, y convertir `RN-IMP-01` a `RN-IMP-04` de `resources` en las **reglas de validación específicas del catálogo de equipos** —idempotencia por placa, placa obligatoria— citadas desde administration. Alternativamente, dejar la importación de equipos en `resources` con su propio flujo y quitar `EQUIPOS` del CHECK de administration.

**¿Requiere decisión funcional?** Sí: qué módulo es dueño de la importación de equipos.

---

## Grupo D — Reglas sin flujo que las realice

**Causa raíz.** Varias reglas describen comportamiento que ningún flujo de usuario recoge, de modo que no hay dónde verificar quién lo dispara, con qué actor y en qué orden.

### D1 — La finalización automática de una reserva por espacio no tiene flujo

**Hallazgo.** `RN-TIP-PE-24` establece que, al llegar `hora_fin`, el sistema finaliza la reserva y libera automáticamente el espacio y sus recursos complementarios, y que esos recursos no requieren entrega ni devolución física. Ningún flujo describe ese disparo temporal. Además, `UF-RES-13 — Iniciar ejecución` y `UF-RES-14 — Finalizar reserva` describen acciones manuales del Técnico sin distinguir el tipo de reserva, por lo que parecen aplicar también a las reservas por espacio, que según la regla no deberían pasar por ahí.

**Impacto.** Alto. Es el único mecanismo que libera espacios; si no se implementa, un espacio queda ocupado indefinidamente tras su franja. Y la ambigüedad de `UF-RES-13` puede llevar a exigir una entrega física que la regla descarta.

**Documentos afectados.** `reservations/business-rules.md`, `reservations/user-flows.md`.

**Corrección propuesta.** Añadir un flujo de sistema, por ejemplo `UF-RES-21 — Finalizar automáticamente una reserva por espacio`, con su disparador temporal, y acotar explícitamente `UF-RES-13` y `UF-RES-14` a los tipos que sí requieren entrega y devolución física.

**¿Requiere decisión funcional?** No sobre el comportamiento, que ya está decidido en `RN-TIP-PE-24`; sí conviene confirmar si la finalización automática aplica también a `RECURSO_INTERNO`, cuyo periodo también termina a una hora conocida.

### D2 — `notifications` y `reports` suman 117 reglas y ningún flujo

**Hallazgo.** `notifications/business-rules.md` tiene 59 reglas y `reports/business-rules.md` 58. Ninguno de los dos módulos tiene `user-flow.md`.

**Impacto.** Medio. No es una contradicción, es una ausencia. Impide derivar su contrato de API y deja sin describir quién dispara cada notificación y quién consulta cada informe. Ya está registrado como `OQ-08`.

**Documentos afectados.** `notifications/`, `reports/`.

**Corrección propuesta.** Escribir ambos `user-flow.md`. `notifications` es el más urgente porque `reservations` y `auth` ya dependen de él para recordatorios, confirmaciones, invitaciones y recuperación de contraseña.

**¿Requiere decisión funcional?** Sí, al redactarlos.

### D3 — Las reglas de importación de equipos no tienen flujo

Ver C2. Se cuenta aquí por completitud de la causa raíz.

---

## Grupo E — Tablas documentadas solo en prosa

### E1 — Cuatro tablas sin tabla de campos ni tipos

**Hallazgo.** En `reservations/data-model.md`, estas entidades se describen en un párrafo corrido en lugar de con la tabla de campos que usa el resto del documento:

| Tabla | Problema |
|---|---|
| `reservas.reserva_adjuntos` | Cinco campos sin tipo declarado: `tipo_adjunto`, `nombre_original`, `storage_key`, `content_type`, `size_bytes` |
| `reservas.reserva_historial_estado` | Campos sin tipo: `motivo`, `created_at` |
| `reservas.reserva_ejecucion_recursos` | Descripción compacta, sin restricciones explícitas |

**Impacto.** Bajo-medio. No hay contradicción, pero estas tablas quedan fuera de cualquier inventario automático y sus tipos deben inventarse al implementar. `reserva_adjuntos` sostiene el límite de 5 MB que exige `docs/spec.md` y no declara dónde se valida.

**Documentos afectados.** `reservations/data-model.md`.

**Corrección propuesta.** Convertirlas al mismo formato de tabla que el resto, declarando tipos, nulabilidad y restricciones.

**¿Requiere decisión funcional?** No, salvo el límite de tamaño y los tipos de adjunto admitidos.

---

## Grupo F — Nomenclatura inconsistente

### F1 — Singular y plural mezclados dentro de `espacios`

**Hallazgo.** El mismo módulo usa `reservas.espacio_recursos` (singular) junto a `reservas.espacios_campos` y `reservas.espacios_campos_opciones` (plural).

**Impacto.** Bajo, pero es la clase de detalle que provoca un error de tipeo en cada consulta.

**Documentos afectados.** `espacios/data-model.md`. Afecta además al contrato de espacios, fuera de alcance, que usa `espacio_campos` y `espacio_campo_opciones`, y a `reservations/data-model.md`, cuyo `reserva_campos_valores` referencia esos campos.

**Corrección propuesta.** Unificar en singular: `espacio_recursos`, `espacio_campos`, `espacio_campo_opciones`. Es la forma que ya usan el resto de tablas de asociación del repositorio (`reserva_recursos`, `reserva_acompanantes`).

**¿Requiere decisión funcional?** No.

### F2 — `reservas.id_cuenta` citado como si fuera una tabla

**Hallazgo.** `reservations/data-model.md:267` escribe `reservas.id_cuenta` cuando se refiere a la columna `reservas.reservas.id_cuenta`.

**Impacto.** Bajo.

**Corrección propuesta.** Corregir la referencia.

**¿Requiere decisión funcional?** No.

---

## Grupo G — Referencias obsoletas tras los cambios recientes

### G1 — `reports` cita «control de cambios», reemplazado por `administration.auditoria`

**Hallazgo.** `reports/data-model.md` lista entre sus fuentes «Unidades, cargos y control de cambios». `reservas.control_cambios` es la tabla del inventario heredado que `administration.auditoria` sustituye, y la auditoría de reservas quedó explícitamente fuera de alcance en esta iteración.

**Impacto.** Bajo-medio. Un informe construido sobre esa fuente consultaría una tabla que el diseño objetivo no conserva, y podría prometer trazabilidad de reservas que hoy no existe.

**Documentos afectados.** `reports/data-model.md`.

**Corrección propuesta.** Cambiar la fuente a `administration.auditoria` y añadir una nota de que la auditoría de reservas está fuera de alcance, por lo que los informes de trazabilidad se limitan a operaciones administrativas y a `reserva_historial_estado`.

**¿Requiere decisión funcional?** No.

---

## Grupo H — Ambigüedades menores

### H1 — Cinco puntos sueltos

**Hallazgo.**

| # | Punto | Documento |
|---|---|---|
| 1 | `UF-USR-04` dice «el sistema muestra los datos personales editables» sin excluir el correo, que es inmutable según `RN-AUTH-ID-02` y `RN-ID-12` | `usuarios/user-flow.md` |
| 2 | `personal.personal.estado` admite NULL, mientras `usuarios.usuarios.estado` es `NOT NULL DEFAULT true`. Varias reglas dependen de «personal activo» y un NULL no es ni activo ni inactivo | `usuarios/data-model.md` |
| 3 | `RN-PER-09` de usuarios protege la última cuenta con permisos globales, pero la restricción es sobre asignaciones de permisos, que pertenecen a `auth` | `usuarios/business-rules.md` |
| 4 | `RN-ESP-HAB-03` y `RN-ESP-HAB-05` describen lo mismo; la primera delega y la segunda concreta | `espacios/business-rules.md` |
| 5 | `usuarios/business-rules.md` cierra con una sección «Preguntas abiertas» de cuatro preguntas; al menos dos ya están respondidas en otros documentos, y el registro oficial de pendientes es `docs/decisions/open-questions.md` | `usuarios/business-rules.md` |

**Impacto.** Bajo cada uno. El punto 2 es el más relevante: un `estado` nulo en una ficha de personal dejaría indefinido si puede ejercer permisos.

**Corrección propuesta.** Puntos 1, 3, 4 y 5: precisión de redacción y traslado de `RN-PER-09` a `auth`. Punto 2: declarar `estado boolean NOT NULL DEFAULT true` en `personal.personal`, como ya se hizo en `usuarios.usuarios`, indicándolo como incorporación objetivo pendiente de migración.

**¿Requiere decisión funcional?** Solo el punto 2, por ser un cambio de modelo sobre una tabla del inventario heredado.

---

## Lo que se revisó y salió conforme

Para que la ausencia de hallazgos no se lea como falta de revisión:

- **Cadena de autorización.** `RN-AUTH-ROL-02`, `RN-AUTH-ROL-06`, `RN-AUTH-ROL-07`, `RN-PER-08`, `RN-PER-09` de administration y la derivación de rol en `auth/data-model.md` son coherentes entre sí y con `auth.cuenta_permisos`, incluidos los índices únicos parciales que distinguen asignación global de asignación por unidad.
- **`asistentes`.** `RN-TIP-PE-05`, el CHECK del detalle y la prosa coinciden: cero o más, igual al número de acompañantes, tope por capacidad.
- **Prórroga del FGL 030.** `RN-RES-14` la elimina y el modelo ya no tiene `fecha_prorroga`. Sin residuos.
- **Periodo de recursos y ADR-001.** `reserva_recursos.periodo`, `incorporado_at` y las reglas `RN-TIP-*-03` describen lo mismo que el ADR.
- **Traslado de equipos a `recursos.*`.** No quedaron referencias a `equipos.equipos` ni a `equipos.categoria`.
- **Auditoría de reservas fuera de alcance.** Declarado de forma coherente en reglas y modelo.
- **`reports` sin tablas propias.** Documentado como decisión, no como omisión.

---

## Orden sugerido

1. **C** — importación de equipos: es la única funcionalidad exigida por el producto que hoy nadie puede implementar sin decidir antes.
2. **D1** — finalización automática de reservas por espacio: sin ella, los espacios no se liberan.
3. **A1 y A2** — duplicación de identidad y colisión de `RN-PER`: cuanto más tarde se corrija, más citas habrá que ajustar.
4. **B** — propietario de los perfiles académicos.
5. **E, F, G, H** — precisión y limpieza; pueden ir en una sola pasada.
6. **D2** — flujos de `notifications` y `reports`, que además desbloquean sus contratos.
