# Autenticación y autorización

El módulo `auth` administra las cuentas, credenciales, sesiones y decisiones de autorización. Las identidades funcionales se encuentran en `usuarios.usuarios` y `personal.personal`; una cuenta corresponde exactamente a una de ellas.

## Cuentas e identidades — RN-AUTH-ID

- **RN-AUTH-ID-01:** Toda operación autenticada requiere una cuenta activa.
- **RN-AUTH-ID-02:** El correo electrónico es único y sirve para identificar la cuenta.
- **RN-AUTH-ID-03:** Una cuenta debe estar vinculada a `usuarios.usuarios` o a `personal.personal`, nunca a ambas.
- **RN-AUTH-ID-04:** La restricción de exclusividad se conserva mediante `ck_auth_cuentas_identidad` y las restricciones únicas de las referencias de identidad.
- **RN-AUTH-ID-05:** Desactivar una cuenta o identidad impide nuevas operaciones autenticadas, sin eliminar su historial.

## Roles y alcance — RN-AUTH-ROL

- **RN-AUTH-ROL-01:** Los únicos roles funcionales son Usuario, Técnico y Administrador.
- **RN-AUTH-ROL-02:** El Técnico es personal asociado a una unidad organizacional y solo puede ejecutar operaciones administrativas sobre esa unidad.
- **RN-AUTH-ROL-03:** El Administrador tiene alcance global sobre las unidades organizacionales.
- **RN-AUTH-ROL-04:** El Usuario no tiene permisos administrativos por el hecho de poseer una cuenta o una vinculación académica.
- **RN-AUTH-ROL-05:** Los permisos y el alcance deben validarse en el servidor con información vigente; no se derivan únicamente del nombre del cargo ni de datos enviados por el cliente.

## Sesiones — RN-AUTH-SES

- **RN-AUTH-SES-01:** Las sesiones se registran en `auth.sesiones` y una sesión revocada o vencida no puede continuar operaciones.
- **RN-AUTH-SES-02:** Cerrar sesión revoca la sesión correspondiente.
- **RN-AUTH-SES-03:** Los cambios de cuenta, identidad o permisos aplican a nuevas decisiones de autorización y no alteran la trazabilidad histórica.

Las entidades persistentes se detallan en [data-model.md](data-model.md). Los controles técnicos de seguridad se detallan en [security.md](security.md).
