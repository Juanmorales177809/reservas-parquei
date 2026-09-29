import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { GestionReservaClient } from "@/src/components/reservas/GestionReservaClient";
import type { ContextoSesion } from "@/src/lib/auth-types";
import { ApiRequestError } from "@/src/lib/http";
import { elegir } from "@/src/test-utils";

vi.mock("next/navigation", () => ({
  useParams: () => ({ id: "501" }),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

const detalleMock = vi.fn();
const aceptarMock = vi.fn();
const finalizarMock = vi.fn();
const aprobarMock = vi.fn();
const viabilidadMock = vi.fn();
const formularioMock = vi.fn();
const agregarMock = vi.fn();
const editarMock = vi.fn();

const acompanantesMock = vi.fn();
const OPCIONES_CONTEXTO = {
  tipo_cuenta: "USUARIO",
  proyectos: [{ id: 12, codigo: "P-12", nombre: "Ensayos" }, { id: 13, codigo: "P-13", nombre: "Otro proyecto" }],
  semilleros: [], pasantias: [], trabajos_grado: [],
  actividades: [{ id: 2, nombre: "Feria", dependencia: "Extensión" }],
};
const ESPACIO_DETALLE = {
  id: 3, id_unidad: 7, nombre: "Sala de Redes", capacidad: 5, habilitado: true, ubicacion: null, descripcion: null, horario_unidad: null,
  recursos: [{ recurso_id: 43, nombre: "Cables", habilitado: true }],
  campos: [{ id: 5, nombre: "Ensayo previsto", tipo: "TEXTO", obligatorio: true, orden: 0, habilitado: true }],
};
vi.mock("@/src/lib/espacios-api", () => ({
  listarEspacios: () => Promise.resolve({ datos: [{ id: 3, id_unidad: 7, nombre: "Sala de Redes", capacidad: 5, habilitado: true }, { id: 4, id_unidad: 7, nombre: "Sala B", capacidad: 8, habilitado: true }] }),
  detalleEspacio: (id: number) => Promise.resolve(id === 4 ? { ...ESPACIO_DETALLE, id: 4, nombre: "Sala B", capacidad: 8, recursos: [], campos: [] } : ESPACIO_DETALLE),
}));
vi.mock("@/src/lib/recursos-api", () => ({
  detalleRecurso: () => Promise.resolve({ especializacion: {} }),
  listarRecursos: () =>
    Promise.resolve({
      datos: [
        { id: 41, tipo: "MOBILIARIO", nombre: "Mesa", id_unidad: 7, habilitado: true },
        { id: 43, tipo: "OTRO", nombre: "Cables", id_unidad: 7, habilitado: true },
      ],
    }),
}));

const ORDEN = {
  id: 1, reserva_id: 501, fecha_generacion: "2026-09-01T10:00:00Z", razon_solicitud: "Práctica de campo",
  nombre_actividad_evento: null, lugar_nombre: "Sede Robledo", lugar_direccion: "Calle 1", dependencia_solicitante_snapshot: "Facultad",
  fecha_retiro_snapshot: "2030-08-04", fecha_regreso_snapshot: "2030-08-06", proyecto_codigo_snapshot: "P-1",
  responsable_nombre_snapshot: "Ana Ruiz", responsable_cedula_snapshot: "1", responsable_correo_snapshot: "a@itm.edu.co",
  responsable_telefono_snapshot: "300", observaciones: null, actividades: [],
  items: [{ reserva_recurso_id: 11, placa_snapshot: "PL-9", descripcion_snapshot: "Osciloscopio", bodega_snapshot: null, cc_snapshot: null, fecha_compra_snapshot: null }],
};

vi.mock("@/src/lib/reservas-api", () => ({
  detalleReserva: (...args: unknown[]) => detalleMock(...args),
  aprobarReserva: (...args: unknown[]) => aprobarMock(...args),
  rechazarReserva: vi.fn(),
  crearPropuesta: vi.fn(),
  aceptarPropuesta: (...args: unknown[]) => aceptarMock(...args),
  rechazarPropuesta: vi.fn(),
  ejecutarReserva: vi.fn(),
  finalizarReserva: (...args: unknown[]) => finalizarMock(...args),
  cancelarReserva: vi.fn(),
  retirarRecurso: vi.fn(),
  registrarViabilidad: (...args: unknown[]) => viabilidadMock(...args),
  diligenciarFormulario: (...args: unknown[]) => formularioMock(...args),
  agregarRecursos: (...args: unknown[]) => agregarMock(...args),
  editarReserva: (...args: unknown[]) => editarMock(...args),
  ordenSalida: () => Promise.resolve(ORDEN),
  urlOrdenSalidaPdf: (id: number) => `/api/reservas/${id}/orden-salida.pdf`,
  urlCalendario: (id: number) => `/api/reservas/${id}/calendario.ics`,
  opcionesContexto: () => Promise.resolve(OPCIONES_CONTEXTO),
  opcionesAcompanantes: (...a: unknown[]) => acompanantesMock(...a),
  consultarDisponibilidad: () => Promise.resolve({ horario_unidad: { dias_atencion: [], hora_apertura: "07:00", hora_cierre: "19:00" }, franjas: [] }),
  listarAdjuntos: () => Promise.resolve({ datos: [] }),
  subirAdjunto: vi.fn(),
  urlAdjunto: () => "#",
}));

const SESION_BASE: ContextoSesion = {
  id_cuenta: 1042,
  tipo_cuenta: "USUARIO",
  rol: "USUARIO",
  correo: "u@itm.edu.co",
  actualizacion_inicial_pendiente: false,
  id_sesion: "s",
  unidades_autorizadas: [],
  autenticacion_reciente: false,
};
const REPORTERO: ContextoSesion = { ...SESION_BASE, id_cuenta: 900, tipo_cuenta: "PERSONAL", rol: "TECNICO", unidades_autorizadas: [7] };

const DETALLE_BASE = {
  id: 501,
  id_unidad: 7,
  id_cuenta: 1042,
  observacion: null,
  requiere_apoyo: false,
  created_at: "2026-01-01",
  updated_at: "2026-01-01",
  fecha_aprobacion: null,
  fecha_cancelacion: null,
  motivo_cancelacion: null,
  detalle: {},
  contexto: {},
  recursos: [],
  acompanantes: [],
  campos_adicionales: [],
  historial: [],
  propuesta_vigente: null,
  lista_espera: null,
};

const LISTA = (extra: Record<string, unknown> = {}) => ({
  ...DETALLE_BASE,
  estado: "SOLICITADA",
  tipo_reserva: "LISTA_ESPERA",
  lista_espera: {
    viable: null, fecha_evaluacion_viabilidad: null, fecha_recepcion_material: null, prioridad: null,
    horas_ejecucion: null, formulario: null, ...extra,
  },
});

// FE-19 y FE-26 (WF-RES-02, WF-RES-03): cada rol ve solo lo que le corresponde.
describe("GestionReservaClient", () => {
  beforeEach(() => {
    for (const m of [detalleMock, aceptarMock, finalizarMock, aprobarMock, viabilidadMock, formularioMock, agregarMock, editarMock, acompanantesMock]) m.mockReset();
    acompanantesMock.mockResolvedValue({ datos: [] });
  });

  it("aceptar propuesta vigente reprograma y conserva el estado", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE_BASE,
      estado: "SOLICITADA",
      tipo_reserva: "ESPACIO",
      propuesta_vigente: {
        id: 9, origen: "TECNICO", fecha_inicio_propuesta: "2030-08-05",
        fecha_fin_propuesta: "2030-08-05", hora_inicio: "14:00", hora_fin: "16:00",
        motivo: "Mantenimiento", created_at: "2026-01-01",
      },
    });
    aceptarMock.mockResolvedValue({});

    render(<GestionReservaClient sesion={SESION_BASE} />);
    await usuario.click(await screen.findByRole("button", { name: "Aceptar" }));
    await waitFor(() => {
      expect(aceptarMock).toHaveBeenCalledWith(501);
    });
    // El reservista no ve acciones de gestión (RN-PRO-03).
    expect(screen.queryByRole("button", { name: "Aprobar" })).not.toBeInTheDocument();
  });

  it("la propuesta del técnico solo la responde el reservista, no el técnico (RN-PROP-03)", async () => {
    detalleMock.mockResolvedValue({
      ...DETALLE_BASE, estado: "SOLICITADA", tipo_reserva: "ESPACIO",
      propuesta_vigente: { id: 9, origen: "TECNICO", fecha_inicio_propuesta: "2030-08-05", fecha_fin_propuesta: "2030-08-05", hora_inicio: null, hora_fin: null, motivo: "Mantenimiento", created_at: "x" },
    });
    render(<GestionReservaClient sesion={REPORTERO} />);
    expect(await screen.findByText(/Esperando la respuesta de el reservista/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Aceptar" })).not.toBeInTheDocument();
  });

  it("finalizar campus sin devolución muestra el error sin cerrar", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE_BASE,
      estado: "EN_EJECUCION",
      tipo_reserva: "RECURSO_CAMPUS",
      recursos: [{ reserva_recurso_id: 11, recurso_id: 41, rol: "PRINCIPAL", estado_asignacion: "ASIGNADO" }],
    });
    finalizarMock.mockRejectedValue(
      new ApiRequestError(409, { codigo: "ESTADO_INCOMPATIBLE", mensaje: "x", detalles: [] })
    );

    render(<GestionReservaClient sesion={REPORTERO} />);
    await usuario.click(await screen.findByRole("button", { name: "Registrar devolución completa y finalizar" }));
    await waitFor(() => {
      expect(finalizarMock).toHaveBeenCalledTimes(1);
    });
    expect(await screen.findByText("La reserva ya no está en un estado válido para esta acción.")).toBeInTheDocument();
  });

  it("lista de espera: el técnico evalúa la viabilidad y una negativa exige motivo (RN-TIP-PLE-03)", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue(LISTA());
    viabilidadMock.mockResolvedValue({});
    render(<GestionReservaClient sesion={REPORTERO} />);
    const noViable = await screen.findByRole("button", { name: "No es viable" });
    expect(noViable).toBeDisabled();
    await usuario.type(screen.getByLabelText("Motivo si no es viable"), "Fuera de alcance");
    await usuario.click(noViable);
    await waitFor(() => {
      expect(viabilidadMock).toHaveBeenCalledWith(501, false, "Fuera de alcance");
    });
  });

  it("lista de espera: el reservista diligencia solo su parte y no ve la aprobación (RN-TIP-PLE-04)", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue(LISTA({ viable: true }));
    formularioMock.mockResolvedValue({});
    render(<GestionReservaClient sesion={SESION_BASE} />);
    await usuario.type(await screen.findByLabelText("Campo"), "Material");
    await usuario.type(screen.getByLabelText("Valor"), "Aluminio 6061");
    await usuario.click(screen.getByRole("button", { name: "Guardar parte del reservista" }));
    await waitFor(() => {
      expect(formularioMock).toHaveBeenCalledWith(501, { datos_usuario: { Material: "Aluminio 6061" } });
    });
    expect(screen.queryByRole("button", { name: "Registrar recepción y aprobar" })).not.toBeInTheDocument();
    // La parte técnica no es del reservista: ni se le ofrece editarla.
    expect(screen.queryByRole("button", { name: "Guardar parte técnica" })).not.toBeInTheDocument();
  });

  it("lista de espera: aprobar exige confirmar la recepción y todo el formulario revisado (RN-TIP-PLE-05)", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue(
      LISTA({
        viable: true,
        formulario: {
          datos_usuario: { Material: "Aluminio" }, datos_tecnico: { Proceso: "Corte CNC" },
          diligenciado_at: "2026-09-01T10:00:00Z", revisado_por: 900, revisado_at: "2026-09-02T10:00:00Z",
        },
      })
    );
    aprobarMock.mockResolvedValue({});
    render(<GestionReservaClient sesion={REPORTERO} />);
    const aprobar = await screen.findByRole("button", { name: "Registrar recepción y aprobar" });
    expect(aprobar).toBeDisabled(); // falta confirmar la recepción
    await usuario.click(screen.getByRole("checkbox", { name: "Confirmo que el material fue recibido" }));
    expect(aprobar).toBeEnabled();
    await usuario.click(aprobar);
    await waitFor(() => {
      expect(aprobarMock).toHaveBeenCalledWith(501, { material_recibido: true });
    });
  });

  it("lista de espera sin la parte del reservista: la aprobación indica qué falta", async () => {
    detalleMock.mockResolvedValue(LISTA({ viable: true }));
    render(<GestionReservaClient sesion={REPORTERO} />);
    expect(await screen.findByText(/Falta: la parte del reservista/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Registrar recepción y aprobar" })).toBeDisabled();
  });

  it("muestra nombres y no identificadores: unidad, solicitante, espacio, recursos, contexto y acompañantes", async () => {
    detalleMock.mockResolvedValue({
      ...DETALLE_BASE, estado: "APROBADA", tipo_reserva: "ESPACIO",
      unidad_nombre: "Laboratorio de Redes", solicitante_nombre: "Camila Torres",
      detalle: { espacio_nombre: "Sala de Redes", fecha: "2030-08-04", hora_inicio: "10:00:00", hora_fin: "12:00:00", asistentes: 1 },
      contexto: { proyecto_nombre: "Ensayos", proyecto_codigo: "P-12" },
      acompanantes_detalle: [{ id_cuenta: 99, nombre: "Luis Mora" }],
      recursos: [{ reserva_recurso_id: 1, recurso_id: 41, nombre: "Mesa de soldadura", rol: "ADICIONAL", estado_asignacion: "ASIGNADO" }],
      historial: [{ estado_anterior: null, estado_nuevo: "APROBADA", actor_cuenta_id: 900, actor_nombre: "Ana Técnica", motivo: null, created_at: "2026-09-01T10:00:00Z" }],
    });
    render(<GestionReservaClient sesion={SESION_BASE} />);
    expect(await screen.findByText("Espacio · Aprobada")).toBeInTheDocument();
    for (const t of ["Laboratorio de Redes", "Camila Torres", "Sala de Redes", "Ensayos (P-12)", "Luis Mora"]) {
      expect(screen.getByText(t)).toBeInTheDocument();
    }
    expect(screen.getByText(/Mesa de soldadura · adicional/)).toBeInTheDocument();
    expect(screen.getByText(/Ana Técnica/)).toBeInTheDocument();
    expect(screen.queryByText(/Recurso 41/)).not.toBeInTheDocument();
    // El calendario solo se ofrece a una reserva de espacio o interno aprobada (RN-CAL-01).
    expect(screen.getByRole("link", { name: /calendario/ })).toHaveAttribute("href", "/api/reservas/501/calendario.ics");
  });

  it("campus aprobada muestra la orden de salida con su PDF y no ofrece calendario", async () => {
    detalleMock.mockResolvedValue({ ...DETALLE_BASE, estado: "APROBADA", tipo_reserva: "RECURSO_CAMPUS" });
    render(<GestionReservaClient sesion={SESION_BASE} />);
    expect(await screen.findByText("Sede Robledo — Calle 1")).toBeInTheDocument();
    expect(screen.getByText(/Osciloscopio · placa PL-9/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /PDF/ })).toHaveAttribute("href", "/api/reservas/501/orden-salida.pdf");
    expect(screen.queryByRole("link", { name: /calendario/ })).not.toBeInTheDocument();
  });

  it("el técnico agrega recursos por nombre a una reserva de espacio (RN-TIP-PE-21)", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE_BASE, estado: "SOLICITADA", tipo_reserva: "ESPACIO",
      recursos: [{ reserva_recurso_id: 1, recurso_id: 41, nombre: "Mesa", rol: "ADICIONAL", estado_asignacion: "ASIGNADO" }],
    });
    agregarMock.mockResolvedValue({});
    render(<GestionReservaClient sesion={REPORTERO} />);
    // Lo ya asignado no se vuelve a ofrecer.
    const cables = await screen.findByRole("checkbox", { name: "Cables · Otro" });
    expect(screen.queryByRole("checkbox", { name: "Mesa · Mobiliario" })).not.toBeInTheDocument();
    await usuario.click(cables);
    await usuario.click(screen.getByRole("button", { name: "Agregar" }));
    await waitFor(() => {
      expect(agregarMock).toHaveBeenCalledWith(501, [{ recurso_id: 43, rol: "ADICIONAL" }]);
    });
  });

  it("el reservista edita su solicitud pendiente y solo viaja lo que cambió (RN-PRO-06)", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE_BASE, estado: "SOLICITADA", tipo_reserva: "RECURSO_INTERNO",
      detalle: { fecha: "2030-08-04", hora_inicio: "10:00:00", hora_fin: "12:00:00" },
      contexto: { proyecto_id: 12, proyecto_nombre: "Ensayos", proyecto_codigo: "P-12" },
      recursos: [{ reserva_recurso_id: 1, recurso_id: 41, nombre: "Mesa", rol: "PRINCIPAL", estado_asignacion: "ASIGNADO" }],
    });
    editarMock.mockResolvedValue({});
    render(<GestionReservaClient sesion={SESION_BASE} />);
    await usuario.click(await screen.findByRole("button", { name: "Editar solicitud" }));
    const fin = screen.getByLabelText("Hora fin");
    await usuario.clear(fin);
    await usuario.type(fin, "13:00");
    await usuario.click(screen.getByRole("button", { name: "Guardar cambios" }));
    await waitFor(() => {
      expect(editarMock).toHaveBeenCalledWith(501, { detalle: { hora_fin: "13:00" } });
    });
  });

  it("nadie edita una reserva ajena ni una que ya no está solicitada (RN-PRO-02, RN-PRO-03)", async () => {
    detalleMock.mockResolvedValue({ ...DETALLE_BASE, estado: "APROBADA", tipo_reserva: "RECURSO_INTERNO" });
    render(<GestionReservaClient sesion={SESION_BASE} />);
    await screen.findByText("Recurso interno · Aprobada");
    expect(screen.queryByRole("button", { name: "Editar solicitud" })).not.toBeInTheDocument();
  });

  it("editar el contexto, los recursos y el apoyo envía cada bloque completo y solo si cambió (RN-PRO-06)", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE_BASE, estado: "SOLICITADA", tipo_reserva: "RECURSO_INTERNO",
      detalle: { fecha: "2030-08-04", hora_inicio: "10:00:00", hora_fin: "12:00:00" },
      contexto: { proyecto_id: 12, proyecto_nombre: "Ensayos", proyecto_codigo: "P-12" },
      recursos: [{ reserva_recurso_id: 1, recurso_id: 41, nombre: "Mesa", rol: "PRINCIPAL", estado_asignacion: "ASIGNADO" }],
    });
    editarMock.mockResolvedValue({});
    render(<GestionReservaClient sesion={SESION_BASE} />);
    await usuario.click(await screen.findByRole("button", { name: "Editar solicitud" }));
    // Contexto precargado: no se preselecciona nada distinto.
    expect(await screen.findByLabelText("Proyecto")).toHaveValue("12");
    await elegir(usuario, "Proyecto", "Otro proyecto (P-13)");
    await usuario.click(await screen.findByRole("checkbox", { name: "Cables · Otro" }));
    await usuario.click(screen.getByRole("checkbox", { name: /Necesito acompañamiento/ }));
    await usuario.click(screen.getByRole("button", { name: "Guardar cambios" }));
    await waitFor(() => {
      expect(editarMock).toHaveBeenCalledWith(501, {
        contexto: { proyecto_id: 13 },
        recursos: [{ recurso_id: 41, rol: "PRINCIPAL" }, { recurso_id: 43, rol: "ADICIONAL" }],
        requiere_apoyo: true,
      });
    });
  });

  it("no deja guardar una solicitud sin contexto (RN-CTX-01)", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE_BASE, estado: "SOLICITADA", tipo_reserva: "LISTA_ESPERA",
      detalle: { descripcion_necesidad: "Pieza" },
      contexto: { actividad_institucional_id: 2, actividad_nombre: "Feria" },
      lista_espera: { viable: null, fecha_evaluacion_viabilidad: null, fecha_recepcion_material: null, prioridad: null, horas_ejecucion: null, formulario: null },
    });
    render(<GestionReservaClient sesion={SESION_BASE} />);
    await usuario.click(await screen.findByRole("button", { name: "Editar solicitud" }));
    await elegir(usuario, "Actividad institucional (reemplaza a lo anterior)", "Ninguna");
    await usuario.click(screen.getByRole("button", { name: "Guardar cambios" }));
    expect(await screen.findByText(/Elige el proyecto, semillero, pasantía/)).toBeInTheDocument();
    expect(editarMock).not.toHaveBeenCalled();
  });

  it("lista de espera: cambiar la descripción tras una evaluación avisa de la nueva viabilidad (RN-TIP-PLE-09)", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE_BASE, estado: "SOLICITADA", tipo_reserva: "LISTA_ESPERA",
      detalle: { descripcion_necesidad: "Pieza" },
      contexto: { proyecto_id: 12, proyecto_nombre: "Ensayos", proyecto_codigo: "P-12" },
      lista_espera: { viable: true, fecha_evaluacion_viabilidad: "2026-09-01T10:00:00Z", fecha_recepcion_material: null, prioridad: null, horas_ejecucion: null, formulario: null },
    });
    editarMock.mockResolvedValue({});
    render(<GestionReservaClient sesion={SESION_BASE} />);
    await usuario.click(await screen.findByRole("button", { name: "Editar solicitud" }));
    const descripcion = screen.getByLabelText("Descripción de la necesidad");
    await usuario.clear(descripcion);
    await usuario.type(descripcion, "Pieza de aluminio");
    expect(screen.getByText(/invalida la evaluación de viabilidad/)).toBeInTheDocument();
    await usuario.click(screen.getByRole("button", { name: "Guardar cambios" }));
    await waitFor(() => expect(editarMock).toHaveBeenCalledWith(501, { detalle: { descripcion_necesidad: "Pieza de aluminio" } }));
    expect(await screen.findByText(/evaluar de nuevo la viabilidad/)).toBeInTheDocument();
  });

  it("espacio: cambiar de espacio pide sus campos de nuevo y los envía junto con los acompañantes (RN-PRO-06)", async () => {
    const usuario = userEvent.setup();
    detalleMock.mockResolvedValue({
      ...DETALLE_BASE, estado: "SOLICITADA", tipo_reserva: "ESPACIO",
      detalle: { espacio_id: 3, espacio_nombre: "Sala de Redes", fecha: "2030-08-04", hora_inicio: "10:00:00", hora_fin: "12:00:00", asistentes: 0 },
      contexto: { proyecto_id: 12, proyecto_nombre: "Ensayos", proyecto_codigo: "P-12" },
      campos_adicionales: [{ campo_id: 5, campo_nombre: "Ensayo previsto", valor_texto: "Tracción", opcion_id: null }],
    });
    acompanantesMock.mockResolvedValue({ datos: [{ id_cuenta: 99, nombre: "Camila Torres" }] });
    editarMock.mockResolvedValue({});
    render(<GestionReservaClient sesion={SESION_BASE} />);
    await usuario.click(await screen.findByRole("button", { name: "Editar solicitud" }));
    // El campo obligatorio llega con su valor actual.
    expect(await screen.findByLabelText("Ensayo previsto")).toHaveValue("Tracción");
    await usuario.click(await screen.findByRole("checkbox", { name: "Camila Torres" }));
    await elegir(usuario, "Espacio", "Sala B (cap. 8)");
    await usuario.click(screen.getByRole("button", { name: "Guardar cambios" }));
    await waitFor(() => {
      expect(editarMock).toHaveBeenCalledWith(501, expect.objectContaining({
        detalle: { espacio_id: 4 },
        acompanantes: [99],
        campos_adicionales: [],
      }));
    });
  });
});
