import 'package:flutter/material.dart';

/// Gradiente de cabecera de tarjeta de laboratorio (no hay fotografía real en
/// este sistema; el gradiente + icono es la identidad visual de la
/// entidad).
///
/// **Cambio de Fase 3 de `~/.claude/plans/dazzling-wobbling-zebra.md`**:
/// antes se elegía por `modalidad_reserva` (`ModalidadLaboratorio`, removido
/// por completo en esa fase). Volver a elegirlo por `id % N` reintroduciría
/// exactamente lo que ese cambio de la Fase 6 había rechazado (textura
/// aleatoria, no información) — en vez de eso, se usa un único gradiente
/// fijo con los colores reales de la identidad del ITM (navy/teal, ver
/// `Manual-ITM-V-2025.pdf`, ya usados en `backend/app/services/
/// email_templates.py`), consistente en toda la app.
const kGradienteLaboratorio = LinearGradient(
  colors: [Color(0xFF102D69), Color(0xFF00A0B7)],
  begin: Alignment.topLeft,
  end: Alignment.bottomRight,
);

/// Velo oscuro sobre el extremo claro del gradiente, para que un badge o
/// icono blanco siga siendo legible sobre cualquier punto de la cabecera.
/// Sin esto, el badge blanco sobre `#4F46E5`/`#2DD4BF` pierde definición.
const kGradientScrim = LinearGradient(
  begin: Alignment.centerLeft,
  end: Alignment.centerRight,
  colors: [Color(0x00000000), Color(0x1F000000)],
);
