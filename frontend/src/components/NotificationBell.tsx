'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  listarMisNotificaciones,
  marcarComoLeida,
  marcarTodasComoLeidas,
} from '@/services/notificaciones';
import type { Notificacion } from '@/types/notificacion';
import { useNotifications } from '@/context/NotificationContext';
import { useAuth } from '@/context/AuthContext';

const tipoBadge: Record<Notificacion['tipo'], string> = {
  Pendiente: 'badge-warning',
  Aprobada: 'badge-success',
  Rechazada: 'badge-danger',
  Cancelada: 'badge-neutral',
};

export default function NotificationBell() {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);
  const { canManageResources } = useAuth();
  const { unreadCount, setUnreadCount } = useNotifications();
  const [open, setOpen] = useState(false);
  const [notificaciones, setNotificaciones] = useState<Notificacion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cargarNotificaciones = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listarMisNotificaciones();
      setNotificaciones(data);
      setUnreadCount(data.filter((item) => !item.leida).length);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron cargar las notificaciones');
    } finally {
      setLoading(false);
    }
  }, [setUnreadCount]);

  useEffect(() => {
    function cerrarFuera(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', cerrarFuera);
    return () => document.removeEventListener('mousedown', cerrarFuera);
  }, []);

  async function toggle() {
    const nuevoEstado = !open;
    setOpen(nuevoEstado);
    if (nuevoEstado) await cargarNotificaciones();
  }

  async function abrirNotificacion(notificacion: Notificacion) {
    try {
      if (!notificacion.leida) {
        const actualizada = await marcarComoLeida(notificacion.id);
        setNotificaciones((actuales) =>
          actuales.map((item) => (item.id === actualizada.id ? actualizada : item)),
        );
        setUnreadCount(Math.max(0, unreadCount - 1));
      }
      setOpen(false);
      const ruta = canManageResources && notificacion.tipo === 'Pendiente'
        ? '/admin/reservas'
        : '/reservas/mis-reservas';
      const query = notificacion.reserva_id ? `?reserva_id=${notificacion.reserva_id}` : '';
      router.push(`${ruta}${query}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo marcar como leída');
    }
  }

  async function marcarTodas() {
    try {
      await marcarTodasComoLeidas();
      setNotificaciones((actuales) => actuales.map((item) => ({ ...item, leida: true })));
      setUnreadCount(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron marcar como leídas');
    }
  }

  return (
    <div className="relative" ref={containerRef}>
      <button
        className="relative flex h-9 w-9 items-center justify-center rounded-md text-text-secondary transition-colors hover:bg-surface-hover hover:text-primary-600"
        type="button"
        aria-label={`Notificaciones${unreadCount ? `, ${unreadCount} sin leer` : ''}`}
        aria-expanded={open}
        onClick={() => void toggle()}
      >
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.081 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute -right-1 -top-1 flex min-h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-bold text-white">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 z-50 mt-2 w-[min(24rem,calc(100vw-2rem))] overflow-hidden rounded-lg border border-border bg-surface-card shadow-xl">
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <div>
              <h2 className="font-semibold text-text-primary">Notificaciones</h2>
              <p className="text-xs text-text-muted">{unreadCount} sin leer</p>
            </div>
            <button
              className="text-xs font-medium text-primary-600 hover:underline disabled:text-text-muted"
              type="button"
              disabled={unreadCount === 0}
              onClick={() => void marcarTodas()}
            >
              Marcar todas como leídas
            </button>
          </div>

          {error && <div className="message-error m-3 text-sm">{error}</div>}
          {loading ? (
            <p className="py-8 text-center text-sm text-text-muted">Cargando...</p>
          ) : notificaciones.length === 0 ? (
            <p className="py-8 text-center text-sm text-text-muted">No tienes notificaciones.</p>
          ) : (
            <div className="max-h-96 overflow-y-auto">
              {notificaciones.map((notificacion) => (
                <button
                  key={notificacion.id}
                  className={`block w-full border-b border-border px-4 py-3 text-left transition-colors hover:bg-surface-hover ${
                    notificacion.leida ? 'bg-surface-card' : 'bg-primary-50'
                  }`}
                  type="button"
                  onClick={() => void abrirNotificacion(notificacion)}
                >
                  <div className="flex items-start justify-between gap-3">
                    <span className={`badge ${tipoBadge[notificacion.tipo]}`}>{notificacion.tipo}</span>
                    {!notificacion.leida && <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-primary-600" />}
                  </div>
                  <p className={`mt-2 text-sm ${notificacion.leida ? 'text-text-secondary' : 'font-medium text-text-primary'}`}>
                    {notificacion.mensaje}
                  </p>
                  <p className="mt-1 text-xs text-text-muted">
                    {new Date(notificacion.created_at).toLocaleString('es')}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
