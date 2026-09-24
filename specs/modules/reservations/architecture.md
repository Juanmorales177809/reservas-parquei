# Arquitectura de Reservations

## Alcance y fuentes

Diseño documental del módulo; no representa backend ni migraciones implementados. Sus fuentes son las [reglas de negocio](business-rules.md), los [flujos](user-flows.md), el [modelo](data-model.md), el [contrato HTTP](../../contratos/reservations/api-contract.md), las [pruebas especificadas](tests.md) y el [estado de la base](database-status.md). Los nombres de clases y archivos siguientes son una propuesta de organización, no cambios en tablas, campos o rutas.

Se mantienen los cinco tipos y los seis estados globales actuales. Este diseño no amplía operaciones, permisos, auditoría ni requisitos funcionales.

## Flujo y dependencias

Flujo lógico: **router → service → Reserva/Strategy → repository**. La última etapa la ejecuta el servicio: ni `Reserva` ni la estrategia acceden directamente al repositorio.

1. El router interpreta la petición conforme al contrato y obtiene el contexto de sesión.
2. El servicio comprueba acceso, abre la transacción cuando hay escritura y carga mediante el repositorio la reserva y los datos necesarios para decidir.
3. El servicio selecciona la estrategia por el código del tipo e instancia o reconstruye `Reserva`, que actúa como Context.
4. `Reserva` delega el comportamiento específico a `ReservationStrategy`. Las políticas reutilizables comprueban las condiciones comunes aplicables.
5. El servicio persiste los cambios resultantes mediante el repositorio, incluidos los efectos sobre otras reservas que la operación exija. Confirma todo o revierte la operación.
6. El router produce la respuesta definida por el contrato. Los efectos de notificación y exportación respetan las dependencias existentes del módulo.

Las lecturas no necesitan pasar por una estrategia cuando no hay una decisión específica del tipo. Los procesos automáticos de horario y deshabilitación entran por el servicio, sin simular una petición HTTP; emplean las mismas reglas y mecanismos de persistencia.

## Responsabilidades

| Componente | Responsabilidad | Límite |
|---|---|---|
| `router` | Rutas, cuerpos, parámetros, sesión y serialización; traducción de errores de dominio al catálogo HTTP | No decide disponibilidad ni transiciones; no consulta directamente la base |
| `service` | Casos de uso, autorización, carga de información, selección de estrategia, políticas comunes, coordinación entre reservas y límites transaccionales | No replica las reglas particulares de los cinco tipos |
| `Reserva` | Context con cabecera, detalle y asociaciones relevantes; ofrece la delegación del comportamiento específico | No sustituye al servicio, no posee la transacción y no es un modelo HTTP ni una tabla nueva |
| `ReservationStrategy` | Validación y determinación de cambios específicos de una operación para un tipo | No obtiene sesión, no ejecuta SQL, no confirma transacciones ni envía notificaciones |
| `repository` | Consultas, reconstrucción y persistencia, bloqueos y operaciones de integridad dentro de la transacción del servicio | No decide permisos, estados o consecuencias funcionales; no crea ni altera el esquema |

El tipo de una reserva existente determina su estrategia; no se cambia de estrategia para eludir restricciones ni para cambiar el tipo inmutable. El selector contiene exactamente las cinco correspondencias del catálogo. La habilitación de un tipo para nuevas solicitudes se valida aparte de la reconstrucción de reservas históricas.

## Context e interfaz común

`Reserva` mantiene la referencia a una `ReservationStrategy` y delega mediante un punto de entrada conceptual `resolver_operacion(operacion, datos, condiciones)`. El servicio sigue siendo responsable de preparar la información, comprobar las políticas comunes y guardar el resultado.

La interfaz común `ReservationStrategy` declara:

| Operación conceptual | Resultado |
|---|---|
| `validar_operacion(reserva, operacion, datos, condiciones)` | Comprueba admisibilidad por tipo, detalle, estado y condiciones específicas; ante fallo produce un error de dominio |
| `determinar_cambios(reserva, operacion, datos, condiciones)` | Describe los cambios exigidos por la operación validada: detalle, asociaciones, transición y registros expresamente previstos |

Estas firmas documentan responsabilidades, no un endpoint genérico. `operacion` identifica únicamente los casos de uso ya existentes en el contrato y los flujos automáticos. `datos` conserva los campos propios de cada operación; no convierte todos los cuerpos en uno universal. `condiciones` contiene información vigente obtenida por el servicio, como disponibilidad, configuración e instante de evaluación; no contiene una conexión ni un repositorio.

`Reserva` coordina ambas llamadas sin escrituras intermedias. El resultado es un objeto de trabajo en memoria, no una tabla, un registro de auditoría ni un nuevo historial de eventos. Se persiste únicamente lo requerido por el modelo actual. Si una operación no aplica al tipo, falla con `TIPO_NO_ADMITIDO`; el estado incorrecto se distingue mediante `ESTADO_INCOMPATIBLE`. No hay métodos vacíos que aparenten éxito.

Esta separación permite comprobar comportamiento específico sin HTTP ni SQL. La revalidación y protección de concurrencia siguen siendo obligatorias al ejecutar el caso de uso transaccional; una decisión en memoria no garantiza disponibilidad.

## Estrategias concretas

| Tipo y clase | Comportamiento delegado | Referencias principales |
|---|---|---|
| `ESPACIO` — `EspacioStrategy` | Detalle de espacio, capacidad, acompañantes y campos configurados; complementarios; disponibilidad por franja; aprobación durante la franja; inicio y fin automáticos; incorporación y retiro manual permitidos | RN-TIP-PE-14, RN-TIP-PE-21, RN-TIP-PE-23, RN-TIP-PE-25, RN-TIP-PE-27; UF-RES-01, UF-RES-09, UF-RES-21, UF-RES-22 |
| `RECURSO_INTERNO` — `RecursoInternoStrategy` | Un principal y adicionales; franjas sin entrega/devolución; inicio y fin automáticos; gestión técnica solo de adicionales; principal protegido frente al retiro genérico; cancelación según inicio | RN-TIP-RI-01, RN-TIP-RI-04, RN-TIP-RI-07, RN-TIP-RI-08, RN-TIP-RI-09, RN-TIP-RI-10, RN-TIP-RI-13; UF-RES-02, UF-RES-10 |
| `RECURSO_CAMPUS` — `RecursoCampusStrategy` | Préstamo que sale del laboratorio y permanece en campus; fechas y destino; compromiso físico; aprobación, FGL 030 y entrega dentro del proceso de salida; devolución completa | RN-TIP-RC-01, RN-TIP-RC-03, RN-TIP-RC-07, RN-TIP-RC-09, RN-TIP-RC-10; UF-RES-03, UF-RES-13, UF-RES-14 |
| `RECURSO_EXTERNO` — `RecursoExternoStrategy` | Préstamo fuera del campus de recursos autorizados; condiciones del destino externo; mismo proceso físico y conservación de la orden | RN-TIP-RE-01, RN-TIP-RE-03, RN-TIP-RE-07, RN-TIP-RE-09, RN-TIP-RE-10; UF-RES-04, UF-RES-13, UF-RES-14 |
| `LISTA_ESPERA` — `ListaEsperaStrategy` | Viabilidad explícita, admisibilidad de adjuntos, formulario habilitado tras viabilidad y partes por actor; invalidación por cambio de descripción; recepción/aprobación conjunta; fabricación o prestación; cierre con horas | RN-TIP-PLE-02, RN-TIP-PLE-03, RN-TIP-PLE-04, RN-TIP-PLE-05, RN-TIP-PLE-07, RN-TIP-PLE-08, RN-TIP-PLE-09; UF-RES-05 |

`ListaEsperaStrategy` no asigna recursos, no ocupa franjas y no registra entrega física. La gestión del archivo y su almacenamiento corresponde al caso de uso, mientras la estrategia decide su admisibilidad conforme al contrato.

Las estrategias de campus y externo reutilizan `PrestamoFisicoPolicy`. **Es una política compartida, no una sexta Strategy**: no se selecciona como tipo ni actúa como Context. Reúne compromiso único, condiciones del proceso de salida, inmutabilidad de FGL 030 y devolución completa. Las diferencias de campus y externo permanecen en sus estrategias.

## Políticas por responsabilidad

No se concentra el dominio en un archivo monolítico de reglas comunes. Las políticas son componentes internos, sin estado persistente propio; reutilizan reglas existentes y reciben datos preparados por el servicio.

| Política | Responsabilidad y referencias |
|---|---|
| `AccesoPolicy` | Propiedad, ámbito, cuenta y unidad; invocada por el servicio. RN-RES-02, RN-RES-11, RN-RES-15, RN-PRO-02, RN-PRO-06 |
| `ContextoPolicy` | Contexto obligatorio y relaciones válidas por tipo de cuenta. RN-CTX-01, RN-CTX-05, RN-CTX-08 |
| `ApoyoPolicy` | Derivación del apoyo obligatorio y solicitud voluntaria. RN-RES-09, RN-RES-10 |
| `HorarioPolicy` | Comprobaciones reutilizables de fecha y franja para los tipos que las utilizan. RN-HOR-01, RN-HOR-02, RN-HOR-03, RN-HOR-04, RN-HOR-06 |
| `DisponibilidadPolicy` | Evaluación común de incompatibilidades con datos vigentes, distinguiendo asignaciones temporales y compromisos físicos. RN-DIS-01, RN-DIS-04, RN-DIS-05, RN-DIS-06, RN-DIS-11 |
| `PropuestasPolicy` | Contraparte autorizada, vigencia y resolución; consulta a la estrategia para admisibilidad y revalidación por tipo. RN-PROP-01, RN-PROP-04, RN-PROP-05, RN-PROP-06, RN-PROP-07 |
| `PrestamoFisicoPolicy` | Comportamiento compartido exclusivamente por campus y externo. RN-RES-14, RN-DIS-06, RN-TIP-RC-07, RN-TIP-RE-07 |

No se redefine la autenticación, el inventario, la configuración de espacios ni las vinculaciones académicas que pertenecen a otros módulos. El servicio obtiene sus datos y respeta la propiedad descrita en las dependencias funcionales de Reservations. Tampoco se impone una transición universal: la estrategia determina las transiciones del tipo dentro de los estados globales existentes.

## Límites transaccionales

El servicio es dueño de la transacción; el repositorio participa en ella sin confirmar por separado. Las siguientes unidades corresponden a operaciones existentes:

- **Creación y edición:** cabecera, detalle y asociaciones se validan y escriben conjuntamente. Se mantienen cardinalidad, contexto, apoyo, disponibilidad y los efectos requeridos de la edición. Un error revierte el conjunto (RN-RES-08, RN-RES-12, RN-PRO-06, RN-DIS-05).
- **Compromiso físico y complementarios:** establecer el compromiso y retirar automáticamente los complementarios de espacios solicitados/aprobados es una sola transacción. Si un espacio afectado está en ejecución, se rechaza todo. La estrategia/política determina la consecuencia y el servicio coordina las reservas afectadas mediante el repositorio (RN-TIP-PE-28, UF-RES-23).
- **Retiro manual:** actualiza únicamente la composición vigente permitida; no genera historial específico ni metadatos de retiro. Se conservan intactas las filas históricas que proceden de retiros automáticos. No se extienden estas operaciones a campus, externo o lista de espera (RN-TIP-PE-21, RN-TIP-RI-10).
- **Propuestas:** aceptación y periodo resultante se guardan juntos después de revalidar; un fallo conserva también la propuesta. En aprobadas solo espacio e interno admiten reprogramación; la FGL de campus/externo impide alterar sus datos (RN-PROP-05).
- **Lista de espera:** recepción de material y aprobación son atómicas. También se mantienen juntas las invalidaciones de viabilidad/revisión por cambio de descripción y las horas con la finalización. La evaluación negativa conserva la unidad de rechazo y motivo definida por el contrato (RN-TIP-PLE-03, RN-TIP-PLE-05, RN-TIP-PLE-08, RN-TIP-PLE-09).
- **Salida física:** aprobación y generación de cabecera, actividades e ítems de FGL se confirman juntas. El contrato conserva la ruta de aprobación (§4.1) y la de ejecución (§6.1) dentro del mismo proceso de salida; no se mantienen transacciones de base abiertas entre peticiones o durante impresión y firma. La entrega física y el cambio a ejecución se registran juntos. El retiro por deshabilitación solo aplica antes de ese proceso; desde la salida la composición permanece fija hasta la devolución (RN-CAN-06, RN-TIP-RC-07, RN-TIP-RE-07).
- **Devolución:** todos los registros de devolución y el cierre se confirman en una operación. No hay devolución parcial ni liberación mediante un simple cambio de estado (RN-TIP-RC-10, RN-TIP-RE-10).
- **Transiciones horarias:** el servicio ejecuta la decisión de cada estrategia con el historial exigido. La aprobación de espacio dentro de su franja registra aprobación e inicio inmediato juntos. La disponibilidad temporal no depende de la puntualidad de ese proceso (RN-TIP-PE-25, RN-TIP-PE-27, RN-TIP-RI-08, RN-TIP-RI-09, RN-DIS-11).

La protección real frente a concurrencia corresponde a las restricciones y mecanismos de base descritos en el modelo. El bloqueo y la consulta previa del repositorio no sustituyen las garantías de exclusión temporal y compromiso físico único. El modelo y `database-status.md` identifican mecanismos todavía pendientes de implementación; este diseño no los declara instalados.

La transacción de base no convierte almacenamiento de adjuntos, correos o impresión en operaciones de base. El servicio respeta los resultados y fallos exigidos por el contrato, sin incorporar nuevos mecanismos persistentes ni una auditoría general.

## Correspondencia con contrato y pruebas

Todas las rutas mantienen el prefijo y los cuerpos del [contrato](../../contratos/reservations/api-contract.md). Los números de sección siguientes remiten a ese documento.

| Caso de uso | Contrato / flujo | Distribución |
|---|---|---|
| Crear y editar | §2.1, §2.8; UF-RES-01 a UF-RES-05, UF-RES-08, UF-RES-24 | Servicio y políticas comunes; Context delega detalle y condiciones del tipo |
| Viabilidad, formulario y adjuntos | §2.3 a §2.7; UF-RES-05 | Servicio y `ListaEsperaStrategy` |
| Consultar y disponibilidad | §2.2, §3; UF-RES-19 | Servicio, ámbito de acceso, política de disponibilidad y repositorio; sin mutaciones por GET |
| Aprobar y rechazar | §4.1, §4.2; UF-RES-07 | Servicio autoriza y coordina; estrategia determina condiciones y registros del tipo |
| Agregar/retirar | §4.3, §4.4; UF-RES-09, UF-RES-10 | Solo estrategias de espacio e interno, con sus roles y estados permitidos |
| Negociar periodo | §5; UF-RES-15 | Política de propuestas, estrategia y servicio transaccional |
| Ejecutar, finalizar y cancelar | §6; UF-RES-11, UF-RES-13, UF-RES-14 | Servicio más comportamiento del tipo; sin entrega/devolución para interno o espacio |
| Orden y PDF | §7; UF-RES-03, UF-RES-04 | Lectura de snapshots inmutables por el servicio; exportar no regenera la orden |
| Calendario, recordatorios y exportación | §8 y §10; UF-RES-16, UF-RES-17 | Servicio y dependencias existentes; no son responsabilidad de persistencia de una Strategy |
| Deshabilitación y horario | §10; UF-RES-12, UF-RES-21, UF-RES-22 | Entrada automática al servicio, con consecuencias específicas delegadas |

`TIPO_NO_ADMITIDO` corresponde a operaciones ajenas al tipo; `ESTADO_INCOMPATIBLE`, al estado; `SOLAPAMIENTO`, al conflicto temporal; `CONFLICTO`, a los supuestos de negocio expresos del contrato. El router conserva los códigos y el formato contractual; no expone excepciones SQL.

Las [pruebas actuales](tests.md) son los criterios de comportamiento: pruebas de servicio para reglas y efectos, de contrato para rutas/respuestas y de base para concurrencia e integridad. La separación en estrategias facilita verificar cada tipo, pero no sustituye ninguna prueba de contrato o de base.

## Organización propuesta

Rutas relativas al futuro paquete backend del módulo; no se crean con este documento:

```text
reservations/
├── router.py
├── schemas.py
├── service.py
├── repository.py
├── domain/
│   └── reserva.py
├── strategies/
│   ├── reservation_strategy.py
│   ├── selector.py
│   ├── espacio.py
│   ├── recurso_interno.py
│   ├── recurso_campus.py
│   ├── recurso_externo.py
│   └── lista_espera.py
└── policies/
    ├── acceso.py
    ├── contexto.py
    ├── apoyo.py
    ├── horario.py
    ├── disponibilidad.py
    ├── propuestas.py
    └── prestamo_fisico.py
```

No se añaden tablas, estados, operaciones HTTP ni requisitos funcionales. La implementación y las garantías de base pendientes continúan sujetas a sus documentos y tareas correspondientes.
