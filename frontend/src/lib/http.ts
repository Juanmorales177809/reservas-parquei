/**
 * Cliente HTTP hacia el backend.
 *
 * Contrato: specs/contratos/README.md §2 (envolvente de error) y
 * specs/contratos/auth/api-contract.md §2 (cookies de sesión y CSRF de
 * doble envío).
 *
 * - La sesión (`rp_access`/`rp_refresh`, ambas HttpOnly) viaja sola: el
 *   navegador la adjunta con `credentials: "include"`. Este módulo nunca
 *   lee ni almacena esas cookies.
 * - Toda mutación exige `X-CSRF-Token` con el valor de la cookie legible
 *   `rp_csrf`, obtenida primero de `GET /api/auth/csrf` si aún no existe.
 * - El cuerpo viaja como JSON, salvo `FormData` (importaciones), que se
 *   envía tal cual para que el navegador fije el boundary multipart.
 * - `401 NO_AUTENTICADO` en el navegador: se renueva la sesión una sola vez
 *   (`POST /api/auth/sesiones/renovacion`, que rota las cookies) y solo si
 *   la renovación tuvo éxito se repite la petición original, ya con las
 *   credenciales nuevas — nunca con las viejas (FE-27). Si la renovación
 *   falla, el `401` original se propaga para que quien llame lleve a login.
 *   Un Server Component no renueva: no recibe `rp_refresh` (su `Path` es
 *   `/api/auth/sesiones`); por eso `AppShell` renueva antes de que venza.
 */

const MUTATING_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);

// En el navegador las peticiones van al mismo origen (`/api/...`) y Next las reenvía
// al backend (rewrite de next.config.mjs): así no hace falta CORS y las cookies de
// sesión son de primera parte. Un Server Component no tiene origen, así que llama al
// backend directamente por BACKEND_URL. NEXT_PUBLIC_API_URL fuerza otro destino.
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  (typeof window === "undefined" ? (process.env.BACKEND_URL ?? "http://localhost:8000") : "");

/** Forma exacta de contratos/README.md §2 — nunca trazas, SQL ni secretos. */
export interface ApiError {
  codigo: string;
  mensaje: string;
  detalles: unknown[];
}

export class ApiRequestError extends Error {
  readonly status: number;
  readonly error: ApiError;

  constructor(status: number, error: ApiError) {
    super(error.mensaje);
    this.name = "ApiRequestError";
    this.status = status;
    this.error = error;
  }
}

function leerCookie(nombre: string): string | undefined {
  if (typeof document === "undefined") return undefined;
  const coincidencia = document.cookie.match(
    new RegExp(`(?:^|; )${nombre}=([^;]*)`)
  );
  return coincidencia ? decodeURIComponent(coincidencia[1]) : undefined;
}

/**
 * Obtiene el token CSRF vigente, pidiendo uno nuevo a `GET /api/auth/csrf`
 * si la cookie `rp_csrf` todavía no existe. Esa ruta es pública y no tiene
 * efecto sobre el estado del sistema (api-contract.md §3.0).
 */
async function obtenerTokenCsrf(): Promise<string> {
  let token = leerCookie("rp_csrf");
  if (!token) {
    await fetch(`${API_BASE_URL}/api/auth/csrf`, {
      method: "GET",
      credentials: "include",
    });
    token = leerCookie("rp_csrf");
  }
  if (!token) {
    throw new Error("No se pudo obtener el token CSRF (GET /api/auth/csrf no devolvió la cookie rp_csrf).");
  }
  return token;
}

// Rutas donde un 401 significa otra cosa (credenciales inválidas, token de un solo uso...) o donde
// renovar no tiene sentido: nunca disparan una renovación.
const RUTAS_SIN_RENOVACION = ["/api/auth/csrf", "/api/auth/registro", "/api/auth/recuperacion", "/api/auth/invitaciones", "/api/auth/reautenticacion"];

function sinRenovacion(path: string): boolean {
  const limpio = path.split("?")[0];
  return (
    limpio === "/api/auth/sesiones" || // login
    limpio === "/api/auth/sesiones/renovacion" ||
    RUTAS_SIN_RENOVACION.some((r) => limpio === r || limpio.startsWith(`${r}/`))
  );
}

let renovacionEnCurso: Promise<boolean> | null = null;

/**
 * Renueva el acceso con la cookie `rp_refresh`. Varias peticiones que vencen a la vez comparten
 * una sola renovación: el refresco rota y una segunda llamada lo invalidaría.
 */
export function renovarSesion(): Promise<boolean> {
  if (typeof document === "undefined") return Promise.resolve(false);
  if (!renovacionEnCurso) {
    renovacionEnCurso = (async () => {
      try {
        const token = await obtenerTokenCsrf();
        const respuesta = await fetch(`${API_BASE_URL}/api/auth/sesiones/renovacion`, {
          method: "POST",
          credentials: "include",
          headers: { "X-CSRF-Token": token },
        });
        return respuesta.ok;
      } catch {
        return false;
      }
    })().finally(() => {
      renovacionEnCurso = null;
    });
  }
  return renovacionEnCurso;
}

export interface ApiRequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  headers?: Record<string, string>;
  /**
   * Cabecera `Cookie` a reenviar. Solo se usa desde un Server Component,
   * que tiene que leerla explícitamente con `cookies()` de `next/headers`
   * y pasarla aquí — este módulo no importa `next/headers` para poder
   * usarse también desde Client Components.
   */
  cookieHeader?: string;
  /** Uso interno: la petición ya se repitió tras renovar la sesión. */
  yaRenovada?: boolean;
}

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const method = options.method ?? "GET";
  const esFormulario = typeof FormData !== "undefined" && options.body instanceof FormData;
  const headers: Record<string, string> = {
    ...options.headers,
  };
  if (!esFormulario) {
    headers["Content-Type"] = "application/json";
  }

  if (options.cookieHeader) {
    headers["Cookie"] = options.cookieHeader;
  }

  if (MUTATING_METHODS.has(method)) {
    if (typeof document === "undefined") {
      throw new Error(
        "Las mutaciones solo se ejecutan desde el cliente: necesitan el token CSRF del navegador. " +
          "Un Server Component no debe llamar a apiRequest con un método distinto de GET."
      );
    }
    headers["X-CSRF-Token"] = await obtenerTokenCsrf();
  }

  const respuesta = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    credentials: "include",
    cache: "no-store",
    body:
      options.body !== undefined
        ? esFormulario
          ? (options.body as FormData)
          : JSON.stringify(options.body)
        : undefined,
  });

  if (respuesta.status === 204) {
    return undefined as T;
  }

  const cuerpo = await respuesta.json().catch(() => null);

  if (
    respuesta.status === 401 &&
    !options.yaRenovada &&
    !options.cookieHeader &&
    typeof document !== "undefined" &&
    cuerpo?.error?.codigo === "NO_AUTENTICADO" &&
    !sinRenovacion(path) &&
    (await renovarSesion())
  ) {
    return apiRequest<T>(path, { ...options, yaRenovada: true });
  }

  if (!respuesta.ok) {
    const error: ApiError = cuerpo?.error ?? {
      codigo: "ERROR_INTERNO",
      mensaje: "Error no controlado.",
      detalles: [],
    };
    throw new ApiRequestError(respuesta.status, error);
  }

  return cuerpo as T;
}
