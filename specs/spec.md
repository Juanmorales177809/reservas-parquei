# Reservas Parquei — Especificación del Producto

## 1. Visión del Producto

Reservas Parquei es una plataforma web para gestionar la reserva de laboratorios, espacios, equipos y otros recursos institucionales para estudiantes, docentes, investigadores y personal autorizado. Resuelve la falta de un proceso centralizado y trazable para solicitar, aprobar, consultar y administrar reservas, evitando conflictos de horario y mejorando el uso de los recursos.

## 2. Usuarios y Casos de Uso

| Usuario | Descripción | Casos de uso |
|---|---|---|
| Principal: solicitante | Estudiante, docente, investigador o colaborador autorizado que necesita utilizar un laboratorio, espacio, equipo u otro recurso institucional. | 1. Consulta los espacios y recursos disponibles 2. Crea una solicitud de reserva indicando fecha, horario, asistentes, proyecto, semillero, motivo y recursos requeridos 3. Consulta el estado de sus solicitudes 4. Cancela una reserva cuando corresponde 5. Recibe notificaciones sobre cambios de estado |
| Secundario: gestor de reservas | Persona responsable de administrar los recursos de una unidad o laboratorio y revisar las solicitudes recibidas. | 1. Consulta las solicitudes pendientes 2. Aprueba, rechaza o modifica solicitudes indicando el motivo 3. Configura horarios y reglas de reserva 4. Administra espacios, equipos, tipos de reserva, mobiliarios y otros recursos 5. Consulta el historial y control de cambios 6. Visualiza y descarga informes de ocupación del laboratorio que administra por proyectos, semilleros, recursos, laboratorios o espacios |
| Secundario: administrador institucional | Usuario con permisos globales para gestionar la configuración general, usuarios, unidades organizacionales y permisos del sistema. | 1. Administra usuarios y cuentas 2. Gestiona unidades, cargos y perfiles 3. Configura permisos y accesos 4. Consulta la actividad general del sistema 5. Supervisa la configuración global de reservas 6. Visualiza y descarga informes de ocupación por laboratorios, espacios, recursos, proyectos o semilleros 7. Consulta el historial y control de cambios |

## 3. Funcionalidades

### Solicitudes de reserva

- El usuario puede consultar los espacios, equipos y recursos disponibles.
- El usuario puede crear una solicitud indicando fecha, horario, asistentes, proyecto, semillero, motivo y recursos requeridos.
- El sistema valida los datos de la solicitud y registra su estado inicial.

### Gestión y aprobación

- El gestor puede consultar, aprobar, editar, rechazar o cancelar solicitudes.
- El sistema evita solicitudes con horarios inválidos y aplica las reglas de uso configuradas.

### Administración de recursos

- El administrador puede crear, editar, habilitar o deshabilitar espacios, equipos, mobiliarios y otros recursos.
- El gestor puede crear, editar, habilitar o deshabilitar mobiliarios y otros recursos.
- El sistema permite configurar horarios de atención, modalidad de reserva, anticipación requerida y aprobación automática.

### Usuarios y trazabilidad

- El administrador puede gestionar usuarios, cuentas, perfiles, unidades organizacionales y permisos.
- El sistema registra notificaciones y un historial de cambios asociados a las operaciones relevantes.

### Estados

- El sistema muestra el estado de la solicitud: pendiente, aprobada, rechazada o cancelada.
- El sistema muestra estados de carga, confirmación, vacío y error durante las operaciones.
- El sistema informa cuando no existen recursos disponibles o solicitudes pendientes.

### Fuera del alcance

- No incluye la gestión de pagos o cobros por las reservas.
- No incluye la compra, inventario contable o mantenimiento financiero de los recursos.
- No incluye reservas realizadas fuera de los recursos y unidades configurados en la plataforma.

## 4. Flujos de Usuario

### Flujo principal — Solicitar una reserva

1. El solicitante inicia sesión y accede al módulo de reservas.
2. Consulta los espacios, equipos y recursos disponibles para su unidad.
3. Selecciona la fecha, el horario, el tipo de uso, el espacio, el proyecto, el semillero y los recursos requeridos.
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

1. El gestor inicia sesión y accede a las solicitudes pendientes de su unidad.
2. Selecciona una solicitud y revisa sus datos, recursos y horario.
3. Elige “Aprobar” o “Rechazar”; si rechaza, registra el motivo.
4. El sistema actualiza el estado, registra el cambio y genera una notificación para el solicitante.
5. El solicitante consulta el nuevo estado desde su historial.

### Flujo secundario — Cancelar una reserva

1. El solicitante abre una reserva propia que todavía puede cancelarse.
2. Selecciona “Cancelar” y confirma la operación.
3. El sistema cambia el estado a cancelada, libera la disponibilidad y registra la acción.
4. El sistema notifica el cambio a los usuarios involucrados.

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
- No incluye integración con calendarios externos ni soporte multiidioma.
