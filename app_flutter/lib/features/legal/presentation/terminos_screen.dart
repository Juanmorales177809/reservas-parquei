import 'package:flutter/material.dart';

import '../../../core/theme/app_spacing.dart';

class TerminosScreen extends StatelessWidget {
  const TerminosScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Términos de uso')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Términos y condiciones', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: AppSpacing.md),
            Text(
              'Al usar Reservas Parquei aceptás las normas de uso de los espacios institucionales. '
              'Las reservas están sujetas a aprobación, respeto de horarios y capacidad, y pueden ser canceladas '
              'si no se cumplen las condiciones. El uso indebido puede derivar en sanciones.\n\n'
              'Este es un placeholder estático — el contenido legal será provisto por la institución.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }
}
