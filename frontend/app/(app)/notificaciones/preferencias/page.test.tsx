import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import PaginaPreferencias from "./page";

// Router estable: un objeto nuevo por render relanzaría el efecto sin fin.
const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({
  useRouter: () => router,
}));

const prefsMock = vi.fn();
const tiposMock = vi.fn();
const guardarMock = vi.fn();

vi.mock("@/src/lib/notificaciones-api", () => ({
  obtenerPreferencias: () => prefsMock(),
  tiposEvento: () => tiposMock(),
  guardarPreferencias: (...args: unknown[]) => guardarMock(...args),
}));

// FE-21 (WF-NOT-02): reemplazo completo con general y explícitas.
describe("notificaciones/preferencias/page.tsx", () => {
  beforeEach(() => {
    prefsMock.mockReset();
    tiposMock.mockReset();
    guardarMock.mockReset();
    prefsMock.mockResolvedValue({
      general: { correo_habilitado: true },
      por_evento: [],
    });
    tiposMock.mockResolvedValue({
      datos: [{ id: 7, codigo: "RESERVA_RECORDATORIO", nombre: "Recordatorio", descripcion: null }],
    });
  });

  it("apagar un tipo guarda reemplazo completo", async () => {
    const usuario = userEvent.setup();
    guardarMock.mockResolvedValue({
      general: { correo_habilitado: true },
      por_evento: [],
    });

    render(<PaginaPreferencias />);
    await usuario.click(await screen.findByLabelText("Recordatorio"));
    await usuario.click(screen.getByRole("button", { name: "Guardar preferencias" }));
    await waitFor(() => {
      expect(guardarMock).toHaveBeenCalledWith({
        general: { correo_habilitado: true },
        por_evento: [{ tipo_evento_id: 7, correo_habilitado: false }],
      });
    });
    expect(await screen.findByText("Preferencias guardadas.")).toBeInTheDocument();
  });

  it("tipo inexistente o deshabilitado: 404 con mensaje de corrección", async () => {
    guardarMock.mockRejectedValue(
      new ApiRequestError(404, { codigo: "NO_ENCONTRADO", mensaje: "x", detalles: [] })
    );
    render(<PaginaPreferencias />);
    await userEvent.click(await screen.findByLabelText("Recordatorio"));
    await userEvent.click(screen.getByRole("button", { name: "Guardar preferencias" }));
    expect(
      await screen.findByText("Un tipo de evento no existe o está deshabilitado. Recarga la página.")
    ).toBeInTheDocument();
  });

  it("tipo repetido: 422 con mensaje de corrección", async () => {
    guardarMock.mockRejectedValue(
      new ApiRequestError(422, { codigo: "VALIDACION", mensaje: "x", detalles: [] })
    );
    render(<PaginaPreferencias />);
    await userEvent.click(await screen.findByLabelText("Recordatorio"));
    await userEvent.click(screen.getByRole("button", { name: "Guardar preferencias" }));
    expect(
      await screen.findByText("Revisa las preferencias: hay un tipo de evento repetido.")
    ).toBeInTheDocument();
  });
});
