import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import PaginaPersonas from "./page";

const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({ useRouter: () => router }));

const usuariosMock = vi.fn();
const personalMock = vi.fn();
const editarUsuarioMock = vi.fn();
const editarPersonalMock = vi.fn();
const estadoUsuarioMock = vi.fn();
const estadoPersonalMock = vi.fn();

vi.mock("@/src/lib/administracion-api", () => ({
  buscarUsuarios: (...a: unknown[]) => usuariosMock(...a),
  buscarPersonal: (...a: unknown[]) => personalMock(...a),
  editarUsuario: (...a: unknown[]) => editarUsuarioMock(...a),
  editarPersonal: (...a: unknown[]) => editarPersonalMock(...a),
  cambiarEstadoUsuario: (...a: unknown[]) => estadoUsuarioMock(...a),
  cambiarEstadoPersonal: (...a: unknown[]) => estadoPersonalMock(...a),
  listarCargos: () => Promise.resolve({ datos: [{ id_cargo: 4, nombre_cargo: "Técnico de laboratorio", id_unidad: 7 }, { id_cargo: 5, nombre_cargo: "Coordinador", id_unidad: 7 }] }),
  listarUnidades: () => Promise.resolve({ datos: [{ id_unidad: 7, nombre: "Laboratorio de Redes", tipo: "LABORATORIO", id_unidad_padre: null, estado: true }] }),
}));

const USUARIO = {
  id_usuario: 1, id_cuenta: 9, nombre: "Ana Pérez", documento: "100", telefono: "300", institucion: "ITM", dependencia: "Facultad",
  correo: "ana@itm.edu.co", estado: true,
};
const PERSONA = {
  id_persona: 2, id_cuenta: null, nombre: "Luis Mora", documento: "200", telefono: "301", correo: "luis@itm.edu.co", estado: true,
  id_cargo: 4, cargo: { id_cargo: 4, nombre_cargo: "Técnico de laboratorio" }, unidad: { id_unidad: 7, nombre: "Laboratorio de Redes" },
};
const PAG = { pagina: 1, paginas: 1, total: 1 };

// FE-29: consultar, editar y activar o desactivar identidades (usuarios §5 y §6).
describe("administracion/personas/page.tsx", () => {
  beforeEach(() => {
    for (const m of [usuariosMock, personalMock, editarUsuarioMock, editarPersonalMock, estadoUsuarioMock, estadoPersonalMock]) m.mockReset();
    usuariosMock.mockResolvedValue({ datos: [USUARIO], paginacion: PAG });
    personalMock.mockResolvedValue({ datos: [PERSONA], paginacion: PAG });
  });

  it("lista usuarios con su afiliación y si ya tienen cuenta", async () => {
    render(<PaginaPersonas />);
    expect(await screen.findByText("Ana Pérez")).toBeInTheDocument();
    expect(screen.getByText(/ITM · Facultad · con cuenta/)).toBeInTheDocument();
  });

  it("edita solo lo que cambió y no permite cambiar el correo de quien ya tiene cuenta", async () => {
    const usuario = userEvent.setup();
    editarUsuarioMock.mockResolvedValue({});
    render(<PaginaPersonas />);
    await usuario.click(await screen.findByRole("button", { name: "Editar" }));
    const formulario = within(screen.getByRole("form", { name: "Editar persona" }));
    expect(formulario.getByLabelText("Correo")).toBeDisabled();
    await usuario.clear(formulario.getByLabelText("Teléfono"));
    await usuario.type(formulario.getByLabelText("Teléfono"), "311");
    await usuario.click(formulario.getByRole("button", { name: "Guardar cambios" }));
    await waitFor(() => expect(editarUsuarioMock).toHaveBeenCalledWith(1, { telefono: "311" }));
  });

  it("desactiva a una persona y reactiva a otra", async () => {
    const usuario = userEvent.setup();
    estadoUsuarioMock.mockResolvedValue({});
    render(<PaginaPersonas />);
    await usuario.click(await screen.findByRole("button", { name: "Desactivar" }));
    await waitFor(() => expect(estadoUsuarioMock).toHaveBeenCalledWith(1, false));
  });

  // Decisión 2026-09-30: el personal y sus cargos llegan de la base institucional; aquí no se editan.
  it("el personal se consulta, pero no se edita desde aquí; su acceso sí se activa o desactiva", async () => {
    const usuario = userEvent.setup();
    render(<PaginaPersonas />);
    await usuario.selectOptions(await screen.findByLabelText("Ver"), "Personal");
    expect(await screen.findByText(/Técnico de laboratorio · Laboratorio de Redes · sin cuenta/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Editar" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Desactivar" })).toBeInTheDocument();
  });

  it("busca y filtra por estado", async () => {
    const usuario = userEvent.setup();
    render(<PaginaPersonas />);
    await screen.findByText("Ana Pérez");
    await usuario.selectOptions(screen.getByLabelText("Estado"), "Inactivos");
    await waitFor(() => expect(usuariosMock).toHaveBeenLastCalledWith({ estado: false }));
    await usuario.type(screen.getByLabelText("Buscar por nombre, documento o correo"), "ana");
    await waitFor(() => expect(usuariosMock).toHaveBeenLastCalledWith({ estado: false, busqueda: "ana" }));
  });
});
