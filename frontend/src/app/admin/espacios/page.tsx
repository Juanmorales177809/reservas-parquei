'use client';

import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { actualizarEspacio, crearEspacio, eliminarEspacio, listarEspacios } from '@/services/espacios';
import type { Espacio, EspacioCreate, EspacioUpdate } from '@/types/espacio';
import LoadingSpinner from '@/components/LoadingSpinner';
import ProtectedRoute from '@/components/ProtectedRoute';
import { badgeEstadoEntidad } from '@/utils/estados';

interface EditingState {
  id: number;
  nombre: string;
  ubicacion: string;
  capacidad: number | null;
}

const estadoSiguiente: Record<string, 'activo' | 'inactivo' | 'mantenimiento'> = {
  activo: 'inactivo',
  inactivo: 'mantenimiento',
  mantenimiento: 'activo',
};

const etiquetaEstadoSiguiente: Record<string, string> = {
  activo: 'Desactivar',
  inactivo: 'Mantenimiento',
  mantenimiento: 'Activar',
};

export default function AdminEspaciosPage() {
  const { isAuthenticated } = useAuth();
  const [espacios, setEspacios] = useState<Espacio[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // New-space form
  const [nuevoNombre, setNuevoNombre] = useState('');
  const [nuevaUbicacion, setNuevaUbicacion] = useState('');
  const [nuevaCapacidad, setNuevaCapacidad] = useState('');
  const [nuevoCorreo, setNuevoCorreo] = useState('');
  const [creating, setCreating] = useState(false);

  const [editing, setEditing] = useState<EditingState | null>(null);

  const loadEspacios = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setEspacios(await listarEspacios());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron cargar los espacios');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) void loadEspacios();
  }, [isAuthenticated, loadEspacios]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!nuevoNombre.trim() || !nuevaUbicacion.trim() || !nuevoCorreo.trim()) return;
    setCreating(true);
    setError(null);
    try {
      await crearEspacio({
        nombre: nuevoNombre.trim(),
        ubicacion: nuevaUbicacion.trim(),
        ...(nuevaCapacidad ? { capacidad: Number(nuevaCapacidad) } : {}),
        correo: nuevoCorreo.trim(),
      } satisfies EspacioCreate);
      setNuevoNombre('');
      setNuevaUbicacion('');
      setNuevaCapacidad('');
      setNuevoCorreo('');
      await loadEspacios();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo crear el espacio');
    } finally {
      setCreating(false);
    }
  }

  async function handleUpdate(id: number) {
    if (!editing || editing.id !== id) return;
    setError(null);
    try {
      const data: EspacioUpdate = {};
      if (editing.nombre.trim()) data.nombre = editing.nombre.trim();
      if (editing.ubicacion.trim()) data.ubicacion = editing.ubicacion.trim();
      if (editing.capacidad !== null && editing.capacidad > 0) data.capacidad = editing.capacidad;
      await actualizarEspacio(id, data);
      setEditing(null);
      await loadEspacios();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo actualizar el espacio');
    }
  }

  async function handleToggleEstado(espacio: Espacio) {
    setError(null);
    try {
      await actualizarEspacio(espacio.id, { estado: estadoSiguiente[espacio.estado] ?? 'activo' } satisfies EspacioUpdate);
      await loadEspacios();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo cambiar el estado');
    }
  }

  function startEdit(espacio: Espacio) {
    setEditing({ id: espacio.id, nombre: espacio.nombre, ubicacion: espacio.ubicacion, capacidad: espacio.capacidad });
  }

  function cancelEdit() {
    setEditing(null);
  }

  async function handleDelete(espacio: Espacio) {
    if (!window.confirm(`¿Eliminar el espacio "${espacio.nombre}" y sus reservas?`)) return;
    setError(null);
    try {
      await eliminarEspacio(espacio.id);
      await loadEspacios();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo eliminar el espacio');
    }
  }

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <ProtectedRoute adminOnly>
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-text-primary sm:text-3xl">Administrar espacios</h1>
        <p className="mt-1 text-text-secondary">Creá y gestioná los espacios institucionales</p>
      </div>

      {error && <div className="message-error mb-6">{error}</div>}

      {/* Create form */}
      <div className="card mb-6">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-muted">Nuevo espacio</h2>
        <form onSubmit={handleCreate} className="flex flex-wrap items-end gap-3">
          <label className="input-label flex-1 min-w-[160px]">
            Nombre
            <input
              className="input"
              value={nuevoNombre}
              onChange={(e) => setNuevoNombre(e.target.value)}
              placeholder="Ej. Aula 101"
              required
              minLength={3}
              maxLength={120}
            />
          </label>
          <label className="input-label flex-1 min-w-[140px]">
            Ubicación
            <input
              className="input"
              value={nuevaUbicacion}
              onChange={(e) => setNuevaUbicacion(e.target.value)}
              placeholder="Sede Central"
              required
              maxLength={200}
            />
          </label>
          <label className="input-label w-28">
            Capacidad
            <input
              className="input"
              type="number"
              value={nuevaCapacidad}
              onChange={(e) => setNuevaCapacidad(e.target.value)}
              placeholder="Ej. 30 (opcional)"
              min={1}
            />
          </label>
          <label className="input-label flex-1 min-w-[200px]">
            Correo
            <input
              className="input"
              type="email"
              value={nuevoCorreo}
              onChange={(e) => setNuevoCorreo(e.target.value)}
              placeholder="espacio@example.com"
              required
              maxLength={255}
            />
          </label>
          <button className="btn btn-primary" type="submit" disabled={creating}>
            {creating ? 'Creando...' : 'Crear espacio'}
          </button>
        </form>
      </div>

      {/* Table */}
      {loading && <LoadingSpinner />}

      {!loading && espacios.length === 0 && (
        <div className="card py-12 text-center">
          <p className="text-text-muted">No hay espacios registrados.</p>
        </div>
      )}

      {!loading && espacios.length > 0 && (
        <div className="card p-0 overflow-hidden">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Ubicación</th>
                  <th>Capacidad</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {espacios.map((espacio) => (
                  <tr key={espacio.id}>
                    {editing?.id === espacio.id ? (
                      <>
                        <td>
                          <input
                            className="input"
                            value={editing.nombre}
                            onChange={(e) => setEditing({ ...editing, nombre: e.target.value })}
                            minLength={1}
                            maxLength={120}
                          />
                        </td>
                        <td>
                          <input
                            className="input"
                            aria-label="Ubicación del espacio"
                            value={editing.ubicacion}
                            onChange={(e) => setEditing({ ...editing, ubicacion: e.target.value })}
                            maxLength={200}
                          />
                        </td>
                        <td>
                          <input
                            className="input w-20"
                            type="number"
                            aria-label="Capacidad del espacio"
                            value={editing.capacidad ?? ''}
                            onChange={(e) =>
                              setEditing({
                                ...editing,
                                capacidad: e.target.value === '' ? null : Number(e.target.value),
                              })
                            }
                            min={1}
                          />
                        </td>
                        <td>
                          <span className={`badge ${badgeEstadoEntidad(espacio.estado)}`}>
                            {espacio.estado}
                          </span>
                        </td>
                        <td>
                          <div className="flex gap-2">
                            <button className="btn btn-success btn-sm" onClick={() => handleUpdate(espacio.id)} type="button">
                              Guardar
                            </button>
                            <button className="btn btn-secondary btn-sm" onClick={cancelEdit} type="button">
                              Cancelar
                            </button>
                          </div>
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="font-medium">{espacio.nombre}</td>
                        <td>{espacio.ubicacion}</td>
                        <td>{espacio.capacidad ?? <span className="text-text-muted">Sin definir</span>}</td>
                        <td>
                          <span className={`badge ${badgeEstadoEntidad(espacio.estado)}`}>
                            {espacio.estado}
                          </span>
                        </td>
                        <td>
                          <div className="flex gap-2">
                            <button className="btn btn-secondary btn-sm" onClick={() => startEdit(espacio)} type="button">
                              Editar
                            </button>
                            <button className="btn btn-secondary btn-sm" onClick={() => handleToggleEstado(espacio)} type="button">
                              {etiquetaEstadoSiguiente[espacio.estado] ?? 'Cambiar'}
                            </button>
                            <button className="btn btn-danger btn-sm" onClick={() => handleDelete(espacio)} type="button">
                              Eliminar
                            </button>
                          </div>
                        </td>
                      </>
                    )}
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
