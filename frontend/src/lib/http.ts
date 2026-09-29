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
 * - Sin reintento en `401`: una sesión vencida o revocada se propaga como
 *   `ApiRequestError` para que quien llame decida (p. ej. redirigir a
 *   login), nunca se reintenta la misma petición con credenciales viejas.
 */

const MUTATING_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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
