'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { actualizarReserva, cancelarMiReserva, listarMisReservas } from '@/services/reservas';
import type { Reserva } from '@/types/reserva';
import LoadingSpinner from '@/components/LoadingSpinner';
import ProtectedRoute from '@/components/ProtectedRoute';
import { badgeEstadoReserva, labelEstadoReserva } from '@/utils/estados';
import { etiquetaObjetivoReserva } from '@/utils/reservaEtiqueta';

export default function MisReservasPage() {
  const { isAuthenticated } = useAuth();
  const [reservas, setReservas] = useState<Reserva[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState<Reserva | null>(null);
  const [highlightedReservaId, setHighlightedReservaId] = useState<number | null>(null);

  useEffect(() => {
    const reservaId = Number(new URLSearchParams(window.location.search).get('reserva_id'));
    setHighlightedReservaId(Number.isInteger(reservaId) && reservaId > 0 ? reservaId : null);
  }, []);

  async function loadReservas() {
    setLoading(true);
    setError(null);
    try {
      setReservas(await listarMisReservas());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron cargar tus reservas');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (isAuthenticated) void loadReservas();
  }, [isAuthenticated]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!loading && highlightedReservaId && reservas.some((reserva) => reserva.id === highlightedReservaId)) {
      document.getElementById(`reserva-${highlightedReservaId}`)?.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
    }
  }, [highlightedReservaId, loading, reservas]);

  async function handleCancel(id: number) {
    if (!window.confirm('¿Cancelar esta reserva?')) return;
    setError(null);
    try {
      await cancelarMiReserva(id);
      await loadReservas();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo cancelar la reserva');
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

  return (
    <ProtectedRoute>
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-text-primary sm:text-3xl">Mis reservas</h1>
        <p className="mt-1 text-text-secondary">
          Todas tus solicitudes de reserva
        </p>
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
          <p className="text-text-muted">No tenés reservas registradas.</p>
        </div>
      )}

      {!loading && reservas.length > 0 && (
        <div className="card p-0 overflow-hidden">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
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
                    <td className="font-medium">{etiquetaObjetivoReserva(reserva)}</td>
                    <td>{reserva.espacio.nombre}</td>
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
                      {reserva.estado === 'rechazada' && reserva.motivo_rechazo && (
                        <div className="mt-1 text-xs text-text-secondary">Motivo: {reserva.motivo_rechazo}</div>
                      )}
                    </td>
                    <td>
                      {editing?.id === reserva.id ? (
                        <div className="flex gap-2">
                          <button className="btn btn-success btn-sm" onClick={handleUpdate} type="button">
                            Guardar
                          </button>
                          <button className="btn btn-secondary btn-sm" onClick={() => setEditing(null)} type="button">
                            Cancelar
                          </button>
                        </div>
                      ) : (
                        <div className="flex gap-2">
                          {reserva.estado === 'esperando' && (
                            <button className="btn btn-secondary btn-sm" onClick={() => setEditing(reserva)} type="button">
                              Editar
                            </button>
                          )}
                          {reserva.estado === 'aprobada' && (
                            <button
                              className="btn btn-sm bg-gray-500 text-white hover:bg-gray-600"
                              onClick={() => handleCancel(reserva.id)}
                              type="button"
                            >
                              Cancelar
                            </button>
                          )}
                        </div>
                      )}
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
