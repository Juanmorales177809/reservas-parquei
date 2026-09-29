import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ContextoSesion } from "@/src/lib/auth-types";
import AdministracionLayout from "./layout";

const obtenerSesionActualMock =
  vi.fn<() => Promise<ContextoSesion | null>>();

vi.mock("@/src/lib/auth", async () => {
  const actual = await vi.importActual<typeof import("@/src/lib/auth")>(
    "@/src/lib/auth"
  );
  return {
    ...actual,
    obtenerSesionActual: () => obtenerSesionActualMock(),
  };
});

vi.mock("next/navigation", () => ({
  redirect: (url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  },
}));

function sesionDeEjemplo(rol: ContextoSesion["rol"]): ContextoSesion {
  return {
    id_cuenta: 1042,
    tipo_cuenta: rol === "USUARIO" ? "USUARIO" : "PERSONAL",
    rol,
    correo: "persona@correo.itm.edu.co",
    actualizacion_inicial_pendiente: null,
    id_sesion: "8f2c1b6e-5a71-4f0c-9a3a-2c9f1d0b7e44",
    unidades_autorizadas: rol === "ADMINISTRADOR" ? "GLOBAL" : [],
    autenticacion_reciente: true,
  };
}

// FE-07: "un intento de acceder a una pantalla de administración sin el
// permiso cuentas.administrar no muestra ni parpadea el contenido
// protegido antes de redirigir".
describe("AdministracionLayout ((app)/administracion/layout.tsx)", () => {
  beforeEach(() => {
    obtenerSesionActualMock.mockReset();
  });

  it("sin sesión válida, redirige a /login sin pintar contenido protegido", async () => {
    obtenerSesionActualMock.mockResolvedValue(null);

    await expect(
      AdministracionLayout({ children: <div>Contenido de administración</div> })
    ).rejects.toThrow("NEXT_REDIRECT:/login");
  });

  it("con sesión de USUARIO, redirige sin pintar contenido protegido", async () => {
    obtenerSesionActualMock.mockResolvedValue(sesionDeEjemplo("USUARIO"));

    await expect(
      AdministracionLayout({ children: <div>Contenido de administración</div> })
    ).rejects.toThrow("NEXT_REDIRECT:/reservas");
  });

  it("con sesión de TECNICO, redirige sin pintar contenido protegido", async () => {
    obtenerSesionActualMock.mockResolvedValue(sesionDeEjemplo("TECNICO"));

    await expect(
      AdministracionLayout({ children: <div>Contenido de administración</div> })
    ).rejects.toThrow("NEXT_REDIRECT:/reservas");
  });

  it("con sesión de ADMINISTRADOR, pinta el contenido", async () => {
    obtenerSesionActualMock.mockResolvedValue(sesionDeEjemplo("ADMINISTRADOR"));

    const jsx = await AdministracionLayout({
      children: <div>Contenido de administración</div>,
    });
    render(jsx);

    expect(screen.getByText("Contenido de administración")).toBeInTheDocument();
  });
});
