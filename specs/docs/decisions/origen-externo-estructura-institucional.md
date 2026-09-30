# Decisión: los laboratorios, el personal, los cargos y los equipos vienen de otra base de datos

**Fecha:** 2026-09-30
**Origen:** indicación directa del equipo al usar la aplicación en el navegador.
**Estado:** vigente para la interfaz. La integración con la base de origen no está diseñada todavía.

## Qué se decidió

- Las **unidades organizacionales** se llaman **laboratorios** para quien usa la aplicación. Su nombre, su estructura, los **cargos** y el **personal** que los ocupan, y los **equipos** se originan en **otra base de datos**: el sistema LIA.
- De LIA **no se trae todo**: solo lo necesario para reservar. De un equipo, por ejemplo: laboratorio, nombre, marca, modelo, placa, serial, estado operativo y si requiere calibración; no su categoría, frecuencias, archivos ni datos técnicos.
- Por eso el administrador **no da de alta** laboratorios, cargos, personal ni equipos desde esta aplicación, ni renombra laboratorios o cargos, ni edita los datos del personal.
- Lo que sí se gestiona aquí es lo propio de las reservas: la **configuración de reservas de cada laboratorio** (horario, antelación, tipos de reserva), habilitar o deshabilitar un laboratorio, los **permisos**, los **recursos** y los **espacios**, el **acceso** (activar o desactivar) del personal, y el registro de **usuarios** que no son personal.

## Qué cambió en la interfaz

| Antes | Ahora |
|---|---|
| «Unidades y cargos» con formularios para crear unidades y cargos | «Laboratorios y cargos», de solo lectura, con «Configurar» y habilitar o deshabilitar |
| «Identidades» permitía registrar una ficha de Personal | Solo registra Usuarios; el personal no se registra aquí |
| Registrar un equipo desde «Registrar recurso» | Solo mobiliario y otros recursos; los equipos llegan de LIA |
| Editar a una persona de Personal (datos y cargo) | El personal se consulta; solo se activa o desactiva su acceso |
| «Unidad» en formularios, filtros y mensajes | «Laboratorio» |

## Qué NO cambió (y por qué importa)

Los endpoints que dan de alta estas entidades siguen existiendo en el servidor: `POST /api/unidades` y `POST /api/cargos` ([administration](../../contratos/administration/api-contract.md) §2.1 y §2.5) `POST /api/personal` ([usuarios](../../contratos/usuarios/api-contract.md) §6.1) y `POST /api/recursos` con `tipo` `EQUIPO` ([resources](../../contratos/resources/api-contract.md) §2.1). **La interfaz ya no los usa.** Se conservan como la vía por la que llegarán los datos de la base de origen (siembra o integración) hasta que esa integración se diseñe; retirarlos antes dejaría sin camino de carga a una estructura de la que dependen las reservas.

## Lo que queda abierto

1. **La integración** con la base de origen: cómo y cuándo llegan los laboratorios, los cargos y el personal, y si cambian por sincronización o por carga. Es una tarea por abrir; no se inventa aquí.
2. **Los identificadores y flujos que hoy suponen el alta manual** (`UF-ADM-03` «Registrar la identidad de Personal», `RN-UNI-01` y las pantallas `WF-ADM-01` y `WF-ADM-03` de [administration](../../modules/administration/)) describen un sistema donde el alta es manual. Siguen escritos así; esta decisión los acota en la interfaz sin reescribirlos. Reescribirlos, o retirar sus identificadores con su nota en [identificadores-retirados.md](identificadores-retirados.md), es una decisión aparte.
3. **Si el renombrado y el estado de un laboratorio** deben quedar también bloqueados en el servidor, o solo en la interfaz (hoy solo la interfaz).

## Carga inicial desde LIA

Los scripts de [`backend/seeds/`](../../../backend/seeds/) cargan lo necesario para reservar, primero en la copia de pruebas y en la base viva solo con autorización expresa:

- `lia_laboratorios_y_cargos.sql`: los 5 laboratorios y los 3 cargos que pertenecen a un laboratorio. No carga «Parque i», «Gestión Laboratorios» ni los cargos administrativos.
- `lia_equipos.sql`: los 2 equipos **activos**. Los otros 3 de LIA están inactivos y repiten serial o placa (únicos aquí); parecen datos de prueba.
- Sin cargar: el personal (LIA no guarda documento, correo ni teléfono, que aquí son obligatorios).

## Los permisos los define el rol (2026-09-30)

Por indicación del equipo, los permisos **no se otorgan a mano**: los define el rol.

| Rol | Qué puede hacer |
|---|---|
| Usuario | Solo reservar |
| Técnico o gestor | Gestionar únicamente su propio laboratorio, el de su cargo |
| Administrador | Todo |

- **El administrador es una cuenta propia de Reservas**, sin ficha en LIA: tipo de cuenta `ADMINISTRADOR`, sin identidad asociada. No viene de LIA y no se crea desde la interfaz (para entrar ya hace falta uno): se crea con `python -m app.scripts.crear_administrador --correo ...`, que pide la contraseña por la terminal.
- **El técnico es el personal de LIA** cuyo cargo pertenece a un laboratorio: gestiona solo ese laboratorio, sin asignación alguna. Sus permisos son los de ámbito de laboratorio (`reservas.administrar`, `reservas.exportar`, `espacios.administrar`, `recursos.administrar`, `recursos.editar_equipos`, `laboratorios.configurar`, `reportes.consultar`); lo demás es del administrador.
- **En la interfaz:** se quitó la pantalla «Permisos» y su entrada en Administración.
- **En el servidor (hecho):** `app/core/authz.py` deriva el rol del tipo de cuenta y del cargo; se eliminó `/api/permisos` y la asignación de permisos; la migración `014_cuenta_administrador.sql` admite el tipo `ADMINISTRADOR`. `auth.cuenta_permisos` queda sin uso y se retirará en otra migración.
- **Lo que queda abierto:** retirar los identificadores `RN-PER-*` y `UF-AUTH-09` (hoy marcados sin efecto), retirar la tabla `auth.cuenta_permisos`, y **aplicar la migración 014 en la base viva y crear su primer administrador** (la viva no tiene ninguna cuenta).
