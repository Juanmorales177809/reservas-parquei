import fs from 'node:fs';
import path from 'node:path';

import { request, type FullConfig } from '@playwright/test';

import { USUARIOS, type RolUsuario } from './data/usuarios';

const BACKEND = 'http://localhost:8000';
const DIR_AUTH = path.join(__dirname, '.auth');

/**
 * Prepara el entorno E2E de forma determinista:
 * 1. Valida que el backend responde.
 * 2. Garantiza un recurso activo en el primer espacio sembrado.
 * 3. Crea los usuarios ficticios de gestor y usuario (el admin lo crea el
 *    lifespan vía INITIAL_ADMIN_*).
 * 4. Genera storageState por rol bajo e2e/.auth/ (directorio ignorado).
 *
 * No usa credenciales reales y nunca toca bases de desarrollo o producción.
 */
export default async function globalSetup(_config: FullConfig) {
  const admin = await request.newContext({ baseURL: BACKEND });
  try {
    const adminToken = await iniciarSesion(admin, 'admin');

    const espacios = (await admin.get('/espacios', { headers: autorizacion(adminToken) })).ok()
      ? ((await (await admin.get('/espacios', { headers: autorizacion(adminToken) })).json()) as Array<{
          id: number;
          estado: string;
        }>)
      : [];
    if (espacios.length === 0) {
      throw new Error('No hay espacios sembrados en la base de pruebas');
    }
    // Elegir un espacio ACTIVO: el admin ve todos (RN-005) y el listado
    // ordenado por nombre puede empezar por un espacio inactivo del seed.
    const activo = espacios.find((espacio) => espacio.estado === 'activo');
    if (!activo) {
      throw new Error('No hay espacios activos sembrados en la base de pruebas');
    }
    const espacioId: number = activo.id;

    const recursosResp = await admin.get(`/recursos?espacio_id=${espacioId}`, {
      headers: autorizacion(adminToken),
    });
    const recursos: unknown[] = await recursosResp.json();
    if (recursos.length === 0) {
      const creado = await admin.post('/recursos', {
        headers: autorizacion(adminToken),
        data: {
          nombre: 'Recurso E2E',
          tipo_recurso_id: 1,
          descripcion: 'Recurso de pruebas E2E',
          capacidad: 10,
          estado: 'activo',
          espacio_id: espacioId,
        },
      });
      if (!creado.ok()) throw new Error(`No se pudo crear el recurso E2E: ${creado.status()}`);
    }

    await crearUsuarioSiFalta(admin, adminToken, USUARIOS.gestor, espacioId);
    await crearUsuarioSiFalta(admin, adminToken, USUARIOS.usuario, null);
  } finally {
    await admin.dispose();
  }

  fs.mkdirSync(DIR_AUTH, { recursive: true });
  await guardarStorageState('admin');
  await guardarStorageState('gestor');
  await guardarStorageState('usuario');
}

async function iniciarSesion(ctx: import('@playwright/test').APIRequestContext, rol: RolUsuario) {
  const respuesta = await ctx.post('/auth/login', {
    data: { username: USUARIOS[rol].username, password: USUARIOS[rol].password },
  });
  if (!respuesta.ok()) {
    throw new Error(`Login API de ${rol} falló: ${respuesta.status()}`);
  }
  return ((await respuesta.json()) as { access_token: string }).access_token;
}

function autorizacion(token: string) {
  return { Authorization: `Bearer ${token}` };
}

async function crearUsuarioSiFalta(
  ctx: import('@playwright/test').APIRequestContext,
  adminToken: string,
  usuario: { username: string; email: string; password: string; rol: string },
  espacioId: number | null,
) {
  const respuesta = await ctx.post('/usuarios', {
    headers: autorizacion(adminToken),
    data: {
      username: usuario.username,
      email: usuario.email,
      password: usuario.password,
      rol: usuario.rol,
      ...(espacioId !== null ? { espacio_id: espacioId } : {}),
    },
  });
  if (!respuesta.ok() && respuesta.status() !== 409) {
    throw new Error(`No se pudo crear ${usuario.rol} ${usuario.username}: ${respuesta.status()}`);
  }
}

/** Construye el storageState a partir del login real por API (Fase 9F-B):
 *  el backend fija la cookie HttpOnly `access_token` en la respuesta de
 *  POST /auth/login (backend/app/api/auth.py); Playwright la captura sola
 *  en el cookie-jar de este APIRequestContext. La cookie se obtiene contra
 *  BACKEND (:8000) sin Domain explícito, pero las cookies no se distinguen
 *  por puerto (RFC 6265): la misma cookie autentica igual cuando el
 *  navegador visite el frontend en :3000 (baseURL de playwright.config.ts).
 *  ctx.storageState() vuelca ese cookie-jar directamente al formato que
 *  Playwright espera — ya no hay que construir localStorage a mano. */
async function guardarStorageState(rol: RolUsuario) {
  const ctx = await request.newContext({ baseURL: BACKEND });
  try {
    await iniciarSesion(ctx, rol);
    // Verificación de humo: confirma que la cookie recién obtenida
    // autentica de verdad (sin header Authorization) antes de persistirla.
    const meResp = await ctx.get('/usuarios/me');
    if (!meResp.ok()) throw new Error(`GET /usuarios/me de ${rol} falló: ${meResp.status()}`);

    const storageState = await ctx.storageState();
    fs.writeFileSync(path.join(DIR_AUTH, `${rol}.json`), JSON.stringify(storageState, null, 2));
  } finally {
    await ctx.dispose();
  }
}
