# Reportes

Contrato funcional del módulo de reportes.

El módulo de reportes permite consultar, visualizar y descargar información consolidada sobre la ocupación y uso de laboratorios, espacios y recursos.

Los reportes utilizan información registrada por los módulos propietarios y no modifican reservas, recursos, usuarios, permisos ni configuraciones del sistema.

---

## Generación de reportes — RN-REP

- **RN-REP-01:** Todo reporte debe generarse a partir de información registrada y disponible en el sistema.

- **RN-REP-02:** La generación de un reporte es una operación de consulta y no puede modificar el estado de las entidades utilizadas como fuente.

- **RN-REP-03:** Los resultados deben corresponder a los criterios y filtros seleccionados por el usuario.

- **RN-REP-04:** La misma combinación de datos fuente y criterios de consulta debe producir resultados consistentes mientras los datos consultados no cambien.

- **RN-REP-05:** Cuando no existan registros que cumplan los criterios seleccionados, el sistema debe devolver un resultado vacío identificable y no interpretar la ausencia de datos como un error.

- **RN-REP-06:** La generación de reportes no sustituye los registros transaccionales ni el historial de los módulos propietarios.

---

## Ámbito de consulta — RN-AMB

- **RN-AMB-01:** Un Técnico solo puede consultar reportes de su propia unidad organizacional.

- **RN-AMB-02:** Un Administrador puede consultar reportes de cualquier unidad organizacional.

- **RN-AMB-03:** El acceso a un reporte debe validarse con información vigente de autorización al momento de realizar la consulta.

- **RN-AMB-04:** La posibilidad de consultar una entidad individual no implica automáticamente autorización para consultar reportes agregados fuera del ámbito permitido.

- **RN-AMB-05:** Los filtros solicitados por el cliente no pueden ampliar el ámbito de información autorizado para la cuenta autenticada.

---

## Dimensiones de reporte — RN-DIM

Los informes de ocupación pueden organizarse según las dimensiones definidas por la especificación del producto.

- **RN-DIM-01:** El sistema debe permitir consultar información de ocupación por laboratorio.

- **RN-DIM-02:** El sistema debe permitir consultar información de ocupación por espacio.

- **RN-DIM-03:** El sistema debe permitir consultar información de ocupación por recurso.

- **RN-DIM-04:** El sistema debe permitir consultar información de ocupación por proyecto cuando la reserva tenga un proyecto asociado.

- **RN-DIM-05:** El sistema debe permitir consultar información de ocupación por semillero cuando la reserva tenga un semillero asociado.

- **RN-DIM-06:** La ausencia de proyecto o semillero en una reserva no invalida dicha reserva ni impide su inclusión en reportes que no dependan de esas dimensiones.

- **RN-DIM-07:** Las dimensiones utilizadas en un reporte deben corresponder a relaciones registradas en las fuentes de datos del sistema y no inferirse a partir de nombres u otros atributos no destinados a establecer relaciones.

---

## Periodos y filtros — RN-FIL

- **RN-FIL-01:** Los reportes deben permitir limitar la consulta mediante un periodo cuando el tipo de reporte dependa de información temporal.

- **RN-FIL-02:** Cuando se indiquen fecha inicial y fecha final, la fecha inicial no puede ser posterior a la fecha final.

- **RN-FIL-03:** Los filtros aplicados deben respetar las relaciones existentes entre las entidades consultadas.

- **RN-FIL-04:** Un filtro que haga referencia a una entidad inexistente o fuera del ámbito autorizado no debe producir acceso a información no permitida.

- **RN-FIL-05:** La ausencia de un filtro opcional debe interpretarse como consulta del conjunto permitido por el ámbito del usuario, no como acceso sin restricciones.

---

## Estados de reserva — RN-EST

- **RN-EST-01:** Los reportes que utilicen reservas como fuente deben diferenciar los estados registrados en el módulo de reservas.

- **RN-EST-02:** El significado de cada estado y sus transiciones pertenece al módulo de reservas y no se redefine en reportes.

- **RN-EST-03:** Cuando un reporte incluya o excluya determinados estados, dicha condición debe estar explícitamente definida por el tipo de reporte.

- **RN-EST-04:** El módulo de reportes no puede modificar el estado de una reserva para alterar su inclusión en un resultado.

---

## Ocupación — RN-OCU

- **RN-OCU-01:** La ocupación debe calcularse a partir de reservas registradas y de las relaciones efectivamente asociadas a laboratorios, espacios o recursos.

- **RN-OCU-02:** Un reporte de ocupación debe utilizar criterios temporales consistentes con las fechas y horarios registrados en las reservas.

- **RN-OCU-03:** Un mismo elemento no debe contabilizarse más de una vez dentro de la misma unidad de análisis cuando corresponda al mismo registro de reserva y al mismo criterio de agrupación.

- **RN-OCU-04:** Los criterios específicos para calcular indicadores derivados, porcentajes o tasas de ocupación deben definirse antes de implementar dichos indicadores.

- **RN-OCU-05:** No debe inferirse capacidad disponible, tiempo disponible u ocupación porcentual cuando el modelo no contenga la información necesaria para calcularlos.

---

## Contexto académico e investigativo — RN-CTX

- **RN-CTX-01:** Los reportes por proyecto o semillero utilizan el contexto registrado en la reserva correspondiente.

- **RN-CTX-02:** Una modificación posterior en la vinculación del usuario con un proyecto o semillero no debe alterar retroactivamente el contexto histórico registrado para una reserva.

- **RN-CTX-03:** Una reserva sin proyecto o semillero asociado no debe asignarse artificialmente a uno durante la generación de reportes.

- **RN-CTX-04:** El contexto académico o investigativo se utiliza como dimensión de análisis y no modifica las reglas de autorización para consultar información.

---

## Datos históricos — RN-HIS

- **RN-HIS-01:** Los reportes históricos deben basarse en la información conservada por los módulos propietarios.

- **RN-HIS-02:** La desactivación posterior de un laboratorio, espacio, recurso, usuario, proyecto o semillero no debe eliminar automáticamente su participación en reportes históricos.

- **RN-HIS-03:** Cuando una entidad haya cambiado posteriormente, el reporte debe utilizar la información histórica disponible cuando esta sea necesaria para interpretar correctamente el registro.

- **RN-HIS-04:** El módulo de reportes no debe reconstruir información histórica mediante suposiciones cuando dicha información no esté almacenada.

---

## Visualización — RN-VIS

- **RN-VIS-01:** La información mostrada en una visualización debe corresponder a los mismos datos y filtros utilizados para generar el reporte.

- **RN-VIS-02:** Las visualizaciones no deben alterar, redondear o transformar los datos de forma que cambie su interpretación funcional.

- **RN-VIS-03:** Cuando una visualización agrupe información, debe ser posible identificar el criterio de agrupación utilizado.

- **RN-VIS-04:** Un resultado sin datos debe representarse como ausencia de información para los criterios seleccionados y no mediante valores ficticios.

---

## Exportación — RN-EXP

- **RN-EXP-01:** Los usuarios autorizados pueden descargar los reportes disponibles para su ámbito de consulta.

- **RN-EXP-02:** El archivo exportado debe corresponder a los mismos filtros y criterios utilizados en el reporte consultado.

- **RN-EXP-03:** La exportación no debe incluir información fuera del ámbito autorizado del usuario.

- **RN-EXP-04:** El archivo debe incluir información suficiente para identificar el periodo y los criterios principales utilizados para generar el reporte.

- **RN-EXP-05:** El formato específico de exportación debe definirse en el diseño o contrato correspondiente antes de su implementación.

---

## Consistencia de datos — RN-CON

- **RN-CON-01:** El módulo de reportes consume información de los módulos propietarios y no mantiene una fuente alternativa que contradiga dichos datos.

- **RN-CON-02:** Las relaciones entre reservas, laboratorios, espacios, recursos, proyectos y semilleros deben determinarse mediante sus identificadores y relaciones persistentes.

- **RN-CON-03:** Los nombres de entidades pueden utilizarse para presentación, pero no como mecanismo principal para relacionar registros.

- **RN-CON-04:** Cuando los datos fuente sean insuficientes para calcular un resultado, el sistema no debe completar el valor mediante estimaciones no definidas.

---

## Protección de información — RN-PRI

- **RN-PRI-01:** Los reportes deben exponer únicamente la información necesaria para el objetivo de la consulta.

- **RN-PRI-02:** La generación o exportación de un reporte no debe incluir credenciales, tokens, hashes, secretos ni otra información técnica sensible.

- **RN-PRI-03:** Los datos personales incluidos en reportes deben limitarse a aquellos necesarios para la función autorizada.

- **RN-PRI-04:** Los mecanismos de filtrado, ordenamiento o exportación no pueden utilizarse para evadir las restricciones de autorización.

---

## Separación de responsabilidades

- El módulo de reservas determina el estado, horario, composición y contexto registrado de cada reserva.

- El módulo de recursos determina la identidad, pertenencia, capacidad, habilitación y estado de laboratorios, espacios y recursos.

- El módulo de autenticación y autorización determina quién puede consultar información y cuál es su ámbito permitido.

- El módulo de reportes consulta, filtra, agrupa, presenta y exporta información existente.

- El módulo de reportes no crea, modifica, aprueba, rechaza ni cancela reservas.

- El módulo de reportes no modifica laboratorios, espacios, recursos, usuarios, permisos, proyectos ni semilleros.

---

## Dependencias funcionales

Las reglas de este documento dependen de otros módulos en los siguientes aspectos:

- **Reservas:** proporciona las reservas, estados, fechas, horarios, recursos asociados y contexto registrado.

- **Recursos:** proporciona laboratorios, espacios, recursos y sus relaciones organizacionales.

- **Autenticación y autorización:** determina la cuenta autenticada y el ámbito de información que puede consultar.

- **Modelo persistente:** define las relaciones y datos disponibles para construir consultas y agregaciones.

---

## Principios del módulo

1. Un reporte consulta información; no modifica el sistema.

2. Los módulos propietarios siguen siendo la fuente de verdad sobre sus datos.

3. Todo reporte respeta el ámbito de autorización del usuario.

4. Los resultados deben derivarse de información almacenada y relaciones verificables.

5. Los datos históricos no deben reinterpretarse utilizando información actual cuando ello cambie el significado original.

6. Los indicadores derivados solo pueden implementarse cuando su definición y datos necesarios estén establecidos.

7. Visualización y exportación deben representar el mismo conjunto de datos y criterios de consulta.