# Investigación — Researchs

Contrato funcional del dominio `investigacion`, alojado en el módulo `researchs`.

`investigacion` es dueño del contexto académico/investigativo y de las vinculaciones del usuario. `reservas` únicamente registra cuáles de esos contextos justificaron la reserva y conserva su información histórica.

## Reglas de investigación — RN-INV

- **RN-INV-01:** Un usuario puede estar vinculado a múltiples proyectos y semilleros.
- **RN-INV-02:** Una pasantía debe registrar universidad de procedencia, nombre del docente responsable en el ITM y correo del docente.
- **RN-INV-03:** Un trabajo de grado debe registrar nombre y correo del director.
- **RN-INV-04:** Las vinculaciones de usuarios con proyectos, semilleros, pasantías y trabajos de grado pueden estar activas o inactivas.
- **RN-INV-05:** La desactivación de una vinculación no elimina su historial.
- **RN-INV-06:** `proyectos` y `semilleros` son catálogos administrados centralmente; sus códigos e identidades son persistentes y no pueden crearse ni modificarse desde el perfil del Usuario ni desde una reserva.
- **RN-INV-07:** El Usuario solo puede seleccionar proyectos y semilleros existentes del catálogo y solicitar o mantener una vinculación válida conforme a las reglas de `investigacion`.
- **RN-INV-08:** Las vinculaciones académicas o investigativas son declaradas por el Usuario bajo su responsabilidad. El sistema verifica que la entidad seleccionada exista, esté habilitada y que la vinculación esté activa, pero no acredita la pertenencia institucional del Usuario. Los proyectos y semilleros se seleccionan exclusivamente de los catálogos administrados; no pueden crearse desde el perfil.
- **RN-INV-09:** El Usuario puede crear, desactivar y reactivar únicamente sus propias vinculaciones. El Técnico no administra vinculaciones de Usuarios.
- **RN-INV-10:** El Administrador con alcance global puede gestionar las vinculaciones de cualquier Usuario e intervenir administrativamente sobre sus pasantías, trabajos de grado y demás contextos propios. Esta facultad no corresponde al Técnico.
- **RN-INV-11:** Cuando ya exista una vinculación inactiva entre un Usuario y la misma entidad, reactivarla actualiza esa misma relación; no se crea una fila duplicada.

### Perfiles académicos e investigativos

- **RN-INV-12:** Los perfiles académicos o investigativos se gestionan mediante los identificadores persistentes del catálogo `investigacion.perfiles`; no se determinan mediante valores fijos en la aplicación.
- **RN-INV-13:** Asignar o retirar un perfil no modifica retroactivamente el contexto registrado en operaciones históricas.
- **RN-INV-14:** Un perfil deshabilitado no puede asignarse en nuevas operaciones mientras permanezca inactivo. Desactivar un perfil conserva las asociaciones existentes conforme a `RN-INV-05`.
- **RN-INV-15:** Solo un Administrador con alcance global puede crear, modificar, habilitar o desactivar perfiles del catálogo. El Técnico no lo administra, en línea con `RN-INV-10` y `RN-ACT-04`.
- **RN-INV-16:** El Usuario gestiona únicamente sus propios perfiles y solo puede asociarse a perfiles habilitados del catálogo. Tener un perfil no concede permisos administrativos ni sustituye una vinculación académica o investigativa a un proyecto, semillero, pasantía o trabajo de grado.

En esta especificación, una «vinculación válida» es una vinculación declarada que cumple las condiciones de RN-INV-08 dentro de la aplicación. Esta definición se aplica a la actualización del perfil, la creación de reservas y la selección de acompañantes; no supone consulta a una fuente institucional ni certificación externa de pertenencia.

## Actividades institucionales — RN-ACT

- **RN-ACT-01:** Una actividad institucional debe registrar `nombre` y `dependencia`.
- **RN-ACT-02:** Solo una actividad institucional con `estado = true` puede utilizarse en una nueva reserva.
- **RN-ACT-03:** Desactivar una actividad institucional no elimina su registro ni las referencias históricas de reservas existentes.
- **RN-ACT-04:** Las actividades institucionales solo pueden ser creadas, modificadas, activadas o desactivadas por un Administrador con alcance global. El Técnico no las administra.

## Relación con reservas

Las reglas [RN-CTX](../reservations/business-rules.md#contexto-de-la-reserva--rn-ctx) determinan qué combinaciones de contexto admite una reserva. Researchs proporciona las entidades, las actividades activas y las vinculaciones activas y válidas del usuario para su selección. Administration puede cargar proyectos y semilleros mediante el flujo autorizado de importación, pero no duplica sus tablas ni su propiedad funcional. Una vinculación académica o investigativa no concede permisos administrativos sobre reservas.

Desactivar una vinculación conserva su registro y las referencias históricas existentes; no modifica retroactivamente el contexto de reservas anteriores.

## Documentación relacionada

- [Overview del módulo](overview.md).
- [Modelo de datos de investigación](data-model.md).
- [Modelo general](../../docs/data-model.md#schema-investigacion).
