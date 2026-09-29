import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { ContextoSesion } from "@/src/lib/auth-types";
import InvestigacionLayout from "./layout";

const obtenerSesionActualMock = vi.fn<() => Promise<ContextoSesion | null>>();

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

// FE-17: sin alcance global no se pinta contenido protegido.
describe("InvestigacionLayout ((app)/investigacion/layout.tsx)", () => {
  it("con sesión de TECNICO, redirige sin pintar contenido protegido", async () => {
    obtenerSesionActualMock.mockResolvedValue(sesionDeEjemplo("TECNICO"));

    await expect(
      InvestigacionLayout({ children: <div>Contenido de investigación</div> })
    ).rejects.toThrow("NEXT_REDIRECT:/reservas");
    expect(document.body.textContent ?? "").not.toContain("Contenido de investigación");
  });

  it("con sesión de ADMINISTRADOR, pinta el contenido", async () => {
    obtenerSesionActualMock.mockResolvedValue(sesionDeEjemplo("ADMINISTRADOR"));

    render(await InvestigacionLayout({ children: <div>Contenido de investigación</div> }));
    expect(document.body.textContent ?? "").toContain("Contenido de investigación");
  });
});
