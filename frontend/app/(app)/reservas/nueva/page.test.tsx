import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "@/src/lib/http";
import { elegir } from "@/src/test-utils";
import PaginaNuevaReserva from "./page";

const router = { push: vi.fn(), replace: vi.fn() };
vi.mock("next/navigation", () => ({
  useRouter: () => router,
}));

vi.mock("@/src/lib/administracion-api", () => ({
  listarUnidades: () =>
    Promise.resolve({
      datos: [{ id_unidad: 7, nombre: "Laboratorio de Redes", tipo: "LABORATORIO", id_unidad_padre: null, estado: true }],
    }),
}));

const detalleEspacioMock = vi.fn();
vi.mock("@/src/lib/espacios-api", () => ({
  listarEspacios: () =>
    Promise.resolve({ datos: [{ id: 3, id_unidad: 7, nombre: "Sala 3", capacidad: 2, habilitado: true }] }),
  detalleEspacio: (...a: unknown[]) => detalleEspacioMock(...a),
}));

const detalleRecursoMock = vi.fn();
vi.mock("@/src/lib/recursos-api", () => ({
  listarRecursos: () =>
    Promise.resolve({
      datos: [
        { id: 41, tipo: "MOBILIARIO", nombre: "Mesa", id_unidad: 7, habilitado: true },
        { id: 42, tipo: "EQUIPO", nombre: "Osciloscopio", id_unidad: 7, habilitado: true },
        { id: 43, tipo: "OTRO", nombre: "Cables", id_unidad: 7, habilitado: true },
      ],
    }),
  detalleRecurso: (...a: unknown[]) => detalleRecursoMock(...a),
}));

const crearMock = vi.fn();
const disponibilidadMock = vi.fn();
const subirMock = vi.fn();
const tiposMock = vi.fn();
const contextoMock = vi.fn();
const acompanantesMock = vi.fn();
vi.mock("@/src/lib/reservas-api", () => ({
  crearReserva: (...args: unknown[]) => crearMock(...args),
  consultarDisponibilidad: (...args: unknown[]) => disponibilidadMock(...args),
  subirAdjunto: (...args: unknown[]) => subirMock(...args),
  tiposHabilitados: (...args: unknown[]) => tiposMock(...args),
  opcionesContexto: () => contextoMock(),
  opcionesAcompanantes: (...args: unknown[]) => acompanantesMock(...args),
}));

const TIPO = (codigo: string, nombre: string) => ({ codigo, nombre });
const ESPACIO_SIMPLE = { id: 3, id_unidad: 7, nombre: "Sala 3", capacidad: 2, habilitado: true, ubicacion: null, descripcion: null, horario_unidad: null, recursos: [], campos: [] };
const USUARIO_CON_UN_PROYECTO = {
  tipo_cuenta: "USUARIO",
  proyectos: [{ id: 12, codigo: "P-12", nombre: "Ensayos" }],
  semilleros: [], pasantias: [], trabajos_grado: [], actividades: [],
};

async function llenarEspacio(usuario: ReturnType<typeof userEvent.setup>) {
  await elegir(usuario, "Unidad", "Laboratorio de Redes");
  await elegir(usuario, "Espacio", "Sala 3 (cap. 2)");
  await usuario.type(screen.getByLabelText("Fecha"), "2030-08-04");
  await usuario.type(screen.getByLabelText("Hora inicio"), "10:00");
  await usuario.type(screen.getByLabelText("Hora fin"), "12:00");
}

// FE-25 (WF-RES-01): la solicitud sigue las reglas de tipos, contexto, campos y acompañantes.
describe("reservas/nueva/page.tsx", () => {
  beforeEach(() => {
    for (const m of [crearMock, disponibilidadMock, subirMock, tiposMock, contextoMock, acompanantesMock, detalleEspacioMock, detalleRecursoMock, router.push])
      m.mockReset();
    subirMock.mockResolvedValue({});
    crearMock.mockResolvedValue({ id: 501 });
    tiposMock.mockResolvedValue({ datos: [TIPO("ESPACIO", "Reserva por espacio")] });
    contextoMock.mockResolvedValue(USUARIO_CON_UN_PROYECTO);
    detalleEspacioMock.mockResolvedValue(ESPACIO_SIMPLE);
    acompanantesMock.mockResolvedValue({ datos: [] });
    detalleRecursoMock.mockResolvedValue({ especializacion: {} });
  });

  it("con un solo tipo habilitado lo asigna solo, y preselecciona la única vinculación (RN-TIP-02, RN-TIP-PE-08)", async () => {
    const usuario = userEvent.setup();
    render(<PaginaNuevaReserva />);
    await llenarEspacio(usuario);
    expect(screen.getByText("Tipo de reserva: Reserva por espacio")).toBeInTheDocument();
    expect(await screen.findByLabelText("Proyecto")).toHaveValue("12");
    await usuario.click(screen.getByRole("button", { name: "Guardar solicitud" }));
    await waitFor(() => {
      expect(crearMock).toHaveBeenCalledWith({
        id_unidad: 7,
        tipo_reserva: "ESPACIO",
        contexto: { proyecto_id: 12 },
        detalle: { espacio_id: 3, fecha: "2030-08-04", hora_inicio: "10:00", hora_fin: "12:00", asistentes: 0 },
      });
    });
  });

  it("una unidad sin tipos habilitados avisa que no admite reservas (RN-TIP-06)", async () => {
    const usuario = userEvent.setup();
    tiposMock.mockResolvedValue({ datos: [] });
    render(<PaginaNuevaReserva />);
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
    expect(await screen.findByText("Esta unidad no admite reservas en este momento.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Guardar solicitud" })).not.toBeInTheDocument();
  });

  it("con varios tipos obliga a elegir uno (RN-TIP-03)", async () => {
    const usuario = userEvent.setup();
    tiposMock.mockResolvedValue({ datos: [TIPO("ESPACIO", "Reserva por espacio"), TIPO("LISTA_ESPERA", "Lista de espera")] });
    render(<PaginaNuevaReserva />);
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
    await screen.findByRole("option", { name: "Lista de espera" });
    expect(screen.queryByRole("button", { name: "Guardar solicitud" })).not.toBeInTheDocument();
  });

  it("un campo adicional obligatorio del espacio se pide y viaja en la solicitud (RN-TIP-PE-18)", async () => {
    const usuario = userEvent.setup();
    detalleEspacioMock.mockResolvedValue({
      ...ESPACIO_SIMPLE,
      campos: [{ id: 5, nombre: "Ensayo previsto", tipo: "TEXTO", obligatorio: true, orden: 1, habilitado: true }],
    });
    render(<PaginaNuevaReserva />);
    await llenarEspacio(usuario);
    await screen.findByLabelText("Proyecto");
    await usuario.click(await screen.findByRole("button", { name: "Guardar solicitud" }));
    expect(await screen.findByText(/Completa la información que pide el espacio: Ensayo previsto/)).toBeInTheDocument();
    expect(crearMock).not.toHaveBeenCalled();

    await usuario.type(screen.getByLabelText("Ensayo previsto"), "Tracción");
    await usuario.click(screen.getByRole("button", { name: "Guardar solicitud" }));
    await waitFor(() => {
      expect(crearMock).toHaveBeenCalledWith(
        expect.objectContaining({ campos_adicionales: [{ campo_id: 5, valor_texto: "Tracción" }] })
      );
    });
  });

  it("los acompañantes se eligen por nombre y determinan los asistentes (RN-ACO-03, RN-TIP-PE-05)", async () => {
    const usuario = userEvent.setup();
    acompanantesMock.mockResolvedValue({ datos: [{ id_cuenta: 99, nombre: "Camila Torres" }] });
    render(<PaginaNuevaReserva />);
    await llenarEspacio(usuario);
    await usuario.click(await screen.findByRole("checkbox", { name: "Camila Torres" }));
    expect(screen.getByText("Asistentes: 1 de 2 (capacidad del espacio)")).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Guardar solicitud" }));
    await waitFor(() => {
      expect(crearMock).toHaveBeenCalledWith(
        expect.objectContaining({
          acompanantes: [99],
          detalle: expect.objectContaining({ asistentes: 1 }),
        })
      );
    });
  });

  it("sin contexto elegido no se envía (RN-CTX-01) y una actividad institucional reemplaza a lo demás (RN-CTX-04)", async () => {
    const usuario = userEvent.setup();
    contextoMock.mockResolvedValue({
      tipo_cuenta: "USUARIO",
      proyectos: [{ id: 12, codigo: "P-12", nombre: "Ensayos" }, { id: 13, codigo: "P-13", nombre: "Otro" }],
      semilleros: [], pasantias: [], trabajos_grado: [],
      actividades: [{ id: 2, nombre: "Feria", dependencia: "Extensión" }],
    });
    render(<PaginaNuevaReserva />);
    await llenarEspacio(usuario);
    await screen.findByLabelText("Proyecto");
    await usuario.click(screen.getByRole("button", { name: "Guardar solicitud" }));
    expect(await screen.findByText(/Elige un proyecto, un semillero/)).toBeInTheDocument();
    expect(crearMock).not.toHaveBeenCalled();

    await elegir(usuario, "Proyecto", "Ensayos (P-12)");
    await elegir(usuario, "Actividad institucional (reemplaza a lo anterior)", "Feria (Extensión)");
    expect(screen.getByLabelText("Proyecto")).toHaveValue("");
    await usuario.click(screen.getByRole("button", { name: "Guardar solicitud" }));
    await waitFor(() => {
      expect(crearMock).toHaveBeenCalledWith(expect.objectContaining({ contexto: { actividad_institucional_id: 2 } }));
    });
  });

  it("una cuenta sin vinculaciones es enviada a Mis vinculaciones", async () => {
    const usuario = userEvent.setup();
    contextoMock.mockResolvedValue({ ...USUARIO_CON_UN_PROYECTO, proyectos: [] });
    render(<PaginaNuevaReserva />);
    await llenarEspacio(usuario);
    expect(await screen.findByRole("link", { name: /Agrégalas en Mis vinculaciones/ })).toBeInTheDocument();
  });

  it("solapamiento muestra el mensaje del servidor", async () => {
    const usuario = userEvent.setup();
    crearMock.mockRejectedValue(new ApiRequestError(409, { codigo: "SOLAPAMIENTO", mensaje: "x", detalles: [] }));
    render(<PaginaNuevaReserva />);
    await llenarEspacio(usuario);
    await screen.findByLabelText("Proyecto");
    await usuario.click(screen.getByRole("button", { name: "Guardar solicitud" }));
    expect(await screen.findByText("Ese periodo ya está ocupado.")).toBeInTheDocument();
  });

  it("permite varios recursos y marca el apoyo como obligatorio si un equipo lo exige (RN-RES-09, RN-RES-12)", async () => {
    const usuario = userEvent.setup();
    tiposMock.mockResolvedValue({ datos: [TIPO("ESPACIO", "Reserva por espacio"), TIPO("RECURSO_INTERNO", "Recurso interno")] });
    detalleRecursoMock.mockImplementation((id: number) =>
      Promise.resolve({ especializacion: id === 42 ? { requiere_apoyo: true } : {} })
    );
    render(<PaginaNuevaReserva />);
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
    await elegir(usuario, "Tipo", "Recurso interno");
    await usuario.type(screen.getByLabelText("Fecha"), "2030-08-04");
    await usuario.type(screen.getByLabelText("Hora inicio"), "10:00");
    await usuario.type(screen.getByLabelText("Hora fin"), "12:00");
    await elegir(usuario, "Recurso principal", "Mesa · Mobiliario");
    expect(screen.queryByRole("checkbox", { name: "Mesa · Mobiliario" })).not.toBeInTheDocument();
    await usuario.click(await screen.findByRole("checkbox", { name: "Osciloscopio · Equipo" }));
    await usuario.click(screen.getByRole("checkbox", { name: "Cables · Otro" }));
    const apoyo = await screen.findByRole("checkbox", { name: /Necesito acompañamiento/ });
    await waitFor(() => expect(apoyo).toBeDisabled());
    expect(apoyo).toBeChecked();
    await usuario.click(screen.getByRole("button", { name: "Guardar solicitud" }));
    await waitFor(() => {
      expect(crearMock).toHaveBeenCalledWith(
        expect.objectContaining({
          tipo_reserva: "RECURSO_INTERNO",
          requiere_apoyo: true,
          recursos: [
            { recurso_id: 41, rol: "PRINCIPAL" },
            { recurso_id: 42, rol: "ADICIONAL" },
            { recurso_id: 43, rol: "ADICIONAL" },
          ],
        })
      );
    });
  });

  it("lista de espera: sin consulta de disponibilidad y con archivos que se suben tras crear", async () => {
    const usuario = userEvent.setup();
    tiposMock.mockResolvedValue({ datos: [TIPO("LISTA_ESPERA", "Lista de espera")] });
    render(<PaginaNuevaReserva />);
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
    await usuario.type(await screen.findByLabelText("Descripción de la necesidad"), "Pieza a medida");
    expect(screen.queryByRole("button", { name: "Consultar disponibilidad" })).not.toBeInTheDocument();
    const plano = new File(["dwg"], "soporte.dwg", { type: "application/octet-stream" });
    await usuario.upload(screen.getByLabelText("Archivos técnicos (opcional)"), plano);
    await screen.findByLabelText("Proyecto");
    await usuario.click(screen.getByRole("button", { name: "Guardar solicitud" }));
    await waitFor(() => {
      expect(subirMock).toHaveBeenCalledWith(501, plano, "PLANO");
    });
  });

  it("un formato no admitido se rechaza antes de subirlo", async () => {
    const usuario = userEvent.setup({ applyAccept: false });
    tiposMock.mockResolvedValue({ datos: [TIPO("LISTA_ESPERA", "Lista de espera")] });
    render(<PaginaNuevaReserva />);
    await elegir(usuario, "Unidad", "Laboratorio de Redes");
    await usuario.upload(await screen.findByLabelText("Archivos técnicos (opcional)"), new File(["x"], "virus.exe"));
    expect(await screen.findByText(/formato no admitido/)).toBeInTheDocument();
  });
});
