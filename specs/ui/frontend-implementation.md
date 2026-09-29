# Implementación frontend

## Propósito

Definir dónde se implementarán los tokens y estilos en el frontend y cómo serán consumidos por Tailwind, los componentes compartidos y las pantallas.

## Estado

`frontend/` todavía no existe en este repositorio (se borró y no tiene tarea abierta en `tasks.md`). Lo que sigue es el objetivo de implementación tomado del artifact de diseño «Botones ITM · Corporativo», para cuando se abra esa tarea — no hay código escrito todavía.

## Ubicación de tokens

Objetivo: los tokens de [Tokens de diseño](design-tokens.md) se implementan como variables CSS (`--color-*`, `--radius`, `--shadow-*`, `--fs-*`, `--fw-*`) en una única hoja global de tokens, con el bloque de overrides de tema oscuro (`prefers-color-scheme: dark` y `data-theme="dark"`) junto a la definición base — no en un archivo aparte.

## Ubicación de estilos

Objetivo: estilos globales (reset mínimo, tipografía base) separados de los estilos por componente. Cada componente compartido resuelve sus propias variantes con clases de Tailwind, sin hojas de estilo propias por componente salvo necesidad puntual (p. ej. la animación del spinner de `Button`).

## Integración con Tailwind

Objetivo, tal como lo deja escrito el artifact: los tokens de color se consumen desde Tailwind por valor literal mapeado a la variable CSS (p. ej. `bg-gradient-to-br from-[#10A83F] to-[#00681F]` para `btn-primary`), no por reimplementación de la paleta en `tailwind.config`. El radio estándar de botón (12px) y la sombra elevada (`--shadow-default/hover/pressed`) se consumen igual, como utilidades de Tailwind parametrizadas con esos mismos valores. Confirmar en la tarea de implementación si conviene además registrar los tokens como `theme.extend` de Tailwind para poder referenciarlos por nombre (`bg-primary-1`) en vez de por valor literal.

## Consumo en componentes compartidos

Objetivo: los componentes compartidos (empezando por `Button`, ver [Componentes UI](components.md#api-objetivo-react)) viven bajo un directorio propio de UI compartida (p. ej. `frontend/src/components/ui/`), resuelven variante/tamaño/estado con utilidades de Tailwind sobre los tokens, y no acceden a valores de color o radio fuera de los documentados en [Tokens de diseño](design-tokens.md).

## Consumo en pantallas

Pendiente: forma de utilizar los componentes compartidos, tokens y estilos en las pantallas, aplicando las reglas de distribución que se definan en [Distribución de la interfaz](layout.md).

## Correspondencia con las especificaciones UI

| Especificación | Se implementa en |
|---|---|
| [Tokens de diseño](design-tokens.md) | Hoja global de variables CSS (ver «Ubicación de tokens») |
| [Sistema de diseño](design-system.md) | Reglas aplicadas dentro de cada componente compartido, no en un archivo propio |
| [Componentes UI](components.md) | `frontend/src/components/ui/` (objetivo) |
| [Distribución de la interfaz](layout.md) | Pendiente, junto con esa especificación |
