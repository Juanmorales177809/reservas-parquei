import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ContextoSesion } from "@/src/lib/auth-types";
import AppLayout from "./layout";

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
  usePathname: () => "/reservas",
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
    autenticacion_reciente: false,
  };
}

describe("AppLayout ((app)/layout.tsx)", () => {
  beforeEach(() => {
    obtenerSesionActualMock.mockReset();
  });

  it("sin sesión válida, redirige a /login sin pintar contenido protegido", async () => {
    obtenerSesionActualMock.mockResolvedValue(null);

    await expect(
      AppLayout({ children: <div>Contenido protegido</div> })
    ).rejects.toThrow("NEXT_REDIRECT:/login?motivo=sesion_vencida");
  });

  it("con sesión válida, pinta el shell y el contenido de la ruta", async () => {
    obtenerSesionActualMock.mockResolvedValue(sesionDeEjemplo("USUARIO"));

    const jsx = await AppLayout({ children: <div>Contenido protegido</div> });
    render(jsx);

    expect(screen.getByText("Contenido protegido")).toBeInTheDocument();
    expect(screen.getByText(/persona@correo\.itm\.edu\.co/)).toBeInTheDocument();
  });
});
