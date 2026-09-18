# Reservas Parquei — Especificación del Producto

## 1. Visión del Producto

Reservas Parquei es una plataforma web para gestionar la reserva de laboratorios, espacios, equipos y otros recursos institucionales para Usuarios, Técnicos y Administradores. Resuelve la falta de un proceso centralizado y trazable para solicitar, aprobar, consultar y administrar reservas, evitando conflictos de horario y mejorando el uso de los recursos.

## 2. Usuarios y Casos de Uso

| Usuario | Descripción | Casos de uso |
|---|---|---|
| Usuario | Estudiante, docente, investigador o colaborador que utiliza laboratorios, espacios, equipos y otros recursos. | 1. Consulta recursos disponibles 2. Crea solicitudes 3. Consulta sus estados 4. Cancela cuando corresponde 5. Recibe notificaciones 6. Gestiona su cuenta 7. Selecciona tipo, contexto y recursos 8. Responde propuestas de horario del Técnico |
| Técnico | Personal que administra reservas y recursos únicamente dentro de su propia unidad organizacional. | 1. Consulta las solicitudes de su unidad 2. Aprueba, rechaza o modifica solicitudes indicando el motivo 3. Configura horarios y reglas de reserva 4. Administra espacios, mobiliarios y otros recursos de su unidad 5. Visualiza y descarga informes de su unidad 6. Propone horarios alternativos y resuelve contrapropuestas 7. Edita solicitudes conforme a las reglas aplicables 8. Administra catálogos de su unidad |
| Secundario: administrador institucional | Usuario con permisos globales para gestionar la configuración general, usuarios, unidades organizacionales y permisos del sistema. | 1. Administra usuarios y cuentas 2. Gestiona unidades, cargos y perfiles 3. Configura permisos y accesos 4. Consulta la actividad general del sistema 5. Supervisa la configuración global de reservas 6. Visualiza y descarga informes de ocupación por laboratorios, espacios, recursos, proyectos, tipos de usuarios o semilleros 7. Consulta el historial y control de cambios 8. Promueve una cuenta a personal administrativo o la degrada de vuelta, sin perder su historial 9. Administra unidades organizacionales, cargos, personal institucional y equipos con jerarquía propia 10. Importa masivamente el inventario institucional de equipos desde una planilla |

## 3. Funcionalidades

### Solicitudes de reserva

- El usuario puede consultar los espacios, equipos y recursos disponibles.
- El usuario puede crear una solicitud seleccionando el tipo de reserva, los datos temporales que ese tipo exija, el número de asistentes, el contexto que la justifica (proyecto, semillero, pasantía, trabajo de grado o actividad institucional) y los recursos requeridos.
- El sistema valida los datos de la solicitud y registra su estado inicial.
- El usuario indica si la reserva es dentro o fuera del laboratorio; si es fuera, debe indicar la ubicación de uso.
- Una misma solicitud puede combinar un espacio, varios recursos del inventario institucional.
- **Fuera de alcance:** agrupar varias fechas u horarios distintos en una sola solicitud (reserva multi-día). Cada fecha u horario requiere su propia solicitud.
- El usuario puede agregar acompañantes a la reserva.
- Si algún recurso incluido lo exige, la solicitud queda marcada automáticamente como "requiere apoyo del auxiliar/técnico".
- El sistema garantiza a nivel de base de datos, no solo de aplicación, que dos solicitudes concurrentes nunca reserven el mismo recurso en el mismo horario.

### Gestión y aprobación

- El Técnico puede consultar, aprobar, editar, rechazar o cancelar solicitudes de su unidad.
- El sistema evita solicitudes con horarios inválidos y aplica las reglas de uso configuradas.
- El Técnico puede proponer un horario alternativo en vez de rechazar directamente; el Usuario lo acepta, lo rechaza o contrapropone otro, sin que la solicitud pase por "rechazada" mientras dura la negociación.
- El Técnico puede editar una solicitud ya aprobada conforme a las reglas aplicables, dentro de su unidad.

## Gestión por tipo de reserva 
 ## #1 - Gestión de reservas por espacios
        -  El Técnico puede consultar, aprobar, editar, rechazar o cancelar solicitudes de su unidad.
        - El sistema evita solicitudes con horarios inválidos y aplica las reglas de uso configuradas.
        - El Técnico puede proponer un horario alternativo; el Usuario lo acepta, lo rechaza o contrapropone otro.
        - El Técnico puede editar una solicitud ya aprobada conforme a las reglas aplicables dentro de su unidad.
        - El usuario puede cancelar una reserva en cualquier estado, dejando su trazabilidad.
        - El usuario solo puede editar una reserva en estado pendiente de aprobación.
        - El usuario puede seleccionar los recursos dentro del espacio.
        - El sistema genera reportes para el Técnico de la unidad y el Administrador.
## #2 - Gestión de reservas en el campus (fuera del laboratorio).
        - El Técnico puede consultar, aprobar, editar, rechazar o cancelar solicitudes de su unidad.
        - El sistema evita solicitudes con horarios inválidos y aplica las reglas de uso configuradas.
        - El Técnico puede proponer un horario alternativo; el Usuario lo acepta, lo rechaza o contrapropone otro.
        - El Técnico puede editar una solicitud ya aprobada conforme a las reglas aplicables dentro de su unidad.
        - El usuario puede cancelar una reserva en cualquier estado, dejando su trazabilidad.
        - El sistema debe generar un formato de salida diligenciado - Para salida dentro del campus.
## #3 - Gestión de reservas en fuera del campus
        - El Técnico puede consultar, aprobar, editar, rechazar o cancelar solicitudes de su unidad.
        - El sistema evita solicitudes con horarios inválidos y aplica las reglas de uso configuradas.
        - El Técnico puede proponer un horario alternativo; el Usuario lo acepta, lo rechaza o contrapropone otro.
        - El Técnico puede editar una solicitud ya aprobada conforme a las reglas aplicables dentro de su unidad.
        - El usuario puede cancelar una reserva en cualquier estado, dejando su trazabilidad.
        - El sistema debe generar un formato de salida diligenciado FGL 030 - Para salida FUERA DEL CAMPUS.
## #4 - Lista de espera 
        - El Técnico puede consultar, aprobar, editar, poner en ejecución, finalizar,
        rechazar o cancelar solicitudes.
        - El usuario debe registrar el requerimiento.
        - El usuario puede adjuntar un archivo para su requerimiento. (LIMITE 5 MB).
        - El Técnico selecciona la siguiente reserva aprobada según prioridad o criterios operativos, conforme a RN-TIP-PLE-06.
        - El Técnico registra las horas empleadas al finalizar la ejecución, conforme a RN-TIP-PLE-08.
        - El sistema debe generar el informe de uso por horas de la maquina seleccionada.


### Administración de recursos

- El administrador puede crear, editar, habilitar o deshabilitar espacios, equipos, mobiliarios y otros recursos.
- El Técnico puede crear, editar, habilitar o deshabilitar mobiliarios y otros recursos dentro de su unidad.
- El sistema permite configurar horarios de atención, modalidad de reserva, anticipación requerida y aprobación automática.
- El administrador puede importar masivamente el inventario institucional de equipos desde una planilla, sin duplicar registros ya importados.
- Cada recurso puede marcarse como "prestación de servicio" y llevar un identificador de placa de inventario.

### Usuarios y trazabilidad

- El administrador puede gestionar usuarios, cuentas, perfiles, unidades organizacionales y permisos.
- El sistema registra notificaciones y un historial de cambios asociados a las operaciones relevantes.
- Un usuario puede autorregistrarse sin invitación previa y, en su primer ingreso, debe completar sus datos obligatorios y seleccionar al menos una vinculación académica o investigativa activa y válida. Los proyectos y semilleros se seleccionan del catálogo administrado por Researchs; después puede recuperar su contraseña de forma autónoma.
- El administrador puede invitar cuentas, reenviar una invitación no completada, y promover o degradar a una persona entre reservista y personal administrativo sin perder su historial.
- El sistema nunca elimina ni degrada la última cuenta con permisos de administrador.
- Las notificaciones se envían tanto dentro de la aplicación como por correo (confirmación, aprobación, rechazo, cancelación, recordatorio antes de la reserva y confirmación con archivo de calendario `.ics`), y cada persona puede optar por no recibir el correo (la notificación dentro de la app no se apaga).

### Datos maestros institucionales

- El administrador administra unidades organizacionales (con jerarquía de unidad padre/hijas), cargos asociados a una unidad, y personal institucional asociado a un cargo.
- El administrador administra equipos institucionales asociados a una unidad, con su estado operativo, calibración y mantenimiento.
- Un equipo institucional puede incluirse en una reserva como un recurso más, siempre que esté operativo.
- Dar de baja personal o un equipo es lógico (queda inactivo), nunca se borra si tiene historial asociado.

### Reportes

- El Técnico puede exportar información de su unidad y el Administrador puede exportar información de cualquier unidad, en CSV o Excel.
- Los informes se pueden filtrar/agrupar por laboratorio, espacio, recurso, proyecto y semillero.

### Estados

- El sistema muestra el estado de la solicitud: pendiente, aprobada, rechazada o cancelada.
- El sistema muestra estados de carga, confirmación, vacío y error durante las operaciones.
- El sistema informa cuando no existen recursos disponibles o solicitudes pendientes.
- El personal institucional y los equipos del inventario institucional usan un estado activo/inactivo como baja lógica.

### Fuera del alcance

- No incluye la gestión de pagos o cobros por las reservas.
- No incluye la compra, inventario contable o mantenimiento financiero de los recursos.
- No incluye reservas realizadas fuera de los recursos y unidades configurados en la plataforma.

## 4. Flujos de Usuario

### Flujo principal — Solicitar una reserva

1. El solicitante inicia sesión y accede al módulo de reservas.
2. Consulta los espacios, equipos y recursos disponibles para su unidad.
3. Selecciona la fecha, el horario, el tipo de uso, el espacio, el proyecto y el semillero del catálogo, además de los recursos requeridos.
4. Completa los asistentes, el motivo de la solicitud y la ubicación cuando corresponda.
5. Envía la solicitud y el sistema valida los datos y registra la reserva en estado pendiente.
6. El sistema muestra la confirmación y notifica al solicitante que la solicitud fue recibida.
7. El solicitante consulta posteriormente el estado de la solicitud desde su historial.

### Flujo de error

1. Si faltan datos obligatorios o el horario no es válido, el sistema muestra los campos que debe corregir.
2. Si el recurso no está disponible o existe un conflicto de horario, el sistema informa el conflicto y solicita seleccionar otra fecha, hora o recurso.
3. Si falla la comunicación con el servidor, el sistema muestra: “No pudimos registrar la solicitud. Inténtalo de nuevo.”
4. La solicitud no se crea hasta que la validación finaliza correctamente.

### Flujo secundario — Aprobar o rechazar una solicitud

1. El Técnico inicia sesión y accede a las solicitudes pendientes de su unidad.
2. Selecciona una solicitud y revisa sus datos, recursos y horario.
3. Elige “Aprobar” o “Rechazar”; si rechaza, registra el motivo.
4. El sistema actualiza el estado, registra el cambio y genera una notificación para el solicitante.
5. El solicitante consulta el nuevo estado desde su historial.

### Flujo secundario — Cancelar una reserva

1. El solicitante abre una reserva propia que todavía puede cancelarse.
2. Selecciona “Cancelar” y confirma la operación.
3. El sistema cambia el estado a cancelada, libera la disponibilidad y registra la acción.
4. El sistema notifica el cambio a los usuarios involucrados.

### Flujo secundario — Proponer y resolver un horario alternativo

1. El Técnico abre una solicitud pendiente y, en vez de rechazarla, propone un horario alternativo con un motivo.
2. El sistema notifica al solicitante.
3. El solicitante acepta el horario propuesto, lo rechaza, o contrapropone otro horario con su propio motivo.
4. Si contrapone, el Técnico recibe el aviso y puede aceptar o rechazar esa contrapropuesta.
5. Al aceptarse cualquiera de las dos propuestas, el sistema revalida disponibilidad, capacidad y horario, y reprograma la reserva; al rechazarse, la reserva queda pendiente con su horario original.

### Flujo secundario — Solicitar fabricación o prestación en lista de espera

1. El Usuario registra la necesidad y, cuando corresponda, adjunta un archivo técnico, sin seleccionar fecha ni horario de ejecución.
2. El Técnico evalúa la viabilidad; si es viable, se habilita el formulario complementario.
3. Tras completar las aprobaciones requeridas y registrar la recepción del material, la reserva pasa a `APROBADA`.
4. El Técnico selecciona la siguiente reserva según RN-TIP-PLE-06 e inicia su ejecución.
5. Al finalizar, el Técnico registra las horas empleadas y el sistema notifica los cambios de estado conforme a Notifications.

El detalle se define en [UF-RES-05](../modules/reservations/user-flows.md#uf-res-05--crear-reserva-tipo-lista-de-espera). No se establece una cola de liberación de cupos ni un plazo de confirmación por turno.

### Flujo secundario — Administrar datos maestros institucionales

1. El administrador crea una unidad organizacional, opcionalmente bajo otra unidad padre.
2. Da de alta cargos dentro de esa unidad, y personal institucional dentro de un cargo.
3. Da de alta equipos dentro de una unidad, con sus datos de calibración y mantenimiento.
4. Da de baja (lógica) personal o equipos que ya no correspondan, sin afectar el historial de reservas que ya los incluyeron.

### Flujo secundario — Autorregistro y recuperación de contraseña

1. Una persona sin cuenta se autorregistra con correo, contraseña y los datos obligatorios de RN-DAT de Usuarios: nombre, documento, teléfono, institución y dependencia. En el primer ingreso revisa sus datos y completa las vinculaciones requeridas.
2. Si olvida su contraseña, pide un enlace de recuperación; el sistema responde igual exista o no una cuenta con ese correo, y si existe, envía el enlace por correo.
3. Al completar el cambio, el sistema le confirma por correo que su contraseña fue actualizada.

### Flujo secundario — Exportar un reporte

1. El Técnico filtra la vista de su unidad o el Administrador la vista global que necesita.
2. Elige el formato (CSV o Excel) y descarga el archivo con exactamente los datos que tenía filtrados en pantalla.

## 5. Arquitectura

| Componente | Tecnología | Función |
|---|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS y Recharts | Presenta la interfaz web, las vistas de reservas, administración y consulta de estados. Reenvía las solicitudes `/api/*` al backend. |
| Backend | FastAPI, Python, SQLAlchemy, Pydantic y Uvicorn | Expone la API, autentica usuarios, valida solicitudes, aplica reglas de negocio y gestiona reservas, recursos y notificaciones. |
| Base de datos | PostgreSQL 13 | Almacena usuarios, cuentas, unidades organizacionales, recursos, reservas, estados, notificaciones y control de cambios. También protege la integridad de las reservas concurrentes. |
| Servicio externo | Ninguno requerido para el flujo principal | La aplicación funciona con sus componentes internos. pgAdmin puede utilizarse opcionalmente para administrar la base de datos. |
| Deploy | Docker y Docker Compose | Ejecuta y conecta los contenedores de frontend, backend y PostgreSQL en una red interna. |

### Flujo de datos

```text
Usuario → Next.js (React) → FastAPI → PostgreSQL → FastAPI → Next.js → Usuario
```

## 6. Requisitos No Funcionales

### Rendimiento

- Las operaciones habituales de consulta, creación y actualización deben responder en menos de 2 segundos bajo la carga inicial prevista, excluyendo problemas de red del cliente.
- El sistema debe mantener la validación de disponibilidad y evitar reservas superpuestas incluso cuando existan solicitudes concurrentes.

### Seguridad

- El acceso a las funciones protegidas debe requerir autenticación JWT y autorización según el rol y la unidad organizacional del usuario.
- Las contraseñas deben almacenarse mediante hash seguro con bcrypt y las claves de firma y credenciales deben gestionarse mediante variables de entorno, nunca en el código fuente.
- Los datos personales y las operaciones administrativas deben quedar protegidos y registrados en el control de cambios cuando corresponda.

### Accesibilidad

- La interfaz debe ser usable en móvil, tablet y desktop, y funcionar en las versiones recientes de Chrome, Firefox, Safari y Edge.
- Los formularios, botones, mensajes de error y estados de carga deben ser comprensibles y navegables mediante teclado.

### Fuera del alcance (v1)

- No incluye aplicaciones móviles nativas para Android o iOS.
- No incluye pagos, cobros ni facturación asociados a las reservas.
- No incluye integración con calendarios externos; solo genera y adjunta un archivo `.ics` al correo de confirmación cuando se aprueba una reserva — ver Funcionalidades → Usuarios y trazabilidad. Tampoco incluye soporte multiidioma.
