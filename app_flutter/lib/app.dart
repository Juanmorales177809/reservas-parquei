import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';

class ReservasApp extends ConsumerWidget {
  const ReservasApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(goRouterProvider);
    return MaterialApp.router(
      title: 'Reservas Parquei',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      // Fijado a claro a propósito: la identidad "tech-clean" académica se
      // diseñó entera en claro y no existe todavía un tema oscuro
      // verificado (ver `AppTheme.dark`). Sin esto, `ThemeMode.system`
      // haría que cualquier dispositivo en modo oscuro renderice una
      // variante que nadie revisó.
      themeMode: ThemeMode.light,
      routerConfig: router,
    );
  }
}
