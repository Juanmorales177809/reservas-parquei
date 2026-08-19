'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { listarMisReservas } from '@/services/reservas';
import type { Reserva } from '@/types/reserva';
import LoadingSpinner from '@/components/LoadingSpinner';
import ProtectedRoute from '@/components/ProtectedRoute';
import { badgeEstadoReserva, labelEstadoReserva } from '@/utils/estados';
import { etiquetaObjetivoReserva } from '@/utils/reservaEtiqueta';

export default function DashboardPage() {
  const { user, isAuthenticated } = useAuth();
  const [reservas, setReservas] = useState<Reserva[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return;
    setLoading(true);
    listarMisReservas()
      .then(setReservas)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [isAuthenticated]);

  const pendientes = reservas.filter((r) => r.estado === 'esperando');
  const aprobadas = reservas.filter((r) => r.estado === 'aprobada');
  // upcoming: approved reservations with future dates
  const proximas = aprobadas.filter(
    (r) => new Date(`${r.fecha}T${r.hora_inicio}`) > new Date(),
  );

  return (
    <ProtectedRoute>
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-text-primary sm:text-3xl">
          Hola, {user?.username ?? 'Usuario'}
        </h1>
        <p className="mt-1 text-text-secondary">
          Panel de control de tus reservas de recursos
        </p>
      </div>

      {error && <div className="message-error mb-6">{error}</div>}

      {/* Stats cards */}
      <div className="mb-8 grid gap-4 sm:grid-cols-3">
        <div className="card">
          <p className="text-sm font-medium text-text-muted">Reservas pendientes</p>
          <p className="mt-1 text-3xl font-bold text-warning">{pendientes.length}</p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-text-muted">Reservas aprobadas</p>
          <p className="mt-1 text-3xl font-bold text-success">{aprobadas.length}</p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-text-muted">Próximas reservas</p>
          <p className="mt-1 text-3xl font-bold text-primary-600">{proximas.length}</p>
        </div>
      </div>

      {/* Quick actions */}
      <div className="mb-8 flex flex-wrap gap-3">
        <Link href="/espacios" className="btn btn-primary">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          Nueva reserva
        </Link>
        <Link href="/reservas/mis-reservas" className="btn btn-secondary">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15a2.25 2.25 0 012.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
          </svg>
          Mis reservas
        </Link>
      </div>

      {/* Recent reservations */}
      <div className="card p-0 overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <h2 className="font-semibold text-text-primary">Reservas recientes</h2>
          <Link href="/reservas/mis-reservas" className="text-sm font-medium text-primary-600 hover:text-primary-700">
            Ver todas
          </Link>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-6 w-6 animate-spin rounded-full border-4 border-border border-t-primary-600" />
          </div>
        ) : reservas.length === 0 ? (
          <div className="py-12 text-center">
            <p className="text-text-muted">No tenés reservas todavía.</p>
            <Link href="/espacios" className="mt-2 inline-block text-sm font-medium text-primary-600 hover:text-primary-700">
              Reservá tu primer recurso
            </Link>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                    <th>Recurso</th>
                    <th>Espacio</th>
                  <th>Fecha</th>
                  <th>Horario</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {reservas.slice(0, 5).map((reserva) => (
                  <tr key={reserva.id}>
                    <td className="font-medium">{etiquetaObjetivoReserva(reserva)}</td>
                    <td>{reserva.espacio.nombre}</td>
                    <td>{reserva.fecha}</td>
                    <td>
                      {reserva.hora_inicio.slice(0, 5)} - {reserva.hora_fin.slice(0, 5)}
                    </td>
                    <td>
                      <span className={`badge ${badgeEstadoReserva(reserva.estado)}`}>
                        {labelEstadoReserva(reserva.estado)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
    </ProtectedRoute>
  );
}
