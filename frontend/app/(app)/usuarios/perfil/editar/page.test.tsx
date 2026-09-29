import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import PaginaEditarDatos from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

const obtenerPerfilMock = vi.fn();
const actualizarPerfilMock = vi.fn();

vi.mock("@/src/lib/usuarios-api", () => ({
  obtenerPerfil: () => obtenerPerfilMock(),
  actualizarPerfil: (...args: unknown[]) => actualizarPerfilMock(...args),
}));

const PERFIL = {
  id_usuario: 1042,
  nombre: "Persona",
  documento: "1000000001",
  telefono: "+573000000001",
  institucion: "ITM",
  dependencia: "Facultad",
  correo: "persona@correo.itm.edu.co",
  actualizacion_inicial_pendiente: false,
  perfil_actualizado_at: "2026-09-19T14:03:11Z",
  perfiles: [],
  vinculaciones: { proyectos: [], semilleros: [], pasantias: [], trabajos_grado: [] },
};

// FE-09 (WF-USR-03): el duplicado aparece junto al campo, sin identificar el otro registro.
describe("perfil/editar/page.tsx", () => {
  beforeEach(() => {
    obtenerPerfilMock.mockReset();
    actualizarPerfilMock.mockReset();
  });

  it("documento duplicado muestra el mensaje junto al campo", async () => {
    const usuario = userEvent.setup();
    obtenerPerfilMock.mockResolvedValue(PERFIL);
    actualizarPerfilMock.mockRejectedValue(
      new ApiRequestError(409, { codigo: "DOCUMENTO_DUPLICADO", mensaje: "x", detalles: [] })
    );

    render(<PaginaEditarDatos />);
    expect(await screen.findByDisplayValue("1000000001")).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Guardar cambios" }));
    await waitFor(() => {
      expect(actualizarPerfilMock).toHaveBeenCalledTimes(1);
    });
    const campo = screen.getByLabelText("Documento");
    expect(campo).toHaveAttribute("aria-invalid", "true");
    expect(
      await screen.findByText(/ya está registrado en otra identidad/i)
    ).toBeInTheDocument();
  });
});
