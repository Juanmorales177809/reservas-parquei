import { expect, request, test as base } from '@playwright/test';

import { USUARIOS, type RolUsuario } from '../data/usuarios';

export const test = base.extend<{
  backend: import('@playwright/test').APIRequestContext;
}>({
  backend: async ({}, use) => {
    const ctx = await request.newContext({ baseURL: 'http://localhost:8000' });
    await use(ctx);
    await ctx.dispose();
  },
});

export { expect };

/** Ejecuta el archivo únicamente en los proyectos indicados (por rol). */
export function solo(proyectos: string[]) {
  test.beforeEach(async ({}, testInfo) => {
    test.skip(
      !proyectos.includes(testInfo.project.name),
      `Solo para los proyectos: ${proyectos.join(', ')}`,
    );
  });
}

/** Login real por API para un rol ficticio (Fase 9G, cookie-only).
 *  Deja la cookie HttpOnly `access_token` en el jar del contexto: las
 *  peticiones siguientes del mismo `backend` autentican sin headers. No se
 *  extrae ni reenvía `access_token`. */
export async function iniciarSesionApi(
  backend: import('@playwright/test').APIRequestContext,
  rol: RolUsuario,
): Promise<void> {
  const respuesta = await backend.post('/auth/login', {
    data: { username: USUARIOS[rol].username, password: USUARIOS[rol].password },
  });
  if (!respuesta.ok()) throw new Error(`Login API de ${rol} falló: ${respuesta.status()}`);
}

/** Primer recurso activo del entorno E2E (creado por global-setup). */
export async function primerRecurso(backend: import('@playwright/test').APIRequestContext) {
  const respuesta = await backend.get('/recursos');
  const recursos = (await respuesta.json()) as Array<{ id: number; espacio_id: number }>;
  if (recursos.length === 0) throw new Error('No hay recursos en la base de pruebas');
  return recursos[0];
}

/** Creación de reserva directa por API (payload nuevo 12C-6: `recurso_ids`
 *  y `zona_ids`; nunca `recurso_id`). El contexto debe estar autenticado
 *  con cookie vía `iniciarSesionApi`. */
export async function crearReservaApi(
  backend: import('@playwright/test').APIRequestContext,
  datos: {
    recurso_ids?: number[];
    zona_ids?: number[];
    fecha: string;
    hora_inicio: string;
    hora_fin: string;
    asistentes?: number;
  },
) {
  return backend.post('/reservas', {
    data: { recurso_ids: [], zona_ids: [], asistentes: 1, ...datos },
  });
}