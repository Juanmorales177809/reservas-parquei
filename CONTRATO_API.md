# Contrato institucional de integración

Este documento fija el resultado observable del ejercicio. La solución debe leer los registros entregados, convertir los que correspondan al contrato institucional, validarlos localmente y comunicarlos mediante HTTP. No prescribe una arquitectura ni una técnica de pruebas.

## Registro normalizado

Cada registro que pueda convertirse al contrato debe contener los campos institucionales requeridos por el servicio. `origen` admite únicamente estos valores exactos:

- `LIA`
- `RESERVAS`
- `OTRO`

`pais` utiliza un código de país ISO 3166-1 alpha-2, en mayúsculas. `fecha_hora` debe entregarse en formato ISO 8601 y conservar la zona horaria cuando esté disponible en el dato de origen. No se debe inventar una zona horaria ausente; su tratamiento debe ser consistente con la decisión documentada por la solución.

Puede conservarse internamente un identificador de trazabilidad derivado de `provider_record_id`, `record_code` o equivalente. Ese identificador no debe enviarse a la API si no forma parte del contrato institucional.

## Resultados del procesamiento

Las categorías son independientes y deben contabilizarse sin ambigüedad:

- `procesados`: cantidad total de registros leídos desde las fuentes de entrada, incluidos los que terminen con error.
- `normalizados`: registros que fueron convertidos exitosamente al contrato institucional y quedaron escritos en `normalizadas.json`.
- `errores_normalizacion`: registros que no pudieron convertirse al contrato; deben registrarse con la causa y no aparecer en `normalizadas.json`.
- `validos_localmente`: registros normalizados que cumplen las reglas locales antes del envío.
- `rechazados_localmente`: registros normalizados que incumplen una regla de negocio local; permanecen en `normalizadas.json`, pero no se envían.
- `enviados`: solicitudes HTTP realizadas para registros válidos localmente. Cada intento cuenta como una solicitud realizada.
- `aceptados_api`: registros aceptados por la API con una respuesta exitosa definida por el contrato.
- `rechazados_api`: registros que la API rechaza, incluidos los que reciben `409` por conflicto de registro existente.
- `errores_comunicacion`: registros cuyo envío no obtiene una respuesta HTTP utilizable por error de red, timeout o respuesta `5xx` después de agotar los reintentos.

Los conteos deben permitir distinguir un registro normalizado de uno válido localmente y de uno aceptado por la API.

## Clasificación de errores

- **Error de lectura:** no fue posible leer una fuente o interpretar su contenido de entrada. El registro o fuente afectada no se considera normalizado.
- **Error de normalización:** el registro no puede convertirse al contrato institucional. No aparece en `normalizadas.json`.
- **Rechazo en validación local:** el registro sí fue normalizado, permanece en `normalizadas.json`, pero incumple una regla de negocio y no se envía.
- **Rechazo de API:** la API responde indicando que el registro no es aceptable. Un `409` significa que el registro ya existe o entra en conflicto; no es una aceptación.
- **Error de comunicación:** no se obtiene una respuesta HTTP utilizable por error de red, timeout o respuesta `5xx`.

Las respuestas `4xx` no se reintentan automáticamente. Las respuestas `5xx`, los errores de red y los timeouts sí pueden reintentarse.

Para cada registro se permite un intento inicial y hasta dos reintentos adicionales: máximo tres solicitudes HTTP por registro. Los reintentos no convierten un rechazo en aceptación.

Los códigos HTTP no contemplados deben registrarse con el registro afectado y manejarse de forma controlada, sin terminar abruptamente el programa. Si la respuesta no es JSON, debe conservarse al menos el código HTTP y el cuerpo de texto disponible.

## Servicio y configuración de ejecución

`URL_BASE` y `EQUIPO` se suministran como variables de entorno. `URL_BASE` identifica el servicio HTTP contra el que se ejecuta la integración y `EQUIPO` identifica el conjunto o equipo institucional seleccionado por el ejercicio. La misma configuración debe utilizarse durante todo el procesamiento.

La ejecución mínima esperada es:

```bash
python programa.py
pytest
```

Las pruebas deben ser independientes de la API real. El mecanismo concreto para aislar las solicitudes queda abierto, siempre que las pruebas sean reproducibles y verifiquen las clasificaciones y conteos definidos aquí.

## Decisiones abiertas

Se dejan abiertas la estructura interna de los datasets, la selección de archivos de entrada, la ruta concreta del recurso HTTP, la forma de documentar una zona horaria ausente y la organización interna del programa. Estas decisiones son válidas solo si no alteran los campos, valores, clasificaciones, reintentos y conteos definidos en este contrato.
