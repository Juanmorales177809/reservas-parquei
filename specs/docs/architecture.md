# Reservas Parquei — Architecture

## 1. Purpose

Este documento define la arquitectura general de Reservas Parquei y establece las decisiones técnicas, responsabilidades de los componentes, límites entre módulos y restricciones que deben respetarse durante el desarrollo.

La arquitectura descrita aquí es común a todos los módulos del sistema. Las decisiones locales de implementación pueden definirse dentro de cada módulo siempre que no contradigan este documento.

Los cambios a esta arquitectura deben ser revisados y acordados antes de su incorporación.

---

## 2. System Context

Reservas Parquei es una aplicación web para gestionar solicitudes, aprobación, consulta y administración de reservas de laboratorios, espacios, equipos, mobiliarios y otros recursos institucionales.

Los usuarios interactúan con el sistema mediante un navegador web.

Los actores principales son:

- solicitante;
- Técnico;
- administrador institucional.

El sistema no requiere servicios externos para ejecutar el flujo principal de reservas.

```text
Solicitante ───────────────┐
                           │
Técnico ────────────────────┼──→ Reservas Parquei
                           │
Administrador institucional ┘
```

---

## 3. Technology Stack

| Componente | Tecnología | Responsabilidad |
|---|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS y Recharts | Presentación de la interfaz, navegación, formularios, visualización de estados e informes y consumo de la API |
| Backend | FastAPI, Python, SQLAlchemy, Pydantic y Uvicorn | API, autenticación, autorización, validación, reglas de negocio y acceso a datos |
| Base de datos | PostgreSQL 13 | Persistencia, integridad de los datos, relaciones y soporte de transacciones |
| Autenticación | JWT y bcrypt | Autenticación de usuarios y protección de operaciones |
| Despliegue | Docker y Docker Compose | Ejecución y comunicación entre los componentes del sistema |

---

## 4. High-Level Architecture

Reservas Parquei utiliza una arquitectura web separada en frontend, backend y persistencia.

```text
┌──────────────────────┐
│      Navegador       │
│                      │
│ Solicitante          │
│ Técnico              │
│ Administrador        │
└──────────┬───────────┘
           │
           │ HTTP/HTTPS
           ▼
┌──────────────────────┐
│       Next.js        │
│       React          │
│                      │
│     Frontend Web     │
└──────────┬───────────┘
           │
           │ API HTTP
           ▼
┌──────────────────────┐
│       FastAPI        │
│                      │
│ Backend / Business   │
│       Logic          │
└──────────┬───────────┘
           │
           │ SQLAlchemy
           ▼
┌──────────────────────┐
│    PostgreSQL 13     │
│                      │
│     Persistence      │
└──────────────────────┘
```

El flujo general de datos es:

```text
Usuario
  ↓
Next.js
  ↓
FastAPI
  ↓
PostgreSQL
  ↓
FastAPI
  ↓
Next.js
  ↓
Usuario
```

---

## 5. Component Responsibilities

### 5.1 Frontend

El frontend es responsable de:

- presentar la interfaz web;
- gestionar navegación y vistas;
- capturar información mediante formularios;
- ejecutar validaciones de interfaz;
- consumir la API del backend;
- mostrar estados de carga, confirmación, vacío y error;
- visualizar información de reservas, recursos e informes;
- adaptar la interfaz a móvil, tablet y desktop.

El frontend no debe ser la única capa responsable de validar reglas de negocio críticas.

Las validaciones realizadas en el cliente deben considerarse complementarias a las realizadas por el backend.

---

### 5.2 Backend

El backend constituye la autoridad para las reglas de negocio y es responsable de:

- exponer la API;
- autenticar usuarios;
- verificar autorizaciones;
- validar solicitudes;
- aplicar reglas de negocio;
- gestionar reservas;
- gestionar recursos;
- gestionar usuarios y permisos cuando corresponda;
- registrar notificaciones;
- registrar historial y control de cambios;
- ejecutar operaciones transaccionales;
- coordinar el acceso a PostgreSQL;
- devolver respuestas y errores consistentes al frontend.

Las reglas que afecten integridad, autorización o disponibilidad deben ser verificadas en el backend independientemente de las validaciones existentes en el frontend.

---

### 5.3 Database

PostgreSQL es responsable de almacenar la información persistente del sistema.

Debe proporcionar:

- integridad referencial;
- restricciones estructurales;
- consistencia transaccional;
- relaciones entre entidades;
- soporte para operaciones concurrentes.

Las restricciones que puedan protegerse directamente en la base de datos deben evaluarse como complemento de las validaciones realizadas en el backend.

La base de datos no debe utilizarse como sustituto de la lógica de negocio del sistema.

---

## 6. Module Boundaries

El sistema se divide en módulos funcionales con responsabilidades definidas.

### 6.1 Authentication

Responsable de:

- autenticación;
- emisión y validación de JWT;
- protección de operaciones autenticadas;
- identificación del usuario que ejecuta una operación.

No administra las reglas funcionales de reservas o recursos.

---

### 6.2 Resources

Responsable de gestionar:

- laboratorios;
- espacios;
- equipos;
- mobiliarios;
- otros recursos;
- disponibilidad configurable;
- habilitación o deshabilitación;
- horarios de atención;
- parámetros asociados al uso de recursos.

No es responsable del ciclo de aprobación de una reserva.

---

### 6.3 Reservation Request

Responsable del proceso mediante el cual un solicitante crea una solicitud de reserva.

Incluye:

- selección de fecha;
- selección de horario;
- selección de espacio;
- selección de recursos;
- registro de asistentes;
- proyecto;
- semillero;
- motivo;
- validación de datos;
- validación de disponibilidad;
- creación de la solicitud;
- asignación del estado inicial.

---

### 6.4 Reservation Management

Responsable de gestionar solicitudes existentes.

Incluye:

- consulta de solicitudes;
- aprobación;
- rechazo;
- edición cuando corresponda;
- cancelación;
- actualización de estado;
- liberación de recursos cuando corresponda;
- registro del motivo de rechazo cuando sea requerido;
- registro de cambios asociados a la gestión.

---

### 6.5 Notifications

Responsable de registrar y suministrar notificaciones relacionadas con eventos relevantes del sistema.

Entre ellas:

- recepción de una solicitud;
- aprobación;
- rechazo;
- cancelación;
- otros cambios de estado definidos por el producto.

El módulo de notificaciones no decide cuándo una reserva puede aprobarse o rechazarse. Recibe el resultado de dichas operaciones.

---

### 6.6 Administration

Responsable de funciones administrativas globales, incluyendo:

- usuarios;
- cuentas;
- perfiles;
- unidades organizacionales;
- permisos;
- configuración general del sistema.

Las responsabilidades específicas deberán mantenerse separadas de las operaciones ordinarias realizadas por Usuarios y Técnicos.

---

### 6.7 Reports

Responsable de consultas e informes relacionados con ocupación y uso.

Debe permitir elaborar información por:

- laboratorios;
- espacios;
- recursos;
- proyectos;
- semilleros.

Este módulo consume información producida por otros módulos y no debe alterar el estado de una reserva como parte de una operación de consulta o generación de informes.

---

## 7. Module Interaction

Los módulos forman parte del mismo backend pero deben conservar límites funcionales claros.

La relación conceptual principal es:

```text
Authentication
      │
      ▼
Reservation Request
      │
      ├──────────────→ Resources
      │
      ▼
Reservation Management
      │
      ├──────────────→ Notifications
      │
      └──────────────→ Change History

Administration
      │
      ├──────────────→ Users / Permissions
      └──────────────→ Resources

Reports
      │
      └──────────────→ Reservation and Resource Data
```

Un módulo puede utilizar información de otro módulo cuando sea necesario, pero no debe asumir responsabilidades que pertenecen al módulo propietario.

---

## 8. Communication and API

La comunicación entre frontend y backend se realiza mediante una API HTTP.

```text
Browser
   ↓
Next.js
   ↓
/api/*
   ↓
FastAPI
```

Las operaciones protegidas requieren autenticación.

Los contratos específicos de endpoints, solicitudes, respuestas y códigos HTTP deben documentarse fuera de este archivo en la documentación de API.

La API debe mantener convenciones comunes para:

- estructura de solicitudes;
- estructura de respuestas;
- autenticación;
- validación;
- códigos HTTP;
- representación de errores;
- paginación cuando corresponda.

Los módulos no deben definir convenciones incompatibles entre sí.

---

## 9. Data Architecture

La información persistente se almacena en PostgreSQL.

El acceso desde el backend se realiza mediante SQLAlchemy.

Pydantic se utiliza para validación y representación de datos en las fronteras de la API.

El modelo de datos completo debe documentarse en `data-model.md`.

Este documento arquitectónico solo establece los siguientes principios:

- cada entidad debe tener una responsabilidad identificable;
- las relaciones entre entidades deben mantenerse explícitas;
- debe evitarse la duplicación innecesaria de información;
- las operaciones que modifican varias entidades relacionadas deben preservar consistencia;
- las operaciones críticas deben ejecutarse mediante transacciones cuando corresponda;
- el modelo de datos debe permitir mantener historial y trazabilidad de las operaciones relevantes.

---

## 10. Reservation Consistency and Concurrency

La disponibilidad de recursos es una restricción central del sistema.

El sistema debe impedir inconsistencias cuando dos o más solicitudes intenten utilizar simultáneamente un mismo recurso en horarios incompatibles.

La validación de disponibilidad realizada únicamente antes de una operación de escritura no garantiza por sí sola la consistencia en escenarios concurrentes.

La implementación deberá utilizar mecanismos transaccionales y restricciones adecuadas para garantizar que una condición válida al comenzar una operación no pueda invalidarse silenciosamente por otra solicitud concurrente.

La decisión técnica específica para implementar esta protección debe documentarse como una decisión arquitectónica antes de su implementación.

---

## 11. Security Architecture

### 11.1 Authentication

Las operaciones protegidas requieren autenticación mediante JWT.

El backend es responsable de:

- verificar el token;
- identificar al usuario autenticado;
- rechazar tokens inválidos o expirados;
- asociar las operaciones al usuario correspondiente.

---

### 11.2 Authorization

La autorización debe considerar:

- rol;
- permisos;
- unidad organizacional cuando corresponda;
- propiedad de los recursos o reservas cuando aplique.

La autenticación no implica autorización.

Cada operación protegida debe validar explícitamente si el usuario puede ejecutarla.

---

### 11.3 Password Protection

Las contraseñas deben almacenarse mediante hash con bcrypt.

Las contraseñas originales no deben almacenarse ni registrarse.

---

### 11.4 Secrets

Las claves de firma, contraseñas de base de datos y demás credenciales deben almacenarse mediante variables de entorno o mecanismos equivalentes de configuración externa.

No deben incorporarse al código fuente ni al repositorio.

---

### 11.5 Auditability

Las operaciones administrativas y los cambios relevantes sobre reservas deben poder asociarse con:

- operación ejecutada;
- usuario responsable;
- fecha y hora;
- elemento afectado;
- cambio realizado cuando corresponda.

---

## 12. Error Handling

El backend debe utilizar una estrategia consistente para representar errores.

Se deben diferenciar al menos:

- errores de validación;
- errores de autenticación;
- errores de autorización;
- recurso no encontrado;
- conflictos de negocio;
- errores internos.

El frontend debe interpretar estas respuestas y presentar mensajes comprensibles para el usuario.

Los detalles internos de excepciones, consultas SQL, credenciales o trazas no deben exponerse al cliente.

---

## 13. Validation

La validación se realiza en diferentes niveles.

### Frontend

Responsable de mejorar la experiencia del usuario mediante:

- campos obligatorios;
- formatos;
- restricciones visibles;
- mensajes inmediatos.

### Backend

Responsable de:

- validación definitiva;
- reglas de negocio;
- autorización;
- consistencia de datos;
- disponibilidad.

### Database

Responsable de:

- tipos;
- claves;
- relaciones;
- unicidad;
- restricciones estructurales;
- consistencia transaccional.

Las mismas reglas no deben implementarse innecesariamente en múltiples lugares salvo cuando cada nivel tenga una responsabilidad diferente.

---

## 14. Deployment Architecture

El sistema se ejecuta mediante Docker y Docker Compose.

La arquitectura de despliegue base es:

```text
┌────────────────────┐
│ Frontend Container │
│ Next.js :3000      │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Backend Container  │
│ FastAPI :8000      │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Database Container │
│ PostgreSQL :5432   │
└────────────────────┘
```

Los componentes deben comunicarse mediante la red interna definida por Docker Compose.

Las credenciales y parámetros específicos de cada entorno deben permanecer fuera del código fuente.

---

## 15. Cross-Cutting Concerns

### Configuration

La configuración dependiente del entorno debe mantenerse fuera del código fuente cuando corresponda.

### Logging

El backend debe registrar información suficiente para diagnosticar errores y operaciones relevantes sin almacenar información sensible innecesaria.

### Audit Trail

Las operaciones relevantes definidas por el producto deben generar registros que permitan reconstruir los cambios realizados.

### Date and Time Handling

La representación y almacenamiento de fechas y horas debe mantenerse consistente en todo el sistema.

La convención específica debe definirse antes de implementar módulos que dependan de comparaciones temporales.

### Error Consistency

Los módulos deben seguir la misma convención de respuestas de error.

### Database Migrations

Las modificaciones del esquema de base de datos deben ser reproducibles y versionadas mediante un mecanismo de migraciones.

No deben realizarse cambios manuales no documentados como mecanismo normal de evolución del sistema.

---

## 16. Architectural Constraints

Las siguientes restricciones son obligatorias para todos los módulos:

1. El frontend utiliza Next.js 14, React 18 y TypeScript.

2. El backend utiliza FastAPI, Python, SQLAlchemy y Pydantic.

3. PostgreSQL 13 es la base de datos del sistema.

4. El frontend se comunica con el backend mediante la API definida.

5. Las reglas de negocio críticas deben validarse en el backend.

6. Las operaciones protegidas requieren autenticación y autorización.

7. Las credenciales y secretos no pueden almacenarse en el código fuente.

8. Los módulos deben respetar los límites de responsabilidad definidos en este documento.

9. Un módulo no debe redefinir una regla global del sistema.

10. Los cambios en el modelo de datos deben mantenerse versionados.

11. Las operaciones relacionadas con disponibilidad de recursos deben preservar consistencia ante concurrencia.

12. Los cambios relevantes deben mantener la trazabilidad requerida por el producto.

---

## 17. Architectural Decisions

Las decisiones arquitectónicas que requieran análisis específico deben documentarse independientemente mediante Architecture Decision Records (ADR).

Un ADR debe utilizarse cuando una decisión:

- afecte varios módulos;
- modifique una restricción arquitectónica;
- introduzca una dependencia tecnológica relevante;
- cambie una estrategia de persistencia;
- afecte seguridad;
- afecte concurrencia;
- cambie la forma de comunicación entre componentes.

Este documento debe referenciar dichas decisiones cuando sean incorporadas a la arquitectura aceptada.

Decisiones registradas:

- [ADR-001 — Mecanismo contra la doble reserva concurrente](decisions/adr-001-doble-reserva.md): selecciona a nivel de diseño una restricción de exclusión de PostgreSQL para la exigencia de la sección 10. Pendiente de aprobación formal e implementación.

---

## 18. Relationship with Other Documentation

La documentación del proyecto se divide por responsabilidad.

```text
docs/spec.md
    Define qué debe hacer el producto.

docs/architecture.md
    Define cómo está estructurado el sistema y cuáles son
    sus restricciones técnicas globales.

docs/data-model.md
    Define las entidades persistentes y sus relaciones.

docs/testing.md
    Define cómo se verifica que lo construido corresponde
    a lo especificado.

docs/trazabilidad.md
    Generado. Muestra, para cada regla, si tiene contrato,
    tarea y prueba.

contratos/
    Define los contratos de comunicación, uno por módulo.

modules/
    Define la responsabilidad, diseño, reglas, modelo,
    flujos, tareas y pruebas de cada módulo.
```

Fuera de `specs/`, en la raíz del repositorio: `plan.md` traduce esta arquitectura en cómo se construye, `tasks.md` fija el orden y `AGENTS.md` recoge las convenciones de trabajo.

Cuando exista conflicto entre una decisión local de un módulo y una restricción definida en este documento, prevalece la arquitectura central hasta que se apruebe formalmente un cambio.

---

## 19. Change Control

Este documento forma parte de la documentación central del proyecto.

No debe modificarse como consecuencia automática de una necesidad local de implementación.

Cuando un módulo requiera una modificación arquitectónica, debe presentar:

1. el problema identificado;
2. la restricción afectada;
3. el cambio propuesto;
4. alternativas consideradas;
5. impacto sobre otros módulos;
6. impacto sobre datos, API y pruebas;
7. decisión acordada.

Una vez aprobada la modificación, se actualiza este documento y, cuando corresponda, se registra la decisión mediante un ADR.
