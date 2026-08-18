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

/** Login por API y headers de autorización para un rol ficticio. */
export async function headersPara(
  backend: import('@playwright/test').APIRequestContext,
  rol: RolUsuario,
): Promise<{ Authorization: string }> {
  const respuesta = await backend.post('/auth/login', {
    data: { username: USUARIOS[rol].username, password: USUARIOS[rol].password },
  });
  if (!respuesta.ok()) throw new Error(`Login API de ${rol} falló: ${respuesta.status()}`);
  const { access_token } = (await respuesta.json()) as { access_token: string };
  return { Authorization: `Bearer ${access_token}` };
}

/** Primer recurso activo del entorno E2E (creado por global-setup). */
export async function primerRecurso(backend: import('@playwright/test').APIRequestContext) {
  const respuesta = await backend.get('/recursos');
  const recursos = (await respuesta.json()) as Array<{ id: number; espacio_id: number }>;
  if (recursos.length === 0) throw new Error('No hay recursos en la base de pruebas');
  return recursos[0];
}

/** Creación de reserva directa por API (payload nuevo 12C-6: `recurso_ids`
 *  y `zona_ids`; nunca `recurso_id`). */
export async function crearReservaApi(
  backend: import('@playwright/test').APIRequestContext,
  headers: { Authorization: string },
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
    headers,
    data: { recurso_ids: [], zona_ids: [], asistentes: 1, ...datos },
  });
}
