import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { ContextoSesion } from "@/src/lib/auth-types";
import { apiRequest } from "@/src/lib/http";
import { AppShell } from "./AppShell";

// Router estable: un objeto nuevo por render relanzaría los efectos sin fin.
const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({
  usePathname: () => "/reservas",
  useRouter: () => router,
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
  // Decisión 2026-10-01: el usuario solo reserva, el técnico gestiona su laboratorio y el administrador todo.
  // «Inicio» es el aterrizaje tras el login para los tres roles (FE-47).
  it("USUARIO solo ve Inicio y Reservas", () => {
    render(
      <AppShell sesion={sesionDeEjemplo("USUARIO")}>
        <p>Pantalla</p>
      </AppShell>
    );

    for (const visible of ["Inicio", "Reservas"]) {
      expect(screen.getByRole("link", { name: visible })).toBeInTheDocument();
    }
    for (const oculto of ["Recursos", "Espacios", "Investigación", "Usuarios", "Administración", "Reportes", "Notificaciones"]) {
      expect(screen.queryByRole("link", { name: oculto })).toBeNull();
    }
  });

  it("TECNICO ve Inicio, Reservas, Recursos, Espacios y Reportes, y nada global", () => {
    render(
      <AppShell sesion={sesionDeEjemplo("TECNICO")}>
        <p>Pantalla</p>
      </AppShell>
    );

    for (const visible of ["Inicio", "Reservas", "Recursos", "Espacios", "Reportes"]) {
      expect(screen.getByRole("link", { name: visible })).toBeInTheDocument();
    }
    for (const oculto of ["Investigación", "Usuarios", "Administración"]) {
      expect(screen.queryByRole("link", { name: oculto })).toBeNull();
    }
  });

  it("ADMINISTRADOR ve los ocho destinos; las notificaciones son la campanita, no un destino", () => {
    render(
      <AppShell sesion={sesionDeEjemplo("ADMINISTRADOR")}>
        <p>Pantalla</p>
      </AppShell>
    );

    for (const etiqueta of ["Inicio", "Reservas", "Recursos", "Espacios", "Investigación", "Usuarios", "Administración", "Reportes"]) {
      expect(screen.getByRole("link", { name: etiqueta })).toBeInTheDocument();
    }
    expect(screen.queryByRole("link", { name: "Notificaciones" })).toBeNull();
    expect(screen.getByRole("button", { name: /Notificaciones/ })).toBeInTheDocument();
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
