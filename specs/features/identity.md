# Identidad y roles

## Propósito

Este documento define las reglas de identidad del sistema: autenticación, usuarios, roles, permisos y asignación de gestores a espacios.

## Clasificación

- `Constraint`: regla obligatoria de seguridad, validación o autorización.
- `Suggestion`: comportamiento recomendado o configurable.
- `Open question`: decisión aún no definida.

## Usuarios

### Constraint: datos básicos

Un usuario debe tener:

- `username` entre 3 y 80 caracteres;
- `email` con formato válido;
- `password` de al menos 6 caracteres al recibirla;
- un rol válido.

El sistema almacena únicamente la contraseña cifrada mediante hash; nunca debe persistir la contraseña en texto plano.

Los roles permitidos son `usuario`, `gestor` y `admin`.

El nombre de usuario y el correo electrónico deben ser únicos.

### Constraint: administración de usuarios

- Solo un administrador puede listar usuarios.
- Solo un administrador puede crear usuarios desde el endpoint administrativo.
- Solo un administrador puede actualizar usuarios.
- Solo un administrador puede eliminar usuarios.
- No existe registro público de usuarios en el flujo actual.
- Al crear o actualizar, el rol debe pertenecer al catálogo permitido.
- Si un usuario deja de ser gestor, debe eliminarse su asignación de espacio.

## Autenticación

### Constraint

1. El usuario inicia sesión con `username` y `password`.
2. El sistema debe rechazar credenciales inválidas con `401 Unauthorized`.
3. El sistema genera un token de acceso firmado con la configuración JWT.
4. El token contiene el identificador del usuario (`sub`) y su rol (`rol` y `role`).
5. El token contiene una fecha de expiración.
6. Las rutas protegidas deben exigir un token Bearer válido.
7. El usuario identificado por el token debe existir en la base de datos.
8. Un token inválido, expirado o sin `sub` válido debe rechazarse.

La duración del token se controla mediante `ACCESS_TOKEN_EXPIRE_MINUTES`.

### Suggestion

Se recomienda implementar revocación o invalidación de tokens cuando se cambia la contraseña, se desactiva un usuario o se modifican sus permisos críticos.

## Roles

### `usuario`

Puede consultar su información, crear reservas autenticadas, consultar sus reservas, editar sus reservas pendientes, cancelar sus reservas aprobadas y consultar espacios, recursos y disponibilidad pública.

No puede administrar usuarios, gestionar espacios o recursos, gestionar reservas de otros usuarios ni eliminar reservas.

### `gestor`

Puede gestionar recursos, horarios y reservas dentro de su espacio asignado. También puede crear reservas y consultar la operación de ese espacio.

No puede administrar usuarios, gestionar espacios no asignados, manipular recursos de otros espacios ni modificar reservas fuera de su espacio.

Un gestor debe tener exactamente un espacio asignado en el modelo actual.

### `admin`

Puede administrar usuarios, crear, actualizar y eliminar espacios, gestionar recursos de cualquier espacio y gestionar reservas de cualquier espacio. No está limitado por una asignación de espacio.

## Asignación de gestores a espacios

### Constraint

1. Un gestor debe tener un espacio asignado para ejecutar operaciones de gestión.
2. La asignación debe apuntar a un espacio existente.
3. Un usuario que no sea gestor no debe conservar una asignación de espacio.
4. Un usuario solo puede tener una asignación de espacio en el modelo actual.
5. Si se cambia el espacio de un gestor, la asignación anterior debe reemplazarse.
6. Si se cambia un gestor a otro rol, la asignación debe eliminarse.

La relación se almacena en `usuarios_espacios` y tiene una restricción de unicidad sobre `usuario_id`.

### Suggestion

Si el negocio necesita que una persona gestione varios espacios, debe cambiarse la restricción de unicidad y la lógica de autorización antes de permitirlo.

## Protección de administradores

### Constraint

1. Un administrador no puede eliminar su propia cuenta administrativa.
2. Un administrador no puede cambiarse a sí mismo a otro rol.
3. El sistema debe conservar al menos un administrador.
4. No se puede eliminar o degradar al último administrador.
5. La comprobación del último administrador debe serializarse para evitar condiciones de carrera.

La implementación utiliza un bloqueo transaccional de PostgreSQL para serializar estas operaciones.

## Autorización

La autorización se basa en el usuario cargado desde la base de datos y su rol actual.

- `require_admin` permite exclusivamente el rol `admin`.
- `require_resource_manager` permite `admin` y `gestor`.
- Las operaciones de gestor verifican además el espacio asignado.
- Las operaciones de usuario verifican la propiedad de la reserva o entidad correspondiente.

No debe confiarse únicamente en el rol contenido en el token si el usuario pudo ser actualizado después de emitirlo.

## Contraseñas

### Constraint

- Las contraseñas recibidas deben cumplir la longitud mínima del schema.
- Las contraseñas deben almacenarse como hash.
- La autenticación debe comparar la contraseña proporcionada contra el hash almacenado.
- Las respuestas de usuario nunca deben incluir `hashed_password`.

### Suggestion

Se recomienda elevar la longitud mínima, exigir mayor complejidad y aplicar protección contra intentos repetidos de inicio de sesión.

## Correo electrónico y nombre de usuario

### Constraint

- El nombre de usuario no puede repetirse.
- El correo no puede repetirse.
- En los endpoints administrativos, el correo debe contener `@` y un dominio con punto.

### Open question

Debe definirse si la unicidad de username y email ignora mayúsculas y espacios. Por ejemplo, si `Admin` y `admin` deben considerarse el mismo usuario.

## Auditoría

Las operaciones administrativas sobre usuarios deben registrar creación, actualización, eliminación, cambio de rol y asignación o cambio de espacio.

El registro debe identificar al administrador ejecutor, al usuario afectado y la acción realizada.

## Reglas pendientes de decisión

1. ¿Se permitirá registro público de usuarios?
2. ¿Debe existir verificación de correo electrónico?
3. ¿Debe forzarse cambio de contraseña en el primer inicio de sesión?
4. ¿Debe existir recuperación de contraseña?
5. ¿Se requiere MFA para administradores?
6. ¿Debe permitirse que un gestor administre varios espacios?
7. ¿La desactivación de un usuario debe invalidar inmediatamente sus tokens?
8. ¿Debe existir un estado `activo/inactivo` para usuarios?
9. ¿Un gestor puede crear reservas aprobadas automáticamente en su espacio?
10. ¿Deben existir permisos más granulares que los tres roles actuales?
11. ¿La comparación de username y email debe ser case-insensitive?
12. ¿Debe aplicarse rate limiting al endpoint de login?
