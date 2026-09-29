# Especificación funcional de pantallas — Notifications

## Alcance y fuentes

Derivado exclusivamente de [user-flow.md](user-flow.md), [business-rules.md](business-rules.md), [data-model.md](data-model.md) y [overview.md](overview.md). La navegación se detalla en [screen-flow.md](screen-flow.md). Los identificadores corresponden a superficies funcionales; no prescriben páginas independientes, rutas HTTP ni componentes.

No se amplían reglas, datos, contratos ni flujos. Los estados de procesamiento describen la espera del resultado de una acción existente, no operaciones nuevas. No se especifican estilos, disposición visual, textos literales de error ni códigos API.

**Fuera de alcance de este documento:** la generación de eventos (la origina cada módulo productor); el estado de los envíos de correo (no se consulta desde aquí); las plantillas editables (el texto vive en el código, `RN-CNT-06`).

## Criterios comunes

- **Actor:** cualquier cuenta autenticada y activa; todo opera sobre la cuenta de la sesión, sin identificador de cuenta enviado (`RN-CON-01`).
- **Backend:** marca lectura y guarda preferencias sin tocar reservas, recursos ni envíos (`RN-EST-04`, `RN-COR-05`).
- **Contenido histórico:** título y cuerpo son lo comunicado, no se recalculan (`RN-HIS-03`, `RN-CNT-04`).
- **Canales independientes:** in-app y correo derivan del mismo evento con ciclos separados (`RN-COR-05`).

## SCR-NOT-01 — Bandeja de notificaciones

- **User Flow de origen:** `UF-NOT-01`.
- **Actor:** cualquier cuenta autenticada.
- **Objetivo:** consultar las notificaciones propias y marcarlas como leídas.
- **Precondiciones:** cuenta autenticada y activa.
- **Información visible:** tipo de evento, fecha y hora, estado de lectura y referencia relacionada cuando exista; filtros por estado y tipo.
- **Entradas:** filtros; acción de marcar como leída sobre una notificación propia.
- **Acciones:** filtrar y paginar; marcar como leída.
- **Validaciones visibles:** solo las propias (`RN-CON-01`); consultar no modifica nada (`RN-CON-04`).
- **Estados:** consultando, listado con paginación, marcando, marcada con instante.
- **Errores y respuestas:** ajena o inexistente indistinguibles (`404`); marcar no altera reserva, recurso ni envío (`RN-EST-04`); repetir sobre leída conserva el instante.
- **Resultado/navegación:** permanece; la entidad desactivada después sigue apareciendo (`RN-HIS-02`); sin purga (`RN-HIS-01`).
- **Backend:** filtra por cuenta destinataria, ordena cronológicamente (`RN-CON-03`), registra `leida_at`.
- **RN/SEC relacionadas:** `RN-CON-01`, `RN-CON-02`, `RN-CON-03`, `RN-CON-04`; `RN-EST-01`, `RN-EST-02`, `RN-EST-03`, `RN-EST-04`, `RN-EST-05`; `RN-HIS-01`, `RN-HIS-02`, `RN-HIS-03`, `RN-HIS-04`.
- **Dependencias:** módulos productores, que originan los eventos.

## SCR-NOT-02 — Preferencias de correo

- **User Flow de origen:** `UF-NOT-02`.
- **Actor:** cualquier cuenta autenticada.
- **Objetivo:** ver y fijar la preferencia general y las preferencias por tipo de evento.
- **Precondiciones:** cuenta autenticada y activa.
- **Información visible:** preferencia general (por defecto si no existe) y preferencias explícitas por tipo.
- **Entradas:** habilitación general; habilitación por tipo de evento.
- **Acciones:** guardar preferencias (reemplazo completo).
- **Validaciones visibles:** la más específica prevalece (`RN-PREF-04`); solo canal correo (`RN-PREF-01`); la unidad deshabilitada bloquea aunque el individuo habilite (`RN-PREF-02`); auth ignora preferencias (`RN-PREF-03`).
- **Estados:** consultando, captura, guardando, confirmación.
- **Errores y respuestas:** tipo inexistente o deshabilitado → corrección; tipo repetido → corrección.
- **Resultado/navegación:** permanece; lo no listado se rige por la general.
- **Backend:** valida tipos vigentes, reemplaza el conjunto, conserva historial implícito por reemplazo.
- **RN/SEC relacionadas:** `RN-PREF-01`, `RN-PREF-02`, `RN-PREF-03`, `RN-PREF-04`.
- **Dependencias:** `resources`, propietaria del flag por unidad.

## Cobertura de todos los User Flows

| User Flow revisado | Superficie |
|---|---|
| UF-NOT-01 | SCR-NOT-01 |
| UF-NOT-02 | SCR-NOT-02 |
| UF-NOT-03 | Sin pantalla propia: tarea programada del sistema |

## Ambigüedades y límites de las fuentes

1. **Presentación del tipo de evento:** se muestra código y nombre del catálogo; no se define icono ni color propio.
2. **Destino tras marcar o guardar:** ningún flujo lo fija. No se decide aquí.
3. **Retornos al abandonar no fijados por las fuentes:** no se agregan botones de retorno o cancelación.
4. **Orden del listado:** cronológico descendente según el contrato; no se ofrece otro orden.

## Decisiones aplicadas a las ambigüedades de prioridad alta

- Bandeja y preferencias son dos superficies separadas porque tienen actores de lectura distintos en la práctica (toda cuenta lee su bandeja; la preferencia es configuración) aunque el actor formal coincida.
- `UF-NOT-03` queda explícitamente sin superficie por ejecutarlo una tarea programada sin iniciador humano.
- El estado de los envíos no tiene superficie en este módulo por decisión explícita del contrato.

## Documentos relacionados

- [Flujos de usuario](user-flow.md): los tres flujos (uno sin iniciador humano) que originan estas pantallas.
- [Reglas de negocio](business-rules.md): `RN-CON`, `RN-EST`, `RN-PREF`, `RN-COR`, `RN-HIS`, `RN-CNT`.
- [Modelo de datos](data-model.md): eventos, notificaciones, envíos y preferencias.
- [Navegación funcional](screen-flow.md): cómo se conectan estas dos superficies entre sí y con reservations, resources y auth.
