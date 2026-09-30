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
const crearUsuarioMock = vi.fn();

vi.mock("@/src/lib/administracion-api", () => ({
  buscarUsuarios: (...a: unknown[]) => usuariosMock(...a),
  buscarPersonal: (...a: unknown[]) => personalMock(...a),
  editarUsuario: (...a: unknown[]) => editarUsuarioMock(...a),
  editarPersonal: (...a: unknown[]) => editarPersonalMock(...a),
  cambiarEstadoUsuario: (...a: unknown[]) => estadoUsuarioMock(...a),
  cambiarEstadoPersonal: (...a: unknown[]) => estadoPersonalMock(...a),
  crearUsuarioIdentidad: (...a: unknown[]) => crearUsuarioMock(...a),
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
    for (const m of [usuariosMock, personalMock, editarUsuarioMock, editarPersonalMock, estadoUsuarioMock, estadoPersonalMock, crearUsuarioMock]) m.mockReset();
    usuariosMock.mockResolvedValue({ datos: [USUARIO], paginacion: PAG });
    personalMock.mockResolvedValue({ datos: [PERSONA], paginacion: PAG });
  });

  it("lista usuarios con su afiliación y si ya tienen cuenta", async () => {
    render(<PaginaPersonas />);
    expect(await screen.findByText("Ana Pérez")).toBeInTheDocument();
    expect(screen.getByText(/ITM · Facultad/)).toBeInTheDocument();
    expect(screen.getByText("Con cuenta")).toBeInTheDocument();
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
    await screen.findByText("Ana Pérez");
    await usuario.click(screen.getByRole("button", { name: "Personal" }));
    expect(await screen.findByText(/Técnico de laboratorio · Laboratorio de Redes/)).toBeInTheDocument();
    expect(screen.getByText("Sin cuenta")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Editar" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Desactivar" })).toBeInTheDocument();
    // Quien aún no tiene cuenta se puede invitar desde su tarjeta.
    expect(screen.getByRole("link", { name: "Invitar cuenta" })).toHaveAttribute(
      "href", "/administracion/cuentas/invitar?correo=luis%40itm.edu.co&tipo=PERSONAL"
    );
  });

  it("busca y filtra por estado", async () => {
    const usuario = userEvent.setup();
    render(<PaginaPersonas />);
    await screen.findByText("Ana Pérez");
    await usuario.click(screen.getByRole("button", { name: "Inactivos" }));
    await waitFor(() => expect(usuariosMock).toHaveBeenLastCalledWith({ estado: false }));
    await usuario.type(screen.getByLabelText("Buscar por nombre, documento o correo"), "ana");
    await waitFor(() => expect(usuariosMock).toHaveBeenLastCalledWith({ estado: false, busqueda: "ana" }));
  });

  // FE-39: editar y registrar son modales; el listado son tarjetas.
  it("editar abre un modal y se cierra con Cancelar sin enviar nada", async () => {
    const usuario = userEvent.setup();
    render(<PaginaPersonas />);
    await usuario.click(await screen.findByRole("button", { name: "Editar" }));
    expect(screen.getByRole("dialog", { name: "Editar a Ana Pérez" })).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(editarUsuarioMock).not.toHaveBeenCalled();
  });

  it("registra un usuario en un modal, actualiza el listado y ofrece invitar su cuenta", async () => {
    const usuario = userEvent.setup();
    crearUsuarioMock.mockResolvedValue({ id_usuario: 5 });
    render(<PaginaPersonas />);
    await screen.findByText("Ana Pérez");
    await usuario.click(screen.getByRole("button", { name: "Registrar usuario" }));
    const dialogo = within(screen.getByRole("dialog", { name: "Registrar usuario" }));
    await usuario.type(dialogo.getByLabelText("Nombre"), "Marta Ríos");
    await usuario.type(dialogo.getByLabelText("Documento"), "500");
    await usuario.type(dialogo.getByLabelText("Teléfono"), "312");
    await usuario.type(dialogo.getByLabelText("Correo"), "marta@itm.edu.co");
    await usuario.type(dialogo.getByLabelText("Institución"), "ITM");
    await usuario.type(dialogo.getByLabelText("Dependencia"), "Facultad");
    usuariosMock.mockClear();
    await usuario.click(dialogo.getByRole("button", { name: "Guardar" }));
    await waitFor(() =>
      expect(crearUsuarioMock).toHaveBeenCalledWith({
        nombre: "Marta Ríos", documento: "500", correo: "marta@itm.edu.co", telefono: "312", institucion: "ITM", dependencia: "Facultad",
      })
    );
    expect(await dialogo.findByText("Identidad guardada.")).toBeInTheDocument();
    expect(dialogo.getByRole("link", { name: "Invitar una cuenta" })).toHaveAttribute(
      "href", "/administracion/cuentas/invitar?correo=marta%40itm.edu.co"
    );
    await waitFor(() => expect(usuariosMock).toHaveBeenCalled()); // el listado se actualizó
  });
});
