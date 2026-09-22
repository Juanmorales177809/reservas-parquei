# Contratos de API — convenciones transversales

Este documento define lo que **todos** los contratos de módulo comparten: formato, errores, autenticación, paginación y concurrencia. Cumple la exigencia de `architecture.md` §8 de mantener convenciones comunes y de que ningún módulo defina convenciones incompatibles.

Un contrato de módulo no repite nada de aquí: lo referencia y solo documenta lo propio. Ante conflicto, prevalecen las reglas del módulo propietario y la [arquitectura central](../docs/architecture.md).

## Contratos existentes

| Módulo | Contrato | Derivado de |
|---|---|---|
| [auth](auth/api-contract.md) | sesión, credenciales, invitaciones y administración de cuentas | 13 flujos `UF-AUTH` |
| [reservations](reservations/api-contract.md) | ciclo completo de la reserva | 19 flujos `UF-RES` |
| [espacios](espacios/api-contract.md) | espacios, recursos asociados y campos adicionales | 14 flujos `UF-ESP` |
| [usuarios](usuarios/api-contract.md) | perfil del reservista y vinculaciones | 11 flujos `UF-USR` |
| [resources](resources/api-contract.md) | catálogo de recursos y configuración del laboratorio | 12 flujos `UF-REC` |

Pendientes de escribir: `administration`, `notifications`, `reports` y `researchs`. Researchs ya define su flujo administrativo, pero aún no define rutas HTTP; redactar su contrato exigiría inventar esa superficie. Los demás módulos requieren primero completar su `user-flow.md`.

---

## 1. Formato y transporte

| Aspecto | Definición |
|---|---|
| Base path | `/api/<módulo>`, indicado en cada contrato |
| Formato | `application/json` en solicitudes y respuestas |
| Fechas y horas | ISO 8601 en UTC (`2026-09-19T14:03:11Z`) |
| Fechas sin hora | `YYYY-MM-DD` |
| Horas sin fecha | `HH:MM` en 24 horas |
| Identificadores | enteros; `id_cuenta` es de 64 bits y `id_sesion` es UUID |
| Transporte | HTTPS obligatorio en toda ruta autenticada (`SEC-INF-01`, `SEC-SES-06`) |
| Caché | las respuestas con información de sesión declaran `Cache-Control: no-store` (`SEC-SES-11`) |

Las operaciones que modifican estado nunca se exponen mediante `GET` (`SEC-CSRF-03`).

Los nombres de campo usan `snake_case` y conservan el nombre de la columna del modelo de datos cuando lo exponen directamente, para que el contrato y el modelo se lean juntos sin traducción mental.

## 2. Errores

Toda respuesta de error usa la misma estructura, conforme a `architecture.md` §12:

```json
{
  "error": {
    "codigo": "CONFLICTO",
    "mensaje": "El horario solicitado ya no está disponible.",
    "detalles": []
  }
}
```

`detalles` se usa solo para errores de validación de campos y nunca contiene trazas internas, SQL, secretos ni variables de entorno (`SEC-INF-04`).

### Catálogo común de códigos

| HTTP | `codigo` | Uso |
|---|---|---|
| 400 | `SOLICITUD_INVALIDA` | Cuerpo malformado o parámetros incompatibles |
| 401 | `NO_AUTENTICADO` | Falta sesión válida, o venció o fue revocada (`SEC-SES-07`) |
| 401 | `CREDENCIALES_INVALIDAS` | Autenticación fallida, sin distinguir la causa (`SEC-ABU-02`) |
| 401 | `REAUTENTICACION_REQUERIDA` | Operación sensible sin autenticación reciente (`SEC-REAUTH-01`) |
| 403 | `NO_AUTORIZADO` | Permiso ausente, fuera de ámbito o recurso ajeno (`SEC-AUTZ-02`, `SEC-AUTZ-04`, `SEC-AUTZ-06`) |
| 403 | `PERFIL_INICIAL_PENDIENTE` | Requiere haber completado la actualización inicial del Usuario (`RN-USR-08` de usuarios) |
| 403 | `VINCULACION_REQUERIDA` | El Usuario no conserva ninguna vinculación activa y válida (`RN-USR-11` de usuarios) |
| 404 | `NO_ENCONTRADO` | Recurso inexistente dentro del ámbito visible del actor |
| 409 | `CONFLICTO` | Conflicto de negocio: duplicado, solapamiento o estado incompatible |
| 410 | `TOKEN_NO_VIGENTE` | Token vencido, ya utilizado o revocado (`SEC-TOK-05`) |
| 422 | `VALIDACION` | Campos inválidos según el esquema |
| 429 | `DEMASIADOS_INTENTOS` | Límite contra abuso superado (`SEC-ABU-01`) |
| 500 | `ERROR_INTERNO` | Error no controlado, sin detalle interno |

`403 NO_AUTORIZADO` no distingue entre "sin permiso", "fuera de ámbito" y "recurso ajeno", para no facilitar enumeración. Un recurso existente pero fuera del ámbito del actor responde `404 NO_ENCONTRADO` cuando revelar su existencia constituya una fuga.

Un contrato de módulo puede añadir códigos propios, pero no redefinir el significado de los anteriores.

## 3. Autenticación y autorización

Todas las rutas son autenticadas salvo que su contrato diga lo contrario. El detalle del mecanismo —cookies `rp_access` y `rp_refresh`, claims del JWT, renovación y cierre— está en el [contrato de auth](auth/api-contract.md) y no se repite aquí.

Lo que cada módulo debe asumir:

- La identidad proviene de la sesión, nunca de identificadores enviados por el cliente (`SEC-AUTZ-03`).
- Toda operación que modifica estado exige el encabezado `X-CSRF-Token` con el valor de la cookie `rp_csrf`, obtenible en `GET /api/auth/csrf` (`SEC-CSRF-01`).
- El permiso y el ámbito organizacional se evalúan en el servidor en cada operación, mediante `exigir_permiso` del contrato interno de auth (`SEC-AUTZ-01`, `SEC-AUTZ-04`).
- La comprobación de que un recurso concreto pertenece al actor corresponde al módulo propietario, además del permiso general (`SEC-AUTZ-06`).
- Ante imposibilidad de comprobar el permiso, la decisión es denegar (`SEC-AUTZ-02`).

Cada endpoint declara el permiso que exige. Un endpoint sin permiso declarado solo requiere sesión válida.

## 4. Listados, paginación, filtros y orden

`architecture.md` §8 exige una convención común de paginación. Todo endpoint que devuelva una colección la aplica.

**Solicitud** mediante parámetros de consulta:

| Parámetro | Valor |
|---|---|
| `pagina` | entero desde 1; por defecto 1 |
| `tamano` | entero entre 1 y 100; por defecto 20 |
| `orden` | nombre de campo admitido por el endpoint, con `-` delante para descendente |

**Respuesta** con la misma envolvente en todos los módulos:

```json
{
  "datos": [],
  "paginacion": {
    "pagina": 1,
    "tamano": 20,
    "total": 137,
    "paginas": 7
  }
}
```

Los filtros propios de cada endpoint se declaran en su contrato y viajan como parámetros de consulta adicionales. Un filtro desconocido responde `400 SOLICITUD_INVALIDA` en lugar de ignorarse en silencio, para que un error de nombre no devuelva datos que el cliente cree filtrados.

Un listado nunca devuelve elementos fuera del ámbito autorizado del actor: el filtro de ámbito se aplica en el servidor antes de paginar, de modo que `total` refleja lo que el actor puede ver y no el total del sistema.

## 5. Concurrencia y consistencia

Las operaciones que dependen de disponibilidad —crear, reprogramar o aprobar una reserva— revalidan sus condiciones dentro de la transacción de escritura. Que el cliente haya consultado disponibilidad antes no garantiza nada: un conflicto detectado al guardar responde `409 CONFLICTO`, incluso si la consulta previa fue satisfactoria.

La propuesta de diseño seleccionada en [ADR-001](../docs/decisions/adr-001-doble-reserva.md) es una restricción de exclusión de PostgreSQL. Su aprobación formal, implementación y pruebas de concurrencia siguen pendientes; hasta completarlas, ningún contrato puede afirmar que esa garantía esté satisfecha.

Una operación que afecte varias entidades relacionadas es atómica: o se escriben todas o ninguna (`RN-INT-01` de administration, `architecture.md` §9).

## 6. Auditoría

La auditoría administrativa registra actor, acción, entidad, identificador y momento en `administration.auditoria`. Ningún contrato expone endpoints que permitan modificar esos registros. La auditoría de Reservations está fuera del alcance funcional actual; el historial de estados de una reserva no la sustituye ni define un mecanismo de auditoría.
