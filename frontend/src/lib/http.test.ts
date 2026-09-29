import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiRequest, ApiRequestError } from "./http";

// FE-27: un 401 NO_AUTENTICADO en el navegador renueva la sesión una vez y repite la petición.
const respuesta = (status: number, cuerpo: unknown) =>
  Promise.resolve(new Response(JSON.stringify(cuerpo), { status, headers: { "Content-Type": "application/json" } }));
const NO_AUTENTICADO = { error: { codigo: "NO_AUTENTICADO", mensaje: "Se requiere una sesión válida.", detalles: [] } };

describe("apiRequest: renovación de sesión", () => {
  const fetchMock = vi.fn();
  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
    document.cookie = "rp_csrf=token-de-prueba";
  });

  it("renueva y repite la petición original cuando el acceso venció", async () => {
    fetchMock
      .mockImplementationOnce(() => respuesta(401, NO_AUTENTICADO)) // GET original
      .mockImplementationOnce(() => respuesta(200, {})) // POST renovación
      .mockImplementationOnce(() => respuesta(200, { datos: [1] })); // GET repetido
    await expect(apiRequest("/api/notificaciones")).resolves.toEqual({ datos: [1] });
    const rutas = fetchMock.mock.calls.map((c) => `${c[1].method} ${c[0]}`);
    expect(rutas).toEqual([
      "GET /api/notificaciones",
      "POST /api/auth/sesiones/renovacion",
      "GET /api/notificaciones",
    ]);
    expect(fetchMock.mock.calls[1][1].headers["X-CSRF-Token"]).toBe("token-de-prueba");
  });

  it("si la renovación falla, propaga el 401 original y no reintenta", async () => {
    fetchMock
      .mockImplementationOnce(() => respuesta(401, NO_AUTENTICADO))
      .mockImplementationOnce(() => respuesta(401, NO_AUTENTICADO)); // renovación rechazada
    await expect(apiRequest("/api/notificaciones")).rejects.toMatchObject({ status: 401 });
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("varias peticiones vencidas a la vez comparten una sola renovación", async () => {
    let renovaciones = 0;
    fetchMock.mockImplementation((url: string) => {
      if (url.endsWith("/renovacion")) {
        renovaciones += 1;
        return respuesta(200, {});
      }
      // La primera vez de cada ruta vence; la repetida responde bien.
      const yaVencio = fetchMock.mock.calls.filter((c) => c[0] === url).length > 1;
      return yaVencio ? respuesta(200, { ok: url }) : respuesta(401, NO_AUTENTICADO);
    });
    await Promise.all([apiRequest("/api/reservas"), apiRequest("/api/recursos")]);
    expect(renovaciones).toBe(1);
  });

  it("un login con credenciales inválidas no dispara renovación", async () => {
    fetchMock.mockImplementationOnce(() => respuesta(401, NO_AUTENTICADO));
    await expect(
      apiRequest("/api/auth/sesiones", { method: "POST", body: { correo: "a", contrasena: "b" } })
    ).rejects.toBeInstanceOf(ApiRequestError);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("un error distinto de NO_AUTENTICADO no renueva", async () => {
    fetchMock.mockImplementationOnce(() => respuesta(403, { error: { codigo: "NO_AUTORIZADO", mensaje: "x", detalles: [] } }));
    await expect(apiRequest("/api/reservas")).rejects.toMatchObject({ status: 403 });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
