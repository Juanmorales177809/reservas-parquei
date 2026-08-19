'use client';

import { FormEvent, useCallback, useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { listarEspacios } from '@/services/espacios';
import {
  actualizarRecurso,
  crearRecurso,
  eliminarRecurso,
  listarRecursosGestion,
  listarTiposRecursos,
} from '@/services/recursos';
import type { Espacio } from '@/types/espacio';
import type { Recurso, RecursoCreate, TipoRecurso } from '@/types/recurso';
import LoadingSpinner from '@/components/LoadingSpinner';
import ProtectedRoute from '@/components/ProtectedRoute';

const initialForm: RecursoCreate = {
  nombre: '',
  descripcion: '',
  capacidad: 1,
  tipo_recurso_id: 0,
  estado: 'activo',
};

export default function AdminRecursosPage() {
  const { isAuthenticated, isAdmin, user } = useAuth();
  const [recursos, setRecursos] = useState<Recurso[]>([]);
  const [tipos, setTipos] = useState<TipoRecurso[]>([]);
  const [espacios, setEspacios] = useState<Espacio[]>([]);
  const [form, setForm] = useState<RecursoCreate>(initialForm);
  const [editing, setEditing] = useState<Recurso | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [recursosData, tiposData, espaciosData] = await Promise.all([
        listarRecursosGestion(),
        listarTiposRecursos(),
        isAdmin ? listarEspacios() : Promise.resolve([]),
      ]);
      setRecursos(recursosData);
      setTipos(tiposData);
      setEspacios(espaciosData);
      setForm((current) => ({
        ...current,
        tipo_recurso_id: current.tipo_recurso_id || tiposData[0]?.id || 0,
        espacio_id: current.espacio_id || espaciosData[0]?.id,
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron cargar los recursos');
    } finally {
      setLoading(false);
    }
  }, [isAdmin]);

  useEffect(() => {
    if (isAuthenticated) void loadData();
  }, [isAuthenticated, loadData]);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await crearRecurso(form);
      setForm({
        ...initialForm,
        tipo_recurso_id: tipos[0]?.id || 0,
        espacio_id: isAdmin ? espacios[0]?.id : undefined,
      });
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo crear el recurso');
    } finally {
      setSaving(false);
    }
  }

  async function handleUpdate() {
    if (!editing) return;
    setSaving(true);
    setError(null);
    try {
      await actualizarRecurso(editing.id, {
        nombre: editing.nombre,
        descripcion: editing.descripcion || '',
        capacidad: editing.capacidad,
        estado: editing.estado as RecursoCreate['estado'],
        tipo_recurso_id: editing.tipo_recurso_id,
        espacio_id: isAdmin ? editing.espacio_id : undefined,
      });
      setEditing(null);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo actualizar el recurso');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(recurso: Recurso) {
    if (!window.confirm(`¿Eliminar el recurso "${recurso.nombre}"?`)) return;
    try {
      await eliminarRecurso(recurso.id);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo eliminar el recurso');
    }
  }

  if (loading) return <LoadingSpinner />;

  return (
    <ProtectedRoute roles={['admin', 'gestor']} redirectForbidden="/dashboard">
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold sm:text-3xl">Administrar recursos</h1>
        <p className="mt-1 text-text-secondary">
          {isAdmin ? 'Gestioná los recursos de todos los espacios.' : `Gestioná los recursos de ${user?.espacio?.nombre ?? 'tu espacio'}.`}
        </p>
      </div>
      {error && <div className="message-error mb-6">{error}</div>}
      <form className="card mb-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3" onSubmit={handleCreate}>
        <label className="input-label">Nombre<input className="input" value={form.nombre} onChange={(event) => setForm({ ...form, nombre: event.target.value })} required /></label>
        <label className="input-label">Tipo<select className="input" value={form.tipo_recurso_id} onChange={(event) => setForm({ ...form, tipo_recurso_id: Number(event.target.value) })} required>{tipos.map((tipo) => <option key={tipo.id} value={tipo.id}>{tipo.nombre}</option>)}</select></label>
        {isAdmin && <label className="input-label">Espacio<select className="input" value={form.espacio_id} onChange={(event) => setForm({ ...form, espacio_id: Number(event.target.value) })} required>{espacios.map((espacio) => <option key={espacio.id} value={espacio.id}>{espacio.nombre}</option>)}</select></label>}
        <label className="input-label">Capacidad<input className="input" type="number" min={1} value={form.capacidad} onChange={(event) => setForm({ ...form, capacidad: Number(event.target.value) })} required /></label>
        <label className="input-label md:col-span-2">Descripción<input className="input" value={form.descripcion} onChange={(event) => setForm({ ...form, descripcion: event.target.value })} /></label>
        <button className="btn btn-primary w-fit" disabled={saving || tipos.length === 0} type="submit">{saving ? 'Guardando...' : 'Crear recurso'}</button>
      </form>

      {loading ? <LoadingSpinner /> : (
        <div className="card overflow-hidden p-0">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Recurso</th><th>Tipo</th><th>Espacio</th><th>Capacidad</th><th>Estado</th><th>Acciones</th></tr></thead>
              <tbody>
                {recursos.map((recurso) => (
                  <tr key={recurso.id}>
                    <td>{editing?.id === recurso.id ? <input className="input" aria-label="Nombre del recurso" value={editing.nombre} onChange={(event) => setEditing({ ...editing, nombre: event.target.value })} /> : <><strong>{recurso.nombre}</strong><div className="text-xs text-text-muted">{recurso.descripcion}</div></>}</td>
                    <td>{editing?.id === recurso.id ? <select className="input" aria-label="Tipo del recurso" value={editing.tipo_recurso_id} onChange={(event) => setEditing({ ...editing, tipo_recurso_id: Number(event.target.value) })}>{tipos.map((tipo) => <option key={tipo.id} value={tipo.id}>{tipo.nombre}</option>)}</select> : recurso.tipo.nombre}</td>
                    <td>{recurso.espacio.nombre}</td>
                    <td>{editing?.id === recurso.id ? <input className="input w-24" type="number" min={1} aria-label="Capacidad del recurso" value={editing.capacidad} onChange={(event) => setEditing({ ...editing, capacidad: Number(event.target.value) })} /> : recurso.capacidad}</td>
                    <td>{editing?.id === recurso.id ? <select className="input" aria-label="Estado del recurso" value={editing.estado} onChange={(event) => setEditing({ ...editing, estado: event.target.value as Recurso['estado'] })}><option value="activo">Activo</option><option value="inactivo">Inactivo</option><option value="mantenimiento">Mantenimiento</option></select> : <span className={`badge ${recurso.estado === 'activo' ? 'badge-success' : 'badge-warning'}`}>{recurso.estado}</span>}</td>
                    <td>{editing?.id === recurso.id ? <div className="flex gap-2"><button className="btn btn-success btn-sm" type="button" onClick={handleUpdate}>Guardar</button><button className="btn btn-secondary btn-sm" type="button" onClick={() => setEditing(null)}>Cancelar</button></div> : <div className="flex gap-2"><button className="btn btn-secondary btn-sm" type="button" onClick={() => setEditing({ ...recurso })}>Editar</button><button className="btn btn-danger btn-sm" type="button" onClick={() => handleDelete(recurso)}>Eliminar</button></div>}</td>
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
