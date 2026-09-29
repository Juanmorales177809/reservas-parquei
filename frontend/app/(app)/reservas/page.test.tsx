import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { elegir } from "@/src/test-utils";
import PaginaReservas from "./page";

const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({ useRouter: () => router }));

vi.mock("@/src/lib/administracion-api", () => ({
  listarUnidades: () =>
    Promise.resolve({
      datos: [{ id_unidad: 7, nombre: "Laboratorio de Redes", tipo: "LABORATORIO", id_unidad_padre: null, estado: true }],
    }),
}));
vi.mock("@/src/lib/espacios-api", () => ({
  listarEspacios: () =>
    Promise.resolve({ datos: [{ id: 3, id_unidad: 7, nombre: "Sala 3", capacidad: 10, habilitado: true }] }),
}));

const listarMock = vi.fn();
vi.mock("@/src/lib/reservas-api", () => ({ listarReservas: (...a: unknown[]) => listarMock(...a) }));

const FILA = {
  id: 501, estado: "SOLICITADA", tipo_reserva: "ESPACIO", id_unidad: 7, id_cuenta: 1, requiere_apoyo: false,
  created_at: "2026-09-01T10:00:00Z",
  periodo: { fecha: "2030-08-04", hora_inicio: "10:00:00", hora_fin: "12:00:00" },
  objeto: "Sala 3", unidad_nombre: "Laboratorio de Redes", solicitante_nombre: "Camila Torres",
};
const RESPUESTA = (paginas = 1) => ({ datos: [FILA], paginacion: { pagina: 1, tamano: 20, total: 21, paginas } });

// FE-28 (WF-RES-04): el listado muestra cuándo, qué, dónde y quién, con filtros y paginación.
describe("reservas/page.tsx", () => {
  beforeEach(() => {
    listarMock.mockReset();
    listarMock.mockResolvedValue(RESPUESTA());
  });

  it("muestra cada reserva con nombres y fecha legible, sin identificadores", async () => {
    render(<PaginaReservas />);
    expect(await screen.findByText("Sala 3")).toBeInTheDocument();
    expect(screen.getByText("Camila Torres")).toBeInTheDocument();
    const tabla = within(screen.getByRole("table"));
    expect(tabla.getByText("Solicitada")).toBeInTheDocument();
    expect(tabla.getByText(/2030.*10:00–12:00/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ver reserva" })).toHaveAttribute("href", "/reservas/501");
  });

  it("filtrar por estado y por unidad vuelve a la primera página con esos filtros", async () => {
    const usuario = userEvent.setup();
    render(<PaginaReservas />);
    await screen.findByText("Sala 3");
    await usuario.selectOptions(screen.getByLabelText("Estado"), "Aprobada");
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith(expect.objectContaining({ estado: "APROBADA", pagina: 1 })));
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
    await waitFor(() =>
      expect(listarMock).toHaveBeenLastCalledWith(expect.objectContaining({ estado: "APROBADA", id_unidad: 7 }))
    );
  });

  it("pagina de a 20 y avanza a la siguiente", async () => {
    const usuario = userEvent.setup();
    listarMock.mockResolvedValue(RESPUESTA(2));
    render(<PaginaReservas />);
    expect(await screen.findByText("Página 1 de 2 · 21 reservas")).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Siguiente" }));
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith(expect.objectContaining({ pagina: 2 })));
  });

  it("sin reservas lo dice", async () => {
    listarMock.mockResolvedValue({ datos: [], paginacion: { pagina: 1, tamano: 20, total: 0, paginas: 1 } });
    render(<PaginaReservas />);
    expect(await screen.findByText("Sin reservas.")).toBeInTheDocument();
  });

  it("filtra por fecha de uso y no consulta con un rango invertido (contrato §3.1)", async () => {
    const usuario = userEvent.setup();
    render(<PaginaReservas />);
    await screen.findByText("Sala 3");
    await usuario.type(screen.getByLabelText("Desde (fecha de uso)"), "2030-08-01");
    await usuario.type(screen.getByLabelText("Hasta (fecha de uso)"), "2030-08-31");
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith(expect.objectContaining({ desde: "2030-08-01", hasta: "2030-08-31", pagina: 1 })));
    listarMock.mockClear();
    await usuario.clear(screen.getByLabelText("Hasta (fecha de uso)"));
    await usuario.type(screen.getByLabelText("Hasta (fecha de uso)"), "2030-07-01");
    expect(await screen.findByText(/no puede ser posterior/)).toBeInTheDocument();
    expect(listarMock).not.toHaveBeenCalledWith(expect.objectContaining({ hasta: "2030-07-01" }));
  });
});
