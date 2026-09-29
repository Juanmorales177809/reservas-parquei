# Administration

## Purpose

Gestionar la configuración administrativa e institucional necesaria para la operación de Reservas Parquei.

El módulo administra usuarios, cuentas, perfiles, unidades organizacionales, permisos y configuraciones globales, respetando las reglas de autenticación, autorización y los límites funcionales definidos por los demás módulos.

## Scope

El módulo cubre:

- gestión administrativa de usuarios;
- gestión administrativa de cuentas;
- gestión de perfiles;
- gestión de unidades organizacionales;
- gestión de permisos;
- habilitación y deshabilitación administrativa de entidades cuando corresponda;
- importación administrativa de proyectos y semilleros hacia los catálogos de `investigacion`;
- trazabilidad de operaciones administrativas.

## Responsibilities

El módulo es responsable de:

- crear, consultar, modificar, habilitar o deshabilitar usuarios cuando corresponda;
- administrar cuentas sin intervenir en los mecanismos internos de autenticación;
- gestionar perfiles;
- gestionar unidades organizacionales;
- gestionar permisos y sus asignaciones;
- mantener configuraciones globales;
- validar dependencias antes de modificar o deshabilitar entidades administrativas;
- preservar la consistencia de los datos administrativos;
- registrar operaciones administrativas relevantes;
- importar catálogos de investigación mediante archivos Excel, sin duplicar su propiedad funcional;
- evitar modificaciones que contradigan reglas funcionales pertenecientes a otros módulos.

## Owned Concepts

El módulo es propietario funcional de los siguientes conceptos:

- usuario administrable;
- cuenta administrable;
- perfil;
- unidad organizacional;
- permiso;
- importación de catálogos de proyectos y semilleros;
- estado administrativo de habilitación o deshabilitación.

Las entidades persistentes concretas asociadas a estos conceptos se definen en `docs/data-model.md`.

## Dependencies

### Auth

El módulo depende de Auth para:

- validar la identidad autenticada;
- verificar permisos;
- determinar el ámbito autorizado de actuación;
- garantizar que una operación administrativa sea ejecutada por una cuenta válida.

Administration gestiona permisos y configuraciones relacionadas, pero Auth es responsable de evaluar la autenticación y autorización durante la ejecución de operaciones protegidas.

### Reservations

El módulo depende de Reservations cuando una modificación administrativa pueda afectar reservas existentes o futuras.

Administration no decide estados, disponibilidad, aprobación, rechazo o cancelación de reservas.

### Resources

El módulo depende de Resources cuando una operación administrativa involucra laboratorios, espacios, equipos, mobiliarios u otros recursos.

Administration no redefine las reglas funcionales propias de dichos elementos.

### Researchs

Administration utiliza el contrato de Researchs para escribir los catálogos de proyectos y semilleros durante una importación autorizada. No crea copias de las entidades ni administra sus vinculaciones.

### Notifications

El módulo puede originar eventos que requieran notificación.

Notifications determina cómo registrar y presentar dichas comunicaciones.

### Reports

El módulo puede proporcionar información administrativa utilizada como dimensión o contexto en reportes.

Reports determina cómo consultar, agrupar y presentar dicha información.

## Provides

El módulo proporciona al resto del sistema:

- información administrativa de usuarios;
- cuentas habilitadas o deshabilitadas;
- perfiles;
- unidades organizacionales;
- permisos;
- configuraciones globales;
- estado administrativo de las entidades gestionadas.

## Out of Scope

No pertenece a este módulo:

- autenticar credenciales;
- emitir o validar tokens;
- gestionar sesiones;
- decidir directamente si una operación está autorizada durante su ejecución;
- crear, aprobar, rechazar o cancelar reservas;
- determinar disponibilidad temporal;
- administrar reglas funcionales de recursos;
- generar notificaciones;
- calcular reportes;
- administrar directamente las vinculaciones académicas o investigativas de los usuarios;
- crear proyectos o semilleros fuera del flujo de importación autorizado;
- modificar directamente la lógica interna de otros módulos.

## Module Boundary

Administration responde principalmente a las siguientes preguntas:

- ¿Qué usuarios existen y cuál es su estado administrativo?
- ¿Qué cuentas están habilitadas administrativamente?
- ¿Qué perfiles existen?
- ¿Qué unidades organizacionales existen?
- ¿Qué permisos están definidos y cómo se asignan?

No responde preguntas como:

- ¿La cuenta está autenticada en este momento?
- ¿El token es válido?
- ¿La reserva puede aprobarse?
- ¿Existe conflicto de disponibilidad?
- ¿Qué notificación debe generarse?
- ¿Cómo se calcula un reporte?

Estas decisiones pertenecen a los módulos propietarios correspondientes.

## Related Documentation

- `business-rules.md`
- `../../docs/product-spec.md`
- `../../docs/architecture.md`
- `../../docs/data-model.md`
- [Especificación de pantallas](screens.md), [wireframes](wireframes.md) y [navegación funcional](screen-flow.md): las cinco superficies de administración.

Los contratos API específicos de administración deben mantenerse en la documentación central de API.


## Modelo persistente

[Modelo de datos del módulo](data-model.md): tablas propias, relaciones y diferencias pendientes respecto al inventario principal.
