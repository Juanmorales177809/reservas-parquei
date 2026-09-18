# User Flows — Administration

Este documento describe los flujos administrativos del módulo `administration`. La importación escribe los catálogos propios de `investigacion`; Researchs conserva la propiedad de las entidades y de las vinculaciones.

## UF-ADM-01 — Importar proyectos o semilleros mediante Excel

**Actor principal:** Administrador

**Precondiciones:**

- La cuenta está autenticada, activa y tiene alcance global.
- El archivo corresponde a un catálogo de proyectos o de semilleros.

**Flujo principal:**

1. El Administrador selecciona «Importar catálogo de investigación».
2. Selecciona el tipo de catálogo: `proyectos` o `semilleros`.
3. Carga un archivo Excel con las columnas `codigo`, `nombre` y `estado`.
4. El sistema valida el formato, las columnas, los campos obligatorios, los estados permitidos y los códigos duplicados dentro del archivo.
5. El sistema compara los códigos con el catálogo correspondiente de `investigacion` y muestra un resumen de registros nuevos, actualizados y desactivados, junto con los errores encontrados.
6. El Administrador revisa el resultado y confirma la importación.
7. El sistema crea los códigos nuevos y actualiza los códigos existentes en la tabla de `investigacion` correspondiente.
8. El sistema conserva las identidades, vinculaciones y referencias históricas; no crea ni modifica vinculaciones de usuarios.
9. El sistema registra la operación, el Administrador, la fecha, el catálogo, la referencia del archivo y el resultado por registro.

**Flujos alternos:**

- Si el archivo no cumple el formato o contiene errores, el sistema rechaza la confirmación y muestra los errores sin guardar cambios parciales.
- Si un código ya existe, se actualiza ese registro; no se crea un duplicado.
- Si el archivo contiene nombres parecidos con códigos diferentes, el sistema puede advertir la coincidencia, pero no fusiona registros automáticamente.
- Si la cuenta no tiene alcance global, el sistema rechaza la operación.

## Separación de responsabilidades

- Administration autoriza, valida y ejecuta la carga.
- Researchs conserva las entidades `proyectos` y `semilleros`, sus identificadores y sus vinculaciones.
- La importación no asigna usuarios a proyectos o semilleros.
- Los Usuarios seleccionan registros existentes; no crean proyectos ni semilleros desde su perfil o una reserva.
