'use client';

import { useEffect, useState } from 'react';
import LoadingSpinner from '@/components/LoadingSpinner';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/context/AuthContext';
import { listarControlCambios } from '@/services/control-cambios';
import type { ControlCambio } from '@/types/control-cambio';

const accionBadge: Record<string, string> = {
  crear: 'badge-success',
  actualizar: 'badge-info',
  configurar: 'badge-info',
  'cambiar estado': 'badge-warning',
  eliminar: 'badge-danger',
};

export default function ControlCambiosPage() {
  const { isAuthenticated } = useAuth();
  const [cambios, setCambios] = useState<ControlCambio[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) return;
    listarControlCambios()
      .then(setCambios)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [isAuthenticated]);

  if (loading) return <LoadingSpinner />;

  return (
    <ProtectedRoute adminOnly redirectForbidden="/admin">
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-text-primary sm:text-3xl">Control de cambios</h1>
        <p className="mt-1 text-text-secondary">
          Historial de operaciones realizadas desde la habilitación de esta sección.
        </p>
      </div>

      {error && <div className="message-error mb-6">{error}</div>}

      {cambios.length === 0 ? (
        <div className="card py-12 text-center text-text-muted">Todavía no hay cambios registrados.</div>
      ) : (
        <div className="card overflow-hidden p-0">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Usuario</th>
                  <th>Acción</th>
                  <th>Entidad</th>
                  <th>Descripción</th>
                </tr>
              </thead>
              <tbody>
                {cambios.map((cambio) => (
                  <tr key={cambio.id}>
                    <td className="whitespace-nowrap">
                      {new Date(cambio.created_at).toLocaleString('es')}
                    </td>
                    <td className="font-medium">{cambio.usuario}</td>
                    <td>
                      <span className={`badge ${accionBadge[cambio.accion] ?? 'badge-neutral'}`}>
                        {cambio.accion}
                      </span>
                    </td>
                    <td>
                      {cambio.entidad}
                      {cambio.entidad_id ? ` #${cambio.entidad_id}` : ''}
                    </td>
                    <td>{cambio.descripcion}</td>
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
