import 'package:flutter/material.dart';

import '../domain/enums.dart';

/// Gradientes de cabecera de tarjeta de espacio (no hay fotografía real en
/// este sistema; el gradiente + icono es la identidad visual de la
/// entidad).
///
/// **Cambio de Fase 6**: antes se elegían por `id % 6`, así que el mismo
/// laboratorio aparecía azul en una lista y naranja en otra según su
/// posición — el gradiente no era información, era textura aleatoria
/// (exactamente lo que se rechazó del estilo "arcoíris", solo con menos
/// saturación). Ahora se atan a `modalidad_reserva`, que es un atributo
/// real, estable y semántico del backend (`ModalidadEspacio`): el color
/// pasa a ser un identificador aprendible.
///
/// Nota: la revisión de diseño sugería atarlos al *tipo* de espacio
/// (laboratorio/auditorio/sala), pero `EspacioResponse` no tiene ese
/// campo y agregarlo implicaría tocar el backend (prohibido sin
/// aprobación aparte). `modalidad_reserva` es la señal semántica más
/// cercana que ya existe.
///
/// Los tres tienen el mismo delta de luminosidad y el mismo ángulo (135°,
/// superior-izquierda → inferior-derecha) para que se lean como una
/// familia y ninguno parezca "deshabilitado" al lado de otro.
LinearGradient gradientePara(ModalidadEspacio modalidad) {
  final colores = switch (modalidad) {
    ModalidadEspacio.equipos => const [Color(0xFF1E3A8A), Color(0xFF3B82F6)],
    ModalidadEspacio.zonas => const [Color(0xFF0F766E), Color(0xFF2DD4BF)],
    ModalidadEspacio.mixto => const [Color(0xFF312E81), Color(0xFF4F46E5)],
  };
  return LinearGradient(
    colors: colores,
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}

/// Etiqueta en español de la modalidad — el gradiente solo comunica si se
/// puede nombrar en algún lado (leyenda, chip de filtro, detalle).
String modalidadLabel(ModalidadEspacio modalidad) => switch (modalidad) {
      ModalidadEspacio.equipos => 'Equipos',
      ModalidadEspacio.zonas => 'Zonas',
      ModalidadEspacio.mixto => 'Mixto',
    };

/// Velo oscuro sobre el extremo claro del gradiente, para que un badge o
/// icono blanco siga siendo legible sobre cualquier punto de la cabecera.
/// Sin esto, el badge blanco sobre `#4F46E5`/`#2DD4BF` pierde definición.
const kGradientScrim = LinearGradient(
  begin: Alignment.centerLeft,
  end: Alignment.centerRight,
  colors: [Color(0x00000000), Color(0x1F000000)],
);
