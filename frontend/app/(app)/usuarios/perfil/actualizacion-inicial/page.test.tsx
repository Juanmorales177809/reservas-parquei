import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import type { Perfil } from "@/src/lib/usuarios-types";
import PaginaActualizacionInicial from "./page";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock, replace: vi.fn() }),
}));

const obtenerPerfilMock = vi.fn();
const actualizarPerfilMock = vi.fn();
const confirmarMock = vi.fn();
const catalogoMock = vi.fn();

vi.mock("@/src/lib/usuarios-api", () => ({
  obtenerPerfil: () => obtenerPerfilMock(),
  actualizarPerfil: (...args: unknown[]) => actualizarPerfilMock(...args),
  confirmarActualizacionInicial: () => confirmarMock(),
  catalogoVinculaciones: () => catalogoMock(),
}));

function perfilBase(vinculaciones?: Partial<Perfil["vinculaciones"]>): Perfil {
  return {
    id_usuario: 1042,
    nombre: "Persona",
    documento: "1000000001",
    telefono: "+573000000001",
    institucion: "ITM",
    dependencia: "Facultad",
    correo: "persona@correo.itm.edu.co",
    actualizacion_inicial_pendiente: true,
    perfil_actualizado_at: null,
    perfiles: [],
    vinculaciones: {
      proyectos: [],
      semilleros: [],
      pasantias: [],
      trabajos_grado: [],
      ...vinculaciones,
    },
  };
}

// FE-09 (WF-USR-01): aviso sin vinculación válida y 409 al continuar.
describe("actualizacion-inicial/page.tsx", () => {
  beforeEach(() => {
    pushMock.mockReset();
    obtenerPerfilMock.mockReset();
    actualizarPerfilMock.mockReset();
    confirmarMock.mockReset();
    catalogoMock.mockResolvedValue({ datos: [] });
  });

  it("muestra el aviso sin vinculación válida y el 409 orienta a completar", async () => {
    const usuario = userEvent.setup();
    obtenerPerfilMock.mockResolvedValue(perfilBase());
    actualizarPerfilMock.mockResolvedValue(perfilBase());
    confirmarMock.mockRejectedValue(
      new ApiRequestError(409, { codigo: "CONFLICTO", mensaje: "x", detalles: [] })
    );

    render(<PaginaActualizacionInicial />);
    expect(
      await screen.findByText(/ninguna vinculación académica o investigativa activa/i)
    ).toBeInTheDocument();

    await usuario.click(screen.getByRole("button", { name: "Continuar" }));
    await waitFor(() => {
      expect(confirmarMock).toHaveBeenCalledTimes(1);
    });
    expect(
      await screen.findByText(/al menos una vinculación válida/i)
    ).toBeInTheDocument();
  });
});
