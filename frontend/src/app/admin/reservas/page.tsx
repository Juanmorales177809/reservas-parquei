'use client';

import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { actualizarReserva, cambiarEstado, eliminarReserva, listarReservas } from '@/services/reservas';
import type { Reserva, ReservaEstadoUpdate } from '@/types/reserva';
import LoadingSpinner from '@/components/LoadingSpinner';
import ProtectedRoute from '@/components/ProtectedRoute';
import { badgeEstadoReserva, labelEstadoReserva } from '@/utils/estados';

export default function AdminReservasPage() {
  const { isAuthenticated, user } = useAuth();
  const [reservas, setReservas] = useState<Reserva[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState<Reserva | null>(null);
  const [highlightedReservaId, setHighlightedReservaId] = useState<number | null>(null);

  useEffect(() => {
    const reservaId = Number(new URLSearchParams(window.location.search).get('reserva_id'));
    setHighlightedReservaId(Number.isInteger(reservaId) && reservaId > 0 ? reservaId : null);
  }, []);

  const loadReservas = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setReservas(await listarReservas());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron cargar las reservas');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) void loadReservas();
  }, [isAuthenticated, loadReservas]);

  useEffect(() => {
    if (!loading && highlightedReservaId && reservas.some((reserva) => reserva.id === highlightedReservaId)) {
      document.getElementById(`reserva-${highlightedReservaId}`)?.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
    }
  }, [highlightedReservaId, loading, reservas]);

  async function handleDelete(id: number) {
    if (!window.confirm('¿Eliminar esta reserva definitivamente?')) return;
    setError(null);
    try {
      await eliminarReserva(id);
      await loadReservas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo eliminar la reserva');
    }
  }

  async function handleUpdate() {
    if (!editing) return;
    setError(null);
    try {
      await actualizarReserva(editing.id, {
        fecha: editing.fecha,
        hora_inicio: editing.hora_inicio.slice(0, 5),
        hora_fin: editing.hora_fin.slice(0, 5),
        asistentes: editing.asistentes,
      });
      setEditing(null);
      await loadReservas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo editar la reserva');
    }
  }

  async function handleEstado(id: number, nuevo_estado: ReservaEstadoUpdate['nuevo_estado']) {
    setError(null);
    try {
      await cambiarEstado(id, nuevo_estado);
      await loadReservas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo actualizar la reserva');
    }
  }

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <ProtectedRoute roles={['admin', 'gestor']} redirectForbidden="/">
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-text-primary sm:text-3xl">Administrar reservas</h1>
        <p className="mt-1 text-text-secondary">Gestioná las solicitudes de reserva</p>
      </div>

      {error && <div className="message-error mb-6">{error}</div>}

      <div className="mb-3 flex justify-end">
        <Link
          href="/espacios"
          className="text-3xl font-light leading-none text-primary-600 transition-colors hover:text-primary-700"
          aria-label="Crear una reserva"
          title="Crear una reserva"
        >
          +
        </Link>
      </div>

      {loading && <LoadingSpinner />}

      {!loading && reservas.length === 0 && (
        <div className="card py-12 text-center">
          <p className="text-text-muted">No hay reservas registradas.</p>
        </div>
      )}

      {!loading && reservas.length > 0 && (
        <div className="card p-0 overflow-hidden">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Recurso</th>
                  <th>Espacio</th>
                  <th>Fecha</th>
                  <th>Horario</th>
                  <th>Asistentes</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {reservas.map((reserva) => (
                  <tr
                    id={`reserva-${reserva.id}`}
                    key={reserva.id}
                    className={highlightedReservaId === reserva.id ? '[&>td]:bg-primary-50' : ''}
                  >
                    <td className="font-medium">{reserva.usuario.username}</td>
                    <td className="font-medium">{reserva.recurso.nombre}</td>
                    <td>{reserva.recurso.espacio.nombre}</td>
                    <td>
                      {editing?.id === reserva.id ? (
                        <input
                          className="input"
                          type="date"
                          aria-label="Fecha de la reserva"
                          value={editing.fecha}
                          onChange={(e) => setEditing({ ...editing, fecha: e.target.value })}
                        />
                      ) : reserva.fecha}
                    </td>
                    <td>
                      {editing?.id === reserva.id ? (
                        <div className="flex gap-2">
                          <input
                            className="input"
                            type="time"
                            aria-label="Hora de inicio de la reserva"
                            value={editing.hora_inicio.slice(0, 5)}
                            onChange={(e) => setEditing({ ...editing, hora_inicio: e.target.value })}
                          />
                          <input
                            className="input"
                            type="time"
                            aria-label="Hora de fin de la reserva"
                            value={editing.hora_fin.slice(0, 5)}
                            onChange={(e) => setEditing({ ...editing, hora_fin: e.target.value })}
                          />
                        </div>
                      ) : `${reserva.hora_inicio.slice(0, 5)} - ${reserva.hora_fin.slice(0, 5)}`}
                    </td>
                    <td>
                      {editing?.id === reserva.id ? (
                        <input
                          className="input w-20"
                          type="number"
                          min={1}
                          aria-label="Asistentes"
                          value={editing.asistentes}
                          onChange={(e) => setEditing({ ...editing, asistentes: Number(e.target.value) })}
                        />
                      ) : reserva.asistentes}
                    </td>
                    <td>
                      <span className={`badge ${badgeEstadoReserva(reserva.estado)}`}>
                        {labelEstadoReserva(reserva.estado)}
                      </span>
                    </td>
                    <td>
                      <div className="flex gap-2">
                        {editing?.id === reserva.id ? (
                          <>
                            <button className="btn btn-success btn-sm" onClick={handleUpdate} type="button">
                              Guardar
                            </button>
                            <button className="btn btn-secondary btn-sm" onClick={() => setEditing(null)} type="button">
                              Cancelar
                            </button>
                          </>
                        ) : (
                          <>
                            <button className="btn btn-secondary btn-sm" onClick={() => setEditing(reserva)} type="button">
                              Editar
                            </button>
                            {reserva.estado === 'esperando' && (
                              <>
                                <button
                                  className="btn btn-success btn-sm"
                                  onClick={() => handleEstado(reserva.id, 'aprobada')}
                                  type="button"
                                >
                                  Aprobar
                                </button>
                                <button
                                  className="btn btn-danger btn-sm"
                                  onClick={() => handleEstado(reserva.id, 'rechazada')}
                                  type="button"
                                >
                                  Rechazar
                                </button>
                              </>
                            )}
                            <button
                              className="btn btn-danger btn-sm"
                              onClick={() => handleDelete(reserva.id)}
                              type="button"
                            >
                              Eliminar
                            </button>
                            {user?.rol === 'gestor' && ['esperando', 'aprobada'].includes(reserva.estado) && (
                              <button
                                className="btn btn-sm bg-gray-500 text-white hover:bg-gray-600"
                                onClick={() => handleEstado(reserva.id, 'cancelada')}
                                type="button"
                              >
                                Cancelar
                              </button>
                            )}
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
    </ProtectedRoute>
  );
}
