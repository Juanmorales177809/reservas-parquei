# Decisiones — registro y pendientes

**Proyecto:** Reservas Parquei · **Rama:** `feature/v0.1.1` · **Último commit:** `765e126` · **Actualizado:** 23 de septiembre de 2026

**De las quince preguntas abiertas del proyecto, catorce están decididas y aplicadas.** Ya no queda ninguna decisión funcional pendiente. Lo que queda es trabajo.

---

## Decisiones tomadas

### Importaciones masivas

| Asunto | Decisión |
|---|---|
| Carga con filas en error | **Rechazo total.** Una sola fila con error impide confirmar la carga entera. El resultado por fila se conserva igual, para saber qué corregir sin volver a procesar el archivo |
| Columnas de la planilla de equipos | Las **seis reales** que se usan hoy: placa, descripción, código de bodega, centro de costos, fecha de inicio y costo. No se diseñó un formato nuevo |
| El costo | Se lee y se descarta. Es un dato contable del inventario institucional y ninguna regla de reservas lo necesita |
| Unidad de los equipos | La planilla no la trae: el Administrador la elige al cargar, y **se aplica solo a los equipos que esa carga cree**. Un equipo existente conserva la suya, porque cambiarla exige un permiso distinto |
| Desactivación por importación | **Nunca.** La importación de equipos solo crea y actualiza. Deshabilitar sigue siendo una acción individual, porque puede cancelar reservas futuras |

Un efecto de la planilla real: las descripciones siguen el patrón «tipo, marca, modelo y capacidad» y no cabían en el campo de nombre, que pasó de 50 a 100 caracteres. Con el rechazo total, una sola descripción larga habría frenado la carga entera.

### Reservas

| Asunto | Decisión |
|---|---|
| Inicio de una reserva de espacio | **Automático** al llegar su hora de inicio, simétrico con la finalización. Solo transita una reserva ya aprobada; el estado significa que la franja está en curso, **no que el usuario se haya presentado** |
| Motivo de solicitud | **Se retira** el catálogo heredado. El contexto ya dice para qué actividad se reserva y la razón del formato de salida ya dice por qué sale el equipo. La columna siempre admitió nulo, así que ninguna reserva depende de ella |
| Campos adicionales de los espacios | **Cinco tipos cerrados:** texto, texto largo, número, sí o no, y lista de opciones |
| Adjuntos de una solicitud | Planos (DWG, DXF, STEP, STL), imágenes (PNG, JPG) y PDF, hasta 5 MB. El técnico tiene que poder abrir el archivo para evaluar el requerimiento |

### Notificaciones

| Asunto | Decisión |
|---|---|
| Contenido de cada aviso | El texto vive en el **código**, no en plantillas editables desde el sistema. Cambiar una redacción es un despliegue; a cambio, no hay que construir una pantalla de administración |
| Entrega y reintento de correos | Una **tarea programada** del propio sistema, no una cola externa. La decisión es de propiedad más que de tecnología: la política de reintento se queda en este dominio y no pasa a depender de lo que decida una infraestructura ajena |

### Documentación

Se autorizó y se escribió el flujo de configuración de laboratorio —era el único sitio donde la interfaz iba por delante de los flujos— y el resumen del módulo de espacios, que tenía cinco líneas frente a las 49 a 164 de los demás.

---

## Lo que queda

### 1. Los contratos de cuatro módulos

Faltan los contratos de API de **administration, notifications, reports y researchs**.

Estuvieron bloqueados porque no había flujos de los que derivar su superficie. **Ese bloqueo ya no existe**: los cuatro tienen flujos, y el documento de convenciones describe la forma común que deben seguir para que no aparezca una quinta estructura distinta.

No es una decisión: es trabajo pendiente, y es lo último del registro.

### 2. La garantía contra doble reserva

Sigue pendiente la **aprobación formal** de la decisión sobre reservas concurrentes, junto con su implementación y sus pruebas.

Esto no es documentación: es la garantía de que dos personas no puedan reservar el mismo espacio a la misma hora. Hasta completarla, la funcionalidad de crear reserva no puede darse por correcta bajo carga, como advierte el propio documento de decisión.

---

## Frontend — arquitectura interna (29 de septiembre, pendiente de revisión)

`architecture.md` §3 fija el stack de frontend (Next.js 14, React 18, TypeScript, Tailwind, Recharts) pero no su arquitectura interna. Al abrir el [plan de frontend](specs/docs/tasks/frontend.md) se tomaron estas decisiones, que **nadie del equipo ha revisado todavía**:

| Asunto | Decisión |
|---|---|
| Router de Next.js 14 | App Router, no Pages Router |
| Componentes por defecto | Server Component; `'use client'` solo con estado o interacción |
| Datos en lectura inicial | `fetch` nativo desde Server Components |
| Mutaciones y refetch | TanStack Query en Client Components |
| Estado de sesión/rol en el cliente | Ninguno persistido; cada acción sensible se revalida contra el backend |

Detalle completo, con el porqué de cada una, en [`specs/docs/tasks/frontend.md`](specs/docs/tasks/frontend.md#decisiones-que-fija-este-plan). Si el equipo las corrige, se corrige ese documento primero, igual que un contrato.

---

## Shell autenticado — tres preguntas abiertas (29 de septiembre, pendiente de revisión)

Al cerrar [`specs/ui/layout.md`](specs/ui/layout.md) (`FE-05`) quedaron tres puntos decididos con el criterio más barato/reversible disponible, no porque fueran obvios. **Nadie del equipo los ha revisado todavía:**

| Asunto | Decisión tomada | Alternativa, y su costo |
|---|---|---|
| Estado de sesión en la cabecera | Mostrar `correo · rol` | Mostrar el nombre real exige que `FE-06` llame también a `GET /api/perfil` (módulo `usuarios`), una dependencia que hoy no tiene |
| Marca o rótulo en la cabecera | Ninguno | Ningún token ni artifact respalda un logo todavía; añadirlo sería una decisión de contenido, no de layout |
| Contador de notificaciones en la navegación | Ninguno | Necesita un componente de badge que `components.md` aún no especifica («Badge de estado/rol: Pendiente») |

Ninguna de las tres es estructural: cambiar cualquiera es un ajuste de contenido o una dependencia nueva declarada, no una reescritura del shell. Detalle en [`specs/ui/layout.md`](specs/ui/layout.md#ubicación-de-elementos).

---

## Estado del proyecto

Los siete bloques de corrección están ejecutados y subidos. Los cinco contratos existentes quedaron cotejados contra los modelos de datos, las reglas y los flujos, y las inconsistencias que ese cotejo encontró están corregidas.

El proyecto documenta hoy **513 reglas de negocio, 82 flujos de usuario y 77 endpoints** en 51 documentos.

Las comprobaciones automáticas salen sin errores:

- ninguna referencia a una regla o un flujo que no exista;
- ninguna tabla citada sin definición en ningún modelo;
- ningún permiso ni código de error fuera de su catálogo;
- ningún enlace roto;
- 75 de los 82 flujos cubiertos por algún endpoint. Los 7 restantes pertenecen a los cuatro módulos sin contrato.

Todo lo anterior es especificación. Estas comprobaciones verifican que los documentos son coherentes entre sí, no que exista implementación.
