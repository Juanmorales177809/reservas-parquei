import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { elegir } from "@/src/test-utils";
import type { ContextoSesion } from "@/src/lib/auth-types";
import { ListadoReservas } from "./ListadoReservas";

const SESION_BASE = {
  tipo_cuenta: "PERSONAL", correo: "t@itm.edu.co", actualizacion_inicial_pendiente: null,
  id_sesion: "s", autenticacion_reciente: true,
} as const;
const ADMIN = { ...SESION_BASE, id_cuenta: 99, rol: "ADMINISTRADOR", unidades_autorizadas: "GLOBAL" } as ContextoSesion;
const TECNICO_OTRA_UNIDAD = { ...SESION_BASE, id_cuenta: 98, rol: "TECNICO", unidades_autorizadas: [55] } as ContextoSesion;
const DUENO = { ...SESION_BASE, id_cuenta: 1, tipo_cuenta: "USUARIO", rol: "USUARIO", unidades_autorizadas: [] } as ContextoSesion;

// El contenido del modal ya tiene sus propias pruebas (GestionReservaClient); aquí solo importa qué vista recibe.
vi.mock("@/src/components/reservas/GestionReservaClient", () => ({
  GestionReservaContenido: ({ vista, onCambio }: { vista: string; onCambio?: () => void }) => (
    <div>
      contenido:{vista}
      <button type="button" onClick={onCambio}>simular cambio</button>
    </div>
  ),
}));

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
describe("ListadoReservas", () => {
  beforeEach(() => {
    listarMock.mockReset();
    listarMock.mockResolvedValue(RESPUESTA());
  });

  it("muestra cada reserva con nombres y fecha legible, sin identificadores", async () => {
    render(<ListadoReservas sesion={ADMIN} />);
    expect(await screen.findByText("Sala 3")).toBeInTheDocument();
    expect(screen.getByText("Camila Torres")).toBeInTheDocument();
    const lista = within(screen.getByRole("list", { name: "Reservas" }));
    expect(lista.getByText("Solicitada")).toBeInTheDocument();
    expect(lista.getByText("10:00–12:00")).toBeInTheDocument();
    expect(lista.getByText("2030")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ver reserva de Sala 3" })).toHaveAttribute("href", "/reservas/501");
  });

  it("filtrar por estado y por unidad vuelve a la primera página con esos filtros", async () => {
    const usuario = userEvent.setup();
    render(<ListadoReservas sesion={ADMIN} />);
    await screen.findByText("Sala 3");
    await usuario.click(screen.getByRole("button", { name: "Aprobadas" }));
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith(expect.objectContaining({ estado: "APROBADA", pagina: 1 })));
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
    await waitFor(() =>
      expect(listarMock).toHaveBeenLastCalledWith(expect.objectContaining({ estado: "APROBADA", id_unidad: 7 }))
    );
  });

  it("pagina de a 20 y avanza a la siguiente", async () => {
    const usuario = userEvent.setup();
    listarMock.mockResolvedValue(RESPUESTA(2));
    render(<ListadoReservas sesion={ADMIN} />);
    expect(await screen.findByText("Página 1 de 2 · 21 reservas")).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Siguiente" }));
    await waitFor(() => expect(listarMock).toHaveBeenLastCalledWith(expect.objectContaining({ pagina: 2 })));
  });

  it("sin reservas lo dice", async () => {
    listarMock.mockResolvedValue({ datos: [], paginacion: { pagina: 1, tamano: 20, total: 0, paginas: 1 } });
    render(<ListadoReservas sesion={ADMIN} />);
    expect(await screen.findByText("Sin reservas.")).toBeInTheDocument();
  });

  it("filtra por fecha de uso y no consulta con un rango invertido (contrato §3.1)", async () => {
    const usuario = userEvent.setup();
    render(<ListadoReservas sesion={ADMIN} />);
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

  // FE-33: cada reserva ofrece las acciones que el actor puede hacer, y se resuelven en un modal.
  it("un administrador ve las acciones de una solicitud y Aprobar abre el modal sobre esa vista", async () => {
    const usuario = userEvent.setup();
    render(<ListadoReservas sesion={ADMIN} />);
    await screen.findByText("Sala 3");
    const lista = within(screen.getByRole("list", { name: "Reservas" }));
    expect(lista.getByRole("button", { name: "Aprobar" })).toBeInTheDocument();
    expect(lista.getByRole("button", { name: "Rechazar" })).toBeInTheDocument();
    expect(lista.getByRole("button", { name: "Cancelar" })).toBeInTheDocument();
    expect(lista.getByRole("button", { name: "Ver detalle" })).toBeInTheDocument();

    await usuario.click(lista.getByRole("button", { name: "Aprobar" }));
    const dialogo = await screen.findByRole("dialog");
    expect(within(dialogo).getByText("contenido:revision")).toBeInTheDocument();
    expect(within(dialogo).getByRole("heading", { name: "Sala 3" })).toBeInTheDocument();
    expect(within(dialogo).getByRole("link", { name: /página completa/ })).toHaveAttribute("href", "/reservas/501");
  });

  it("el modal se cierra con Escape y devuelve el foco al botón que lo abrió", async () => {
    const usuario = userEvent.setup();
    render(<ListadoReservas sesion={ADMIN} />);
    await screen.findByText("Sala 3");
    const boton = screen.getByRole("button", { name: "Ver detalle" });
    await usuario.click(boton);
    expect(await screen.findByText("contenido:todo")).toBeInTheDocument();
    await usuario.keyboard("{Escape}");
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
    expect(boton).toHaveFocus();
  });

  it("una acción completada en el modal actualiza el listado sin vaciarlo", async () => {
    const usuario = userEvent.setup();
    render(<ListadoReservas sesion={ADMIN} />);
    await screen.findByText("Sala 3");
    await usuario.click(screen.getByRole("button", { name: "Rechazar" }));
    listarMock.mockClear();
    await usuario.click(await screen.findByRole("button", { name: "simular cambio" }));
    await waitFor(() => expect(listarMock).toHaveBeenCalledTimes(1));
    expect(within(screen.getByRole("list", { name: "Reservas" })).getByText("Sala 3")).toBeInTheDocument();
  });

  it("quien solicitó ve Editar y Cancelar, pero no las acciones del técnico", async () => {
    render(<ListadoReservas sesion={DUENO} />);
    await screen.findByText("Sala 3");
    const lista = within(screen.getByRole("list", { name: "Reservas" }));
    expect(lista.getByRole("button", { name: "Editar" })).toBeInTheDocument();
    expect(lista.getByRole("button", { name: "Cancelar" })).toBeInTheDocument();
    expect(lista.queryByRole("button", { name: "Aprobar" })).not.toBeInTheDocument();
    expect(lista.queryByRole("button", { name: "Rechazar" })).not.toBeInTheDocument();
  });

  it("un técnico de otra unidad solo puede ver el detalle", async () => {
    render(<ListadoReservas sesion={TECNICO_OTRA_UNIDAD} />);
    await screen.findByText("Sala 3");
    const lista = within(screen.getByRole("list", { name: "Reservas" }));
    expect(lista.getAllByRole("button").map((b) => b.textContent)).toEqual(["Ver detalle"]);
  });
});
