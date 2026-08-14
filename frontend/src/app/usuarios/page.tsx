'use client';

import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import {
  crearUsuario,
  listarUsuarios,
  actualizarUsuario,
  eliminarUsuario,
  type AdminUsuarioCreate,
  type AdminUsuarioUpdate,
} from '@/services/usuarios';
import type { AuthUser } from '@/types/auth';
import type { Espacio } from '@/types/espacio';
import { listarEspacios } from '@/services/espacios';
import LoadingSpinner from '@/components/LoadingSpinner';
import ProtectedRoute from '@/components/ProtectedRoute';

const initialForm: AdminUsuarioCreate = {
  username: '',
  email: '',
  password: '',
  rol: 'usuario',
};

interface EditingState {
  id: number;
  username: string;
  email: string;
  password?: string;
  rol: 'admin' | 'gestor' | 'usuario';
  espacio_id?: number;
}

export default function UsuariosPage() {
  const { isAuthenticated, user } = useAuth();
  const [usuarios, setUsuarios] = useState<AuthUser[]>([]);
  const [espacios, setEspacios] = useState<Espacio[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState<AdminUsuarioCreate>(initialForm);
  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState<EditingState | null>(null);

  const loadUsuarios = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [usuariosData, espaciosData] = await Promise.all([listarUsuarios(), listarEspacios()]);
      setUsuarios(usuariosData);
      setEspacios(espaciosData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron cargar los usuarios');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) void loadUsuarios();
  }, [isAuthenticated, loadUsuarios]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!form.username.trim() || !form.email.trim() || !form.password?.trim()) return;
    if (form.rol === 'gestor' && !form.espacio_id) {
      setError('Debes asignar un espacio al gestor');
      return;
    }
    setCreating(true);
    setError(null);
    try {
      await crearUsuario(form);
      setForm(initialForm);
      await loadUsuarios();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo crear el usuario');
    } finally {
      setCreating(false);
    }
  }

  async function handleUpdate(id: number) {
    if (!editing || editing.id !== id) return;
    setError(null);
    try {
      const data: AdminUsuarioUpdate = {};
      if (editing.username.trim()) data.username = editing.username.trim();
      if (editing.email.trim()) data.email = editing.email.trim();
      if (editing.password?.trim()) data.password = editing.password.trim();
      data.rol = editing.rol;
      if (editing.rol === 'gestor') data.espacio_id = editing.espacio_id;
      await actualizarUsuario(id, data);
      setEditing(null);
      await loadUsuarios();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo actualizar el usuario');
    }
  }

  async function handleDelete(id: number) {
    if (!window.confirm('¿Seguro que deseas eliminar este usuario?')) return;
    setError(null);
    try {
      await eliminarUsuario(id);
      await loadUsuarios();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo eliminar el usuario');
    }
  }

  function startEdit(usuario: AuthUser) {
    setEditing({
      id: usuario.id,
      username: usuario.username,
      email: usuario.email,
      rol: usuario.rol,
      password: '',
      espacio_id: usuario.espacio?.id,
    });
  }

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <ProtectedRoute adminOnly>
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-text-primary sm:text-3xl">Administrar usuarios</h1>
        <p className="mt-1 text-text-secondary">Creá y gestioná los usuarios del sistema</p>
      </div>

      {error && <div className="message-error mb-6">{error}</div>}

      {/* Create form */}
      <div className="card mb-6">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-muted">Nuevo usuario</h2>
        <form onSubmit={handleCreate} className="flex flex-wrap items-end gap-3">
          <label className="input-label flex-1 min-w-[140px]">
            Usuario
            <input
              className="input"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              placeholder="Ej. juanperez"
              required
              minLength={3}
              maxLength={80}
            />
          </label>
          <label className="input-label flex-1 min-w-[180px]">
            Email
            <input
              className="input"
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="juan@correo.itm.edu.co"
              required
            />
          </label>
          <label className="input-label flex-1 min-w-[140px]">
            Contraseña
            <input
              className="input"
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="Min. 6 caracteres"
              required
              minLength={6}
            />
          </label>
          <label className="input-label w-28">
            Rol
            <select
              className="input"
              value={form.rol}
              onChange={(e) => setForm({ ...form, rol: e.target.value as AdminUsuarioCreate['rol'] })}
            >
              <option value="usuario">Usuario de reservas</option>
              <option value="gestor">Gestor de recursos</option>
              <option value="admin">Administrador total</option>
            </select>
          </label>
          {form.rol === 'gestor' && (
            <label className="input-label min-w-[180px]">
              Espacio asignado
              <select className="input" value={form.espacio_id ?? ''} onChange={(e) => setForm({ ...form, espacio_id: Number(e.target.value) })} required>
                <option value="" disabled>Selecciona un espacio</option>
                {espacios.map((espacio) => <option key={espacio.id} value={espacio.id}>{espacio.nombre}</option>)}
              </select>
            </label>
          )}
          <button className="btn btn-primary" type="submit" disabled={creating}>
            {creating ? 'Creando...' : 'Crear usuario'}
          </button>
        </form>
      </div>

      {/* Table */}
      {loading && <LoadingSpinner />}

      {!loading && usuarios.length === 0 && (
        <div className="card py-12 text-center">
          <p className="text-text-muted">No hay usuarios registrados.</p>
        </div>
      )}

      {!loading && usuarios.length > 0 && (
        <div className="card p-0 overflow-hidden">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Usuario</th>
                  <th>Email</th>
                  <th>Rol</th>
                  <th>Espacio asignado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {usuarios.map((usuario) => (
                  <tr key={usuario.id}>
                    {editing?.id === usuario.id ? (
                      <>
                        <td className="text-text-muted">{usuario.id}</td>
                        <td>
                          <input
                            className="input"
                            aria-label="Nombre de usuario"
                            value={editing.username}
                            onChange={(e) => setEditing({ ...editing, username: e.target.value })}
                            minLength={3}
                            maxLength={80}
                            required
                          />
                        </td>
                        <td>
                          <input
                            className="input"
                            type="email"
                            aria-label="Email"
                            value={editing.email}
                            onChange={(e) => setEditing({ ...editing, email: e.target.value })}
                            required
                          />
                        </td>
                        <td>
                          <select
                            className="input"
                            aria-label="Rol del usuario"
                            value={editing.rol}
                            onChange={(e) => setEditing({ ...editing, rol: e.target.value as EditingState['rol'] })}
                          >
                            <option value="usuario">Usuario de reservas</option>
                            <option value="gestor">Gestor de recursos</option>
                            <option value="admin">Administrador total</option>
                          </select>
                        </td>
                        <td>
                          {editing.rol === 'gestor' ? (
                            <select className="input" aria-label="Espacio asignado al gestor" value={editing.espacio_id ?? ''} onChange={(e) => setEditing({ ...editing, espacio_id: Number(e.target.value) })} required>
                              <option value="" disabled>Selecciona un espacio</option>
                              {espacios.map((espacio) => <option key={espacio.id} value={espacio.id}>{espacio.nombre}</option>)}
                            </select>
                          ) : 'No aplica'}
                        </td>
                        <td>
                          <div className="flex flex-col gap-2">
                            <input
                              className="input"
                              type="password"
                              aria-label="Nueva clave (opcional)"
                              value={editing.password}
                              onChange={(e) => setEditing({ ...editing, password: e.target.value })}
                              placeholder="Nueva clave (opcional)"
                              minLength={6}
                            />
                            <div className="flex gap-2">
                              <button className="btn btn-success btn-sm" onClick={() => handleUpdate(usuario.id)} type="button">
                                Guardar
                              </button>
                              <button className="btn btn-secondary btn-sm" onClick={() => setEditing(null)} type="button">
                                Cancelar
                              </button>
                            </div>
                          </div>
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="text-text-muted">{usuario.id}</td>
                        <td className="font-medium">{usuario.username}</td>
                        <td>{usuario.email}</td>
                        <td>
                          <span className={`badge ${usuario.rol === 'admin' ? 'badge-info' : 'badge-neutral'}`}>
                            {usuario.rol}
                          </span>
                        </td>
                        <td>{usuario.espacio?.nombre ?? 'No asignado'}</td>
                        <td>
                          <div className="flex gap-2">
                            <button className="btn btn-secondary btn-sm" onClick={() => startEdit(usuario)} type="button">
                              Editar
                            </button>
                            {user?.id !== usuario.id && (
                              <button className="btn btn-danger btn-sm" onClick={() => handleDelete(usuario.id)} type="button">
                                Eliminar
                              </button>
                            )}
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
