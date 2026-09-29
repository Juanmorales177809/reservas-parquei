# Usuarios

## Propósito

Administrar las identidades funcionales de las personas que operan el sistema: el reservista en `usuarios.usuarios` y el personal institucional en `personal.personal`. Define quién es cada persona ante el sistema, con independencia de cómo se autentica.

## Alcance

El módulo cubre:

- la identidad funcional del Usuario y sus datos obligatorios;
- la identidad del personal institucional y su vínculo con un cargo;
- la actualización inicial del perfil y su condición de completitud;
- la orquestación del perfil cuando requiere información de otros dominios.

## Responsabilidades

- Registrar y mantener los datos obligatorios del Usuario definidos en `RN-DAT`: nombre, documento, teléfono, institución y dependencia.
- Garantizar la unicidad de documento y teléfono entre todos los registros, incluidos los inactivos.
- Marcar mediante `perfil_actualizado_at` cuándo el Usuario completó su actualización inicial, y mantenerla pendiente mientras falte un dato obligatorio o una vinculación válida.
- Orquestar el completado del perfil, consultando a `researchs` las vinculaciones académicas o investigativas sin asumir su validación.
- Conservar la información histórica al deshabilitar una identidad, sin eliminarla.

## Conceptos propios

- Identidad funcional del Usuario.
- Identidad del personal institucional.
- Datos obligatorios del perfil.
- Actualización inicial del perfil.

## Dependencias

- **Auth** administra la cuenta, las credenciales y la sesión. Una cuenta apunta a exactamente una de las dos identidades de este módulo, nunca a ambas (`RN-AUTH-ID-03`). Auth consulta la condición de actualización inicial para aplicar `RN-AUTH-SES-04`, pero no la administra.
- **Researchs** administra proyectos, semilleros, pasantías, trabajos de grado y las vinculaciones del usuario. Este módulo las consume para determinar si el perfil está completo; no las crea ni decide su validez.
- **Administration** gestiona cargos y unidades, y puede administrar estas identidades mediante operaciones autorizadas sin duplicar su modelo.
- **Reservations** utiliza la identidad y la condición del perfil para permitir o impedir la creación de reservas (`RN-RES-11`).

## Fuera de alcance

- Credenciales, sesiones, tokens y decisiones de autorización.
- Creación o validación de entidades académicas e investigativas.
- Reglas del ciclo de vida de una reserva.
- Concesión de permisos administrativos: tener identidad o vinculación no otorga ninguno (`RN-AUTH-ROL-04`).

## Documentación relacionada

- [Reglas de negocio](business-rules.md): `RN-USR` y `RN-DAT`.
- [Modelo de datos](data-model.md): `usuarios.usuarios` y `personal.personal`.
- [Flujos de usuario](user-flow.md): alta, actualización inicial y mantenimiento del perfil.
- [Especificación de pantallas](screens.md), [wireframes](wireframes.md) y [navegación funcional](screen-flow.md): las cinco superficies de autoservicio del perfil.
