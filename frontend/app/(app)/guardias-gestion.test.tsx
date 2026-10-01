import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ContextoSesion } from "@/src/lib/auth-types";
import EspaciosLayout from "./espacios/layout";
import LaboratoriosLayout from "./laboratorios/layout";
import RecursosLayout from "./recursos/layout";

const obtenerSesionActualMock = vi.fn<() => Promise<ContextoSesion | null>>();

vi.mock("@/src/lib/auth", () => ({ obtenerSesionActual: () => obtenerSesionActualMock() }));
vi.mock("next/navigation", () => ({
  redirect: (url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  },
}));

const sesion = (rol: ContextoSesion["rol"]): ContextoSesion => ({
  id_cuenta: 1,
  tipo_cuenta: rol === "USUARIO" ? "USUARIO" : "PERSONAL",
  rol,
  correo: "persona@itm.edu.co",
  actualizacion_inicial_pendiente: null,
  id_sesion: "s",
  unidades_autorizadas: rol === "ADMINISTRADOR" ? "GLOBAL" : [],
  autenticacion_reciente: false,
});

// Decisión 2026-10-01: el usuario solo reserva; recursos, espacios y la configuración de un laboratorio son de
// quien gestiona.
describe.each([
  ["recursos", RecursosLayout],
  ["espacios", EspaciosLayout],
  ["laboratorios", LaboratoriosLayout],
])("guardia de /%s", (_nombre, Layout) => {
  beforeEach(() => obtenerSesionActualMock.mockReset());

  it("sin sesión, va al inicio de sesión", async () => {
    obtenerSesionActualMock.mockResolvedValue(null);
    await expect(Layout({ children: null })).rejects.toThrow("NEXT_REDIRECT:/login?motivo=sesion_vencida");
  });

  it("un usuario vuelve a sus reservas", async () => {
    obtenerSesionActualMock.mockResolvedValue(sesion("USUARIO"));
    await expect(Layout({ children: null })).rejects.toThrow("NEXT_REDIRECT:/reservas");
  });

  it.each(["TECNICO", "ADMINISTRADOR"] as const)("un %s pasa", async (rol) => {
    obtenerSesionActualMock.mockResolvedValue(sesion(rol));
    await expect(Layout({ children: null })).resolves.toBeDefined();
  });
});
