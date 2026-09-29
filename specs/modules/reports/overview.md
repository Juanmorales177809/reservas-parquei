# Reports

## Purpose

Gestionar la consulta, consolidación, visualización y exportación de información derivada de Reservas Parquei.

El módulo transforma datos existentes del sistema en reportes de ocupación y uso, sin modificar el estado de reservas, recursos, usuarios ni configuraciones.

## Scope

El módulo cubre:

- consulta de información consolidada;
- reportes de ocupación por laboratorio;
- reportes por espacio;
- reportes por recurso;
- reportes por proyecto;
- reportes por semillero;
- aplicación de filtros;
- selección de periodos;
- agrupación de información;
- visualización de resultados;
- exportación de reportes;
- control del ámbito autorizado de consulta.

## Responsibilities

El módulo es responsable de:

- consultar información registrada por otros módulos;
- aplicar filtros y criterios de agrupación;
- limitar los resultados al ámbito autorizado del usuario;
- generar reportes por las dimensiones definidas;
- presentar resultados de forma consistente;
- permitir exportaciones cuando corresponda;
- preservar la correspondencia entre datos fuente, filtros y resultados;
- evitar inferencias o cálculos que no estén definidos por reglas explícitas;
- mantener las operaciones de reporte como operaciones de solo lectura.

## Owned Concepts

El módulo es propietario funcional de los siguientes conceptos:

- reporte;
- criterio de consulta;
- filtro;
- periodo;
- dimensión de análisis;
- agrupación;
- resultado agregado;
- visualización;
- exportación.

Las entidades persistentes concretas, si existen, se definen en `docs/data-model.md`.

## Dependencies

### Reservations

El módulo depende de Reservations para obtener:

- reservas registradas;
- estados;
- fechas;
- horarios;
- relaciones con recursos;
- contexto asociado a cada reserva.

Reports no modifica reservas ni redefine sus estados o reglas de negocio.

### Resources

El módulo depende de Resources para obtener:

- laboratorios;
- espacios;
- equipos;
- mobiliarios;
- otros recursos;
- relaciones con unidades organizacionales.

Reports no administra estos elementos.

### Auth

El módulo utiliza Auth para determinar:

- identidad autenticada;
- permisos de consulta;
- ámbito organizacional autorizado.

Reports no autentica usuarios ni evalúa permisos fuera de la información suministrada por Auth.

### Administration

El módulo puede utilizar información administrativa para interpretar unidades organizacionales, perfiles u otros datos necesarios para filtros y agrupaciones.

Reports no administra dicha información.

## Provides

El módulo proporciona al resto del sistema:

- consultas consolidadas;
- reportes de ocupación;
- resultados agrupados por dimensiones autorizadas;
- visualizaciones;
- exportaciones;
- información derivada de datos existentes sin modificar las fuentes.

## Out of Scope

No pertenece a este módulo:

- crear reservas;
- aprobar o rechazar reservas;
- cancelar reservas;
- modificar estados de reserva;
- administrar laboratorios, espacios o recursos;
- autenticar usuarios;
- administrar permisos;
- generar notificaciones;
- alterar datos fuente;
- definir reglas funcionales de otros módulos;
- inferir métricas cuya fórmula no haya sido definida previamente.

## Module Boundary

Reports responde principalmente a las siguientes preguntas:

- ¿Qué información puede consultar el usuario?
- ¿Qué filtros pueden aplicarse?
- ¿Cómo se agrupan los resultados?
- ¿Qué dimensiones pueden utilizarse?
- ¿Qué datos deben mostrarse?
- ¿Qué información puede exportarse?

No responde preguntas como:

- ¿La reserva puede aprobarse?
- ¿Existe un conflicto de horario?
- ¿El recurso está operativo?
- ¿El usuario puede autenticarse?
- ¿Debe generarse una notificación?
- ¿Cómo se modifica una unidad organizacional?

Estas decisiones pertenecen a los módulos propietarios correspondientes.

## Related Documentation

- `business-rules.md`
- `../../docs/product-spec.md`
- `../../docs/architecture.md`
- `../../docs/data-model.md`

Los contratos API específicos de reportes deben mantenerse en la documentación central de API.


## Modelo persistente

[Modelo de datos del módulo](data-model.md): tablas propias, relaciones y diferencias pendientes respecto al inventario principal.

## Pantallas

[Especificación de pantallas](screens.md), [wireframes](wireframes.md) y [navegación funcional](screen-flow.md): las tres superficies de reportes (ocupación, solicitudes y lista de espera) y la decisión de qué se muestra como gráfico y qué solo como tabla exportable.
