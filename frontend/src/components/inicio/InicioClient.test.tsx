import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ContextoSesion } from "@/src/lib/auth-types";
import { ApiRequestError } from "@/src/lib/http";
import { InicioClient, periodoRapido } from "./InicioClient";

const sesion = (rol: "USUARIO" | "TECNICO" | "ADMINISTRADOR", unidades: number[] | "GLOBAL"): ContextoSesion => ({
  id_cuenta: 5, tipo_cuenta: "PERSONAL", rol, correo: "t@itm.edu.co", actualizacion_inicial_pendiente: false,
  id_sesion: "s", unidades_autorizadas: unidades, autenticacion_reciente: true,
});

const pendientesMock = vi.fn();
vi.mock("@/src/lib/reservas-api", () => ({ listarReservas: (...a: unknown[]) => pendientesMock(...a) }));
vi.mock("next/navigation", () => ({ useRouter: () => router }));
const router = { push: vi.fn(), replace: vi.fn() };

const resumenMock = vi.fn();
vi.mock("@/src/lib/reportes-api", () => ({
  consultarResumen: (...a: unknown[]) => resumenMock(...a),
}));
vi.mock("@/src/lib/administracion-api", () => ({
  listarUnidades: async () => ({
    datos: [
      { id_unidad: 7, nombre: "Laboratorio de Redes", tipo: "LABORATORIO", id_unidad_padre: null, estado: true },
    ],
  }),
}));
vi.mock("./GraficosInicio", () => ({
  SeriePorFecha: () => <div>serie-por-fecha</div>,
  BarrasHorizontales: ({ titulo }: { titulo: string }) => <div>barras:{titulo}</div>,
}));

const RESUMEN = {
  resumen: { desde: "2026-09-01", hasta: "2026-09-30", desde_previo: "2026-08-02", hasta_previo: "2026-08-31", filtros: {} },
  indicadores: {
    reservas: { actual: 96, previo: 80 },
    solicitadas: 12,
    horas_reservadas: { actual: 412.5, previo: 350.0 },
    porcentaje_ocupacion: { actual: 38.4, previo: null },
  },
  por_estado: { solicitada: 12, aprobada: 40, rechazada: 3, en_ejecucion: 1, finalizada: 35, cancelada: 5 },
  por_fecha: [{ fecha: "2026-09-01", reservas: 4 }],
  por_laboratorio: [
    { id_unidad: 7, nombre: "Laboratorio de Redes", reservas: 96, horas_reservadas: 412.5, porcentaje_ocupacion: 38.4 },
    { id_unidad: 8, nombre: "Bodega", reservas: 1, horas_reservadas: 3.0, porcentaje_ocupacion: null },
  ],
  recursos_mas_reservados: [{ recurso_id: 42, nombre: "Osciloscopio", reservas: 14 }],
  ocupacion_dia_hora: [{ dia: 1, hora: 9, cantidad: 6 }],
};

describe("InicioClient", () => {
  // Sin llaves el mockReset devolvería el mock y Vitest lo llamaría como
  // limpieza del beforeEach, con una promesa rechazada sin manejar.
  beforeEach(() => {
    resumenMock.mockReset();
    pendientesMock.mockReset();
    pendientesMock.mockResolvedValue({ datos: [], paginacion: { pagina: 1, tamano: 5, total: 0, paginas: 1 } });
  });

  it("el Usuario ve accesos y nunca llama al resumen", () => {
    render(<InicioClient sesion={sesion("USUARIO", [])} />);
    expect(screen.getByRole("link", { name: /Mis reservas/ })).toHaveAttribute("href", "/reservas");
    expect(screen.getByRole("link", { name: /Nueva reserva/ })).toHaveAttribute("href", "/reservas/nueva");
    expect(resumenMock).not.toHaveBeenCalled();
    expect(screen.queryByRole("button", { name: "Consultar" })).toBeNull();
  });

  it("el mes en curso ya viene consultado al entrar, sin pulsar nada (FE-50)", async () => {
    resumenMock.mockResolvedValue(RESUMEN);
    render(<InicioClient sesion={sesion("TECNICO", [7])} />);
    expect(screen.getByText("Consultando…")).toBeInTheDocument();

    // La consulta inicial viaja sola con el mes en curso.
    const ultimo = periodoRapido("este_mes");
    expect(await screen.findByText("serie-por-fecha")).toBeInTheDocument();
    expect(resumenMock).toHaveBeenCalledTimes(1);
    expect(resumenMock).toHaveBeenCalledWith({ desde: ultimo.desde, hasta: ultimo.hasta, id_unidad: "" });
    // Seis estados siempre presentes, en el orden del catálogo.
    const estados = screen.getByRole("region", { name: "Por estado" });
    expect(within(estados).getByText("12")).toBeInTheDocument();
    // Sin horario: horas sí, porcentaje nunca inventado.
    const laboratorios = screen.getByRole("region", { name: "Por laboratorio" });
    expect(within(laboratorios).getByText("Bodega")).toBeInTheDocument();
    expect(within(laboratorios).getByText("—")).toBeInTheDocument();
    // Mapa de calor por cantidad con su celda.
    expect(screen.getByTitle("Lunes 9:00 — 6 reservas")).toHaveTextContent("6");
    // Enlaces a los reportes de detalle.
    expect(screen.getByRole("link", { name: "Ocupación" })).toHaveAttribute("href", "/reportes/ocupacion");
  });

  it("con reservas pero sin secciones explica por qué, en vez de dejar huecos", async () => {
    resumenMock.mockResolvedValue({
      ...RESUMEN,
      indicadores: { ...RESUMEN.indicadores, reservas: { actual: 3, previo: 0 } },
      por_fecha: [],
      recursos_mas_reservados: [],
      ocupacion_dia_hora: [],
    });
    render(<InicioClient sesion={sesion("TECNICO", [7])} />);
    expect(await screen.findByText(/Sin serie por fecha/)).toBeInTheDocument();
    expect(screen.getByText(/Sin recursos destacados/)).toBeInTheDocument();
    expect(screen.getByText(/Sin mapa por día y hora/)).toBeInTheDocument();
  });

  it("volver a consultar con otros filtros viaja con lo elegido", async () => {
    const usuario = userEvent.setup();
    resumenMock.mockResolvedValue(RESUMEN);
    render(<InicioClient sesion={sesion("TECNICO", [7])} />);
    await screen.findByText("serie-por-fecha");
    expect(resumenMock).toHaveBeenCalledTimes(1);

    await usuario.click(screen.getByRole("button", { name: "Consultar" }));
    expect(resumenMock).toHaveBeenCalledTimes(2);
    expect(resumenMock).toHaveBeenLastCalledWith(
      expect.objectContaining({ desde: expect.any(String), hasta: expect.any(String) })
    );
  });

  it("sin permiso muestra la denegación en la misma pantalla", async () => {
    resumenMock.mockRejectedValue(
      new ApiRequestError(403, { codigo: "NO_AUTORIZADO", mensaje: "x", detalles: [] })
    );
    render(<InicioClient sesion={sesion("TECNICO", [7])} />);
    expect(await screen.findByRole("alert")).toHaveTextContent("No tienes acceso a los reportes.");
  });

  it("periodo inválido muestra el mensaje del servidor", async () => {
    resumenMock.mockRejectedValue(
      new ApiRequestError(422, { codigo: "VALIDACION", mensaje: "desde no puede ser posterior a hasta.", detalles: [] })
    );
    render(<InicioClient sesion={sesion("ADMINISTRADOR", "GLOBAL")} />);
    expect(await screen.findByRole("alert")).toHaveTextContent("desde no puede ser posterior a hasta.");
  });
  it("calcula los periodos rápidos (FE-50)", () => {
    const hoy = new Date(2026, 9, 15);
    expect(periodoRapido("este_mes", hoy)).toEqual({ desde: "2026-10-01", hasta: "2026-10-31" });
    expect(periodoRapido("mes_pasado", hoy)).toEqual({ desde: "2026-09-01", hasta: "2026-09-30" });
    expect(periodoRapido("proximos_30", hoy)).toEqual({ desde: "2026-10-15", hasta: "2026-11-13" });
  });

  it("un periodo rápido consulta al instante y conserva el laboratorio; editar una fecha pasa a Personalizado", async () => {
    const usuario = userEvent.setup();
    resumenMock.mockResolvedValue(RESUMEN);
    render(<InicioClient sesion={sesion("TECNICO", [7])} />);
    await screen.findByText("serie-por-fecha");
    expect(screen.getByRole("button", { name: "Este mes" })).toHaveAttribute("aria-pressed", "true");

    resumenMock.mockClear();
    await usuario.click(screen.getByRole("button", { name: "Mes pasado" }));
    const pasado = periodoRapido("mes_pasado");
    expect(resumenMock).toHaveBeenCalledWith({ ...pasado, id_unidad: "" });
    expect(screen.getByLabelText("Desde")).toHaveValue(pasado.desde);
    expect(screen.getByRole("button", { name: "Mes pasado" })).toHaveAttribute("aria-pressed", "true");

    resumenMock.mockClear();
    await usuario.clear(screen.getByLabelText("Desde"));
    await usuario.type(screen.getByLabelText("Desde"), "2026-01-01");
    expect(screen.getByRole("button", { name: "Personalizado" })).toHaveAttribute("aria-pressed", "true");
    expect(resumenMock).not.toHaveBeenCalled();
  });

  it("muestra las reservas pendientes con sus acciones al entrar (FE-51)", async () => {
    resumenMock.mockResolvedValue(RESUMEN);
    pendientesMock.mockResolvedValue({
      datos: [{
        id: 31, id_cuenta: 9, id_unidad: 7, estado: "SOLICITADA", tipo_reserva: "ESPACIO", objeto: "Práctica de redes",
        unidad_nombre: "Redes", solicitante_nombre: "Ana", periodo: { fecha: "2026-10-20", hora_inicio: "08:00:00", hora_fin: "10:00:00" },
      }],
      paginacion: { pagina: 1, tamano: 5, total: 7, paginas: 2 },
    });
    render(<InicioClient sesion={sesion("TECNICO", [7])} />);
    const region = await screen.findByRole("region", { name: "Pendientes de decisión" });
    expect(pendientesMock).toHaveBeenCalledWith({ estado: "SOLICITADA", tamano: 5 });
    expect(await within(region).findByText("Práctica de redes")).toBeInTheDocument();
    expect(within(region).getByRole("button", { name: "Aprobar" })).toBeInTheDocument();
    expect(within(region).getByRole("button", { name: "Rechazar" })).toBeInTheDocument();
    expect(within(region).getByRole("link", { name: "Ver todas (7)" })).toHaveAttribute("href", "/reservas");
  });

  it("sin pendientes lo dice, y el Usuario no llama al listado (FE-51)", async () => {
    resumenMock.mockResolvedValue(RESUMEN);
    const primera = render(<InicioClient sesion={sesion("TECNICO", [7])} />);
    expect(await screen.findByText("No hay reservas pendientes.")).toBeInTheDocument();
    primera.unmount();
    pendientesMock.mockClear();
    render(<InicioClient sesion={sesion("USUARIO", [])} />);
    expect(pendientesMock).not.toHaveBeenCalled();
    expect(screen.queryByRole("region", { name: "Pendientes de decisión" })).toBeNull();
  });

  it("una sesión caducada al cargar los pendientes lleva al login (FE-51)", async () => {
    resumenMock.mockResolvedValue(RESUMEN);
    pendientesMock.mockRejectedValue(new ApiRequestError(401, { codigo: "SESION_INVALIDA", mensaje: "x", detalles: [] }));
    render(<InicioClient sesion={sesion("TECNICO", [7])} />);
    await waitFor(() => expect(router.replace).toHaveBeenCalledWith("/login?motivo=sesion_vencida"));
  });
});
