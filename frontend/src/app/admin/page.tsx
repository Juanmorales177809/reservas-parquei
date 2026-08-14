'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { cambiarEstado, listarReservas } from '@/services/reservas';
import { obtenerResumenAdmin, obtenerResumenGestor } from '@/services/admin-dashboard';
import type { Reserva } from '@/types/reserva';
import type { AdminDashboardSummary } from '@/types/admin-dashboard';
import LoadingSpinner from '@/components/LoadingSpinner';
import AdminDashboardCharts from '@/components/AdminDashboardCharts';
import ProtectedRoute from '@/components/ProtectedRoute';
import { badgeEstadoReserva, labelEstadoReserva } from '@/utils/estados';

export default function AdminDashboardPage() {
  const { isAdmin, isAuthenticated, user } = useAuth();
  const [reservas, setReservas] = useState<Reserva[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<AdminDashboardSummary | null>(null);
  const [selectedReserva, setSelectedReserva] = useState<Reserva | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [reservasData, summaryData] = await Promise.all([
        listarReservas(),
        isAdmin ? obtenerResumenAdmin() : obtenerResumenGestor(),
      ]);
      setReservas(reservasData);
      setSummary(summaryData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar datos');
    } finally {
      setLoading(false);
    }
  }, [isAdmin]);

  useEffect(() => {
    if (isAuthenticated) void loadData();
  }, [isAuthenticated, loadData]);

  async function handleAprobar(id: number) {
    try {
      await cambiarEstado(id, 'aprobada');
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo aprobar');
    }
  }

  async function handleRechazar(id: number) {
    try {
      await cambiarEstado(id, 'rechazada');
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo rechazar');
    }
  }

  if (loading) {
    return <LoadingSpinner />;
  }

  const pendientes = reservas.filter((r) => r.estado === 'esperando');
  const totalReservas = summary?.total_reservas ?? reservas.length;
  const totalPendientes = summary?.reservas_pendientes ?? pendientes.length;

  return (
    <ProtectedRoute roles={['admin', 'gestor']} redirectForbidden="/dashboard">
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-text-primary sm:text-3xl">
          {isAdmin ? 'Panel de administración' : 'Panel de gestión'}
        </h1>
        <p className="mt-1 text-text-secondary">
          Bienvenido, {user?.username ?? 'Admin'}
          {!isAdmin && summary?.espacio_nombre ? ` · ${summary.espacio_nombre}` : ''}
        </p>
      </div>

      {error && <div className="message-error mb-6">{error}</div>}

      {loading && <LoadingSpinner />}

      {!loading && (
        <>
          {/* Stats */}
          <div className={`mb-8 grid gap-4 ${isAdmin ? 'sm:grid-cols-4' : 'sm:grid-cols-3'}`}>
            <div className="card">
              <p className="text-sm font-medium text-text-muted">Total reservas</p>
              <p className="mt-1 text-3xl font-bold text-primary-600">{totalReservas}</p>
            </div>
            <div className="card">
              <p className="text-sm font-medium text-text-muted">Pendientes</p>
              <p className="mt-1 text-3xl font-bold text-warning">{totalPendientes}</p>
            </div>
            <div className="card">
              <p className="text-sm font-medium text-text-muted">Recursos activos</p>
              <p className="mt-1 text-3xl font-bold text-success">{summary?.recursos_activos ?? 0}</p>
            </div>
            {isAdmin && (
              <div className="card">
                <p className="text-sm font-medium text-text-muted">Usuarios</p>
                <p className="mt-1 text-3xl font-bold text-info">{summary?.usuarios ?? 0}</p>
              </div>
            )}
          </div>

          {summary && <AdminDashboardCharts summary={summary} showSpaces={isAdmin} />}

          {isAdmin && (
            <div className="mb-8">
              <Link href="/admin/control-cambios" className="btn btn-secondary">
                Ver control de cambios
              </Link>
            </div>
          )}

          {/* Quick actions */}
          {!isAdmin && (
            <div className="mb-8 flex flex-wrap gap-3">
              <Link href="/espacios" className="btn btn-primary">
                Hacer una reserva
              </Link>
              <Link href="/admin/reservas" className="btn btn-primary">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15a2.25 2.25 0 012.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
                </svg>
                Gestionar reservas
              </Link>
              <Link href="/reservas/mis-reservas" className="btn btn-secondary">
                Mis reservas
              </Link>
              <Link href="/admin/recursos" className="btn btn-secondary">
                Gestionar recursos
              </Link>
              <Link href="/admin/configuracion" className="btn btn-secondary">
                Configurar atención
              </Link>
            </div>
          )}

          {/* Pending reservations */}
          <div className="card p-0 overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-border">
              <h2 className="font-semibold text-text-primary">
                Reservas pendientes
                {pendientes.length > 0 && (
                  <span className="ml-2 badge badge-warning">{pendientes.length}</span>
                )}
              </h2>
              <Link href="/admin/reservas" className="text-sm font-medium text-primary-600 hover:text-primary-700">
                Ver todas
              </Link>
            </div>

            {pendientes.length === 0 ? (
              <div className="py-12 text-center">
                <p className="text-text-muted">No hay reservas pendientes de revisión.</p>
              </div>
            ) : (
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
                    {pendientes.slice(0, 5).map((reserva) => (
                      <tr key={reserva.id}>
                        <td className="font-medium">{reserva.usuario.username}</td>
                        <td>{reserva.recurso.nombre}</td>
                        <td>{reserva.recurso.espacio.nombre}</td>
                        <td>{reserva.fecha}</td>
                        <td>
                          {reserva.hora_inicio.slice(0, 5)} - {reserva.hora_fin.slice(0, 5)}
                        </td>
                        <td>{reserva.asistentes}</td>
                        <td>
                          <span className={`badge ${badgeEstadoReserva(reserva.estado)}`}>
                            {labelEstadoReserva(reserva.estado)}
                          </span>
                        </td>
                        <td>
                          <div className="flex gap-2">
                            {isAdmin && (
                              <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => setSelectedReserva(reserva)}
                                type="button"
                              >
                                Ver
                              </button>
                            )}
                            <button
                              className="btn btn-success btn-sm"
                              onClick={() => handleAprobar(reserva.id)}
                              type="button"
                            >
                              Aprobar
                            </button>
                            <button
                              className="btn btn-danger btn-sm"
                              onClick={() => handleRechazar(reserva.id)}
                              type="button"
                            >
                              Rechazar
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {selectedReserva && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="reserva-detail-title"
          onClick={() => setSelectedReserva(null)}
        >
          <div className="card w-full max-w-lg" onClick={(event) => event.stopPropagation()}>
            <div className="mb-4 flex items-center justify-between">
              <h2 id="reserva-detail-title" className="text-lg font-semibold">
                Reserva #{selectedReserva.id}
              </h2>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setSelectedReserva(null)}
                type="button"
              >
                Cerrar
              </button>
            </div>
            <dl className="grid gap-3 text-sm sm:grid-cols-2">
              <div><dt className="text-text-muted">Usuario</dt><dd className="font-medium">{selectedReserva.usuario.username}</dd></div>
              <div><dt className="text-text-muted">Recurso</dt><dd className="font-medium">{selectedReserva.recurso.nombre}</dd></div>
              <div><dt className="text-text-muted">Espacio</dt><dd className="font-medium">{selectedReserva.recurso.espacio.nombre}</dd></div>
              <div><dt className="text-text-muted">Fecha</dt><dd className="font-medium">{selectedReserva.fecha}</dd></div>
              <div><dt className="text-text-muted">Horario</dt><dd className="font-medium">{selectedReserva.hora_inicio.slice(0, 5)} - {selectedReserva.hora_fin.slice(0, 5)}</dd></div>
              <div><dt className="text-text-muted">Asistentes</dt><dd className="font-medium">{selectedReserva.asistentes}</dd></div>
              <div><dt className="text-text-muted">Estado</dt><dd><span className={`badge ${badgeEstadoReserva(selectedReserva.estado)}`}>{labelEstadoReserva(selectedReserva.estado)}</span></dd></div>
            </dl>
          </div>
        </div>
      )}
    </div>
    </ProtectedRoute>
  );
}
