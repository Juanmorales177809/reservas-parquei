import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import EspaciosPage from './page';
import { AuthProvider } from '@/context/AuthContext';
import type { DisponibilidadSlot, Espacio } from '@/types/espacio';
import type { Recurso } from '@/types/recurso';

const { listarEspaciosMock, listarRecursosMock, getDisponibilidadMock, crearReservaMock } =
  vi.hoisted(() => ({
    listarEspaciosMock: vi.fn(),
    listarRecursosMock: vi.fn(),
    getDisponibilidadMock: vi.fn(),
    crearReservaMock: vi.fn(),
  }));

vi.mock('@/services/espacios', () => ({ listarEspacios: listarEspaciosMock }));
vi.mock('@/services/recursos', () => ({
  listarRecursos: listarRecursosMock,
  getDisponibilidadRecurso: getDisponibilidadMock,
}));
vi.mock('@/services/reservas', () => ({ crearReserva: crearReservaMock }));

function espacio(parcial: Partial<Espacio> = {}): Espacio {
  return {
    id: 1,
    nombre: 'Sala Activa',
    ubicacion: 'Piso 1',
    capacidad: 10,
    estado: 'activo',
    dias_atencion: [0, 1, 2, 3, 4, 5],
    hora_apertura: '07:00:00',
    hora_cierre: '20:00:00',
    horario_atencion: { 0: [7, 8, 9, 10, 11] },
    horas_antelacion: 24,
    ...parcial,
  };
}

function recurso(parcial: Partial<Recurso> = {}): Recurso {
  return {
    id: 7,
    nombre: 'Proyector',
    espacio_id: 1,
    tipo_recurso_id: 1,
    descripcion: null,
    capacidad: 10,
    estado: 'activo',
    tipo: { id: 1, nombre: 'General', descripcion: '', activo: 'activo' },
    espacio: espacio(),
    ...parcial,
  };
}

const SLOTS: DisponibilidadSlot[] = [
  { hora_inicio: '08:00', hora_fin: '09:00', estado: 'libre' },
  { hora_inicio: '09:00', hora_fin: '10:00', estado: 'libre' },
  { hora_inicio: '10:00', hora_fin: '11:00', estado: 'libre' },
  { hora_inicio: '11:00', hora_fin: '12:00', estado: 'libre' },
];

beforeEach(() => {
  listarEspaciosMock.mockReset();
  listarRecursosMock.mockReset();
  getDisponibilidadMock.mockReset();
  crearReservaMock.mockReset();
  listarEspaciosMock.mockResolvedValue([espacio()]);
  listarRecursosMock.mockResolvedValue([recurso()]);
  getDisponibilidadMock.mockResolvedValue(SLOTS);
  crearReservaMock.mockResolvedValue({ id: 42, estado: 'esperando' });
});

function renderPagina() {
  return render(
    <AuthProvider>
      <EspaciosPage />
    </AuthProvider>,
  );
}

describe('EspaciosPage: listado público', () => {
  it('muestra el estado de carga mientras se consulta el backend', () => {
    listarEspaciosMock.mockReturnValue(new Promise(() => {}));
    renderPagina();
    expect(screen.getByText('Cargando espacios...')).toBeInTheDocument();
  });

  it('renderiza solo los espacios activos recibidos', async () => {
    renderPagina();
    expect(await screen.findByText('Sala Activa')).toBeInTheDocument();
    expect(screen.getByText('Activo')).toBeInTheDocument();
  });

  it('muestra el mensaje vacío cuando no hay espacios activos', async () => {
    listarEspaciosMock.mockResolvedValue([]);
    listarRecursosMock.mockResolvedValue([]);
    renderPagina();
    expect(await screen.findByText('No hay espacios activos.')).toBeInTheDocument();
  });

  it('no renderiza espacios inactivos aunque llegaran en la respuesta (defensa cliente)', async () => {
    listarEspaciosMock.mockResolvedValue([espacio(), espacio({ id: 2, nombre: 'Sala Inactiva', estado: 'inactivo' })]);
    renderPagina();
    await screen.findByText('Sala Activa');
    expect(screen.queryByText('Sala Inactiva')).not.toBeInTheDocument();
  });

  it('muestra el mensaje de error cuando falla la consulta', async () => {
    listarEspaciosMock.mockRejectedValue(new Error('No se pudo cargar'));
    renderPagina();
    expect(await screen.findByText('No se pudo cargar')).toBeInTheDocument();
  });
});

describe('EspaciosPage: modal de reserva', () => {
  it('abre un diálogo accesible con nombre accesible', async () => {
    const usuario = userEvent.setup();
    renderPagina();
    await usuario.click(await screen.findByRole('button', { name: 'Disponibilidad' }));
    const dialogo = await screen.findByRole('dialog', { name: 'Sala Activa' });
    expect(dialogo).toHaveAttribute('aria-modal', 'true');
  });

  it('enfoca el botón Cerrar al abrir el diálogo', async () => {
    const usuario = userEvent.setup();
    renderPagina();
    await usuario.click(await screen.findByRole('button', { name: 'Disponibilidad' }));
    const cerrar = await screen.findByRole('button', { name: 'Cerrar' });
    expect(document.activeElement).toBe(cerrar);
  });

  it('cierra con Escape y restaura el foco al disparador', async () => {
    const usuario = userEvent.setup();
    renderPagina();
    const disparador = await screen.findByRole('button', { name: 'Disponibilidad' });
    await usuario.click(disparador);
    await screen.findByRole('dialog');
    await usuario.keyboard('{Escape}');
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
    expect(document.activeElement).toBe(disparador);
  });

  it('selecciona horas consecutivas y muestra el rango en el resumen', async () => {
    window.localStorage.setItem('token', 'token-de-prueba');
    window.localStorage.setItem(
      'user',
      JSON.stringify({ id: 1, username: 'u', email: 'u@test.com', rol: 'usuario', espacio: null }),
    );
    const usuario = userEvent.setup();
    renderPagina();
    await usuario.click(await screen.findByRole('button', { name: 'Disponibilidad' }));
    await usuario.click(await screen.findByRole('button', { name: /08:00 - 09:00/ }));
    await usuario.click(await screen.findByRole('button', { name: /09:00 - 10:00/ }));
    await usuario.click(await screen.findByRole('button', { name: 'Reservar recurso' }));
    expect(await screen.findByText('08:00 - 10:00')).toBeInTheDocument();
  });

  it('la selección no consecutiva reinicia la selección anterior', async () => {
    const usuario = userEvent.setup();
    renderPagina();
    await usuario.click(await screen.findByRole('button', { name: 'Disponibilidad' }));
    await usuario.click(await screen.findByRole('button', { name: /08:00 - 09:00/ }));
    await usuario.click(await screen.findByRole('button', { name: /11:00 - 12:00/ }));
    expect(screen.getAllByRole('button', { name: /seleccionado/ })).toHaveLength(1);
  });

  it('no permite confirmar sin aceptar los términos', async () => {
    window.localStorage.setItem('token', 'token-de-prueba');
    window.localStorage.setItem(
      'user',
      JSON.stringify({ id: 1, username: 'u', email: 'u@test.com', rol: 'usuario', espacio: null }),
    );
    const usuario = userEvent.setup();
    renderPagina();
    await usuario.click(await screen.findByRole('button', { name: 'Disponibilidad' }));
    await usuario.click(await screen.findByRole('button', { name: /08:00 - 09:00/ }));
    await usuario.click(await screen.findByRole('button', { name: 'Reservar recurso' }));
    const confirmar = await screen.findByRole('button', { name: 'Aceptar y reservar' });
    expect(confirmar).toBeDisabled();
  });

  it('envía el payload completo al confirmar la reserva', async () => {
    window.localStorage.setItem('token', 'token-de-prueba');
    window.localStorage.setItem(
      'user',
      JSON.stringify({ id: 1, username: 'u', email: 'u@test.com', rol: 'usuario', espacio: null }),
    );
    const usuario = userEvent.setup();
    renderPagina();
    await usuario.click(await screen.findByRole('button', { name: 'Disponibilidad' }));
    await usuario.click(await screen.findByRole('button', { name: /08:00 - 09:00/ }));
    await usuario.click(await screen.findByRole('button', { name: /09:00 - 10:00/ }));
    await usuario.click(await screen.findByRole('button', { name: 'Reservar recurso' }));
    await usuario.click(await screen.findByRole('checkbox'));
    await usuario.click(await screen.findByRole('button', { name: 'Aceptar y reservar' }));
    await waitFor(() =>
      expect(crearReservaMock).toHaveBeenCalledWith({
        recurso_id: 7,
        fecha: expect.any(String),
        hora_inicio: '08:00',
        hora_fin: '10:00',
        asistentes: 1,
      }),
    );
    expect(await screen.findByText(/Reserva #42 creada correctamente/)).toBeInTheDocument();
  });

  it('muestra el error cuando la reserva falla', async () => {
    window.localStorage.setItem('token', 'token-de-prueba');
    window.localStorage.setItem(
      'user',
      JSON.stringify({ id: 1, username: 'u', email: 'u@test.com', rol: 'usuario', espacio: null }),
    );
    crearReservaMock.mockRejectedValue(new Error('El recurso ya tiene una reserva en ese horario'));
    const usuario = userEvent.setup();
    renderPagina();
    await usuario.click(await screen.findByRole('button', { name: 'Disponibilidad' }));
    await usuario.click(await screen.findByRole('button', { name: /08:00 - 09:00/ }));
    await usuario.click(await screen.findByRole('button', { name: 'Reservar recurso' }));
    await usuario.click(await screen.findByRole('checkbox'));
    await usuario.click(await screen.findByRole('button', { name: 'Aceptar y reservar' }));
    expect(
      await screen.findByText('El recurso ya tiene una reserva en ese horario'),
    ).toBeInTheDocument();
  });

  it('sin sesión muestra el enlace para iniciar sesión en lugar del botón de reserva', async () => {
    const usuario = userEvent.setup();
    renderPagina();
    await usuario.click(await screen.findByRole('button', { name: 'Disponibilidad' }));
    expect(
      await screen.findByRole('link', { name: 'Iniciá sesión para reservar' }),
    ).toBeInTheDocument();
  });
});
