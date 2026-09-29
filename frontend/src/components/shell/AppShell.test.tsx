import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { ContextoSesion } from "@/src/lib/auth";
import { apiRequest } from "@/src/lib/http";
import { AppShell } from "./AppShell";

vi.mock("next/navigation", () => ({
  usePathname: () => "/reservas",
}));

vi.mock("@/src/lib/http", () => ({
  apiRequest: vi.fn().mockResolvedValue(undefined),
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

describe("AppShell", () => {
  it("USUARIO no ve Usuarios, Administración ni Reportes", () => {
    render(
      <AppShell sesion={sesionDeEjemplo("USUARIO")}>
        <p>Pantalla</p>
      </AppShell>
    );

    expect(screen.getByRole("link", { name: "Reservas" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Usuarios" })).toBeNull();
    expect(screen.queryByRole("link", { name: "Administración" })).toBeNull();
    expect(screen.queryByRole("link", { name: "Reportes" })).toBeNull();
  });

  it("TECNICO ve Reportes pero no Usuarios ni Administración", () => {
    render(
      <AppShell sesion={sesionDeEjemplo("TECNICO")}>
        <p>Pantalla</p>
      </AppShell>
    );

    expect(screen.getByRole("link", { name: "Reportes" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Usuarios" })).toBeNull();
    expect(screen.queryByRole("link", { name: "Administración" })).toBeNull();
  });

  it("ADMINISTRADOR ve los ocho destinos", () => {
    render(
      <AppShell sesion={sesionDeEjemplo("ADMINISTRADOR")}>
        <p>Pantalla</p>
      </AppShell>
    );

    for (const etiqueta of [
      "Reservas",
      "Recursos",
      "Espacios",
      "Investigación",
      "Usuarios",
      "Administración",
      "Notificaciones",
      "Reportes",
    ]) {
      expect(screen.getByRole("link", { name: etiqueta })).toBeInTheDocument();
    }
  });

  it("el botón Menú abre el panel superpuesto con los destinos y el estado de sesión", async () => {
    const user = userEvent.setup();
    render(
      <AppShell sesion={sesionDeEjemplo("USUARIO")}>
        <p>Pantalla</p>
      </AppShell>
    );

    // Antes de abrirlo, solo existe la navegación persistente de escritorio.
    expect(screen.getAllByRole("link", { name: "Reservas" })).toHaveLength(1);

    await user.click(screen.getByRole("button", { name: "Menú" }));

    // Al abrirlo se monta también el panel superpuesto: ahora hay dos.
    expect(screen.getAllByRole("link", { name: "Reservas" })).toHaveLength(2);
    expect(
      screen.getAllByText(/persona@correo\.itm\.edu\.co/).length
    ).toBeGreaterThan(0);
  });

  it("Cerrar sesión llama DELETE /api/auth/sesiones/actual", async () => {
    const originalLocation = window.location;
    // jsdom no implementa la navegación real; se sustituye para no ensuciar
    // la prueba con su error de "not implemented" al asignar `href`.
    Object.defineProperty(window, "location", {
      configurable: true,
      value: { ...originalLocation, href: "" },
    });

    const user = userEvent.setup();
    render(
      <AppShell sesion={sesionDeEjemplo("USUARIO")}>
        <p>Pantalla</p>
      </AppShell>
    );

    await user.click(screen.getByRole("button", { name: "Cerrar sesión" }));

    expect(apiRequest).toHaveBeenCalledWith("/api/auth/sesiones/actual", {
      method: "DELETE",
    });
    expect(window.location.href).toBe("/login");

    Object.defineProperty(window, "location", {
      configurable: true,
      value: originalLocation,
    });
  });
});
