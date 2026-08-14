'use client';

import { FormEvent, Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { listarRecursos } from '@/services/recursos';
import { listarEspacios } from '@/services/espacios';
import { crearReserva } from '@/services/reservas';
import type { Espacio } from '@/types/espacio';
import type { Recurso } from '@/types/recurso';
import type { Reserva, ReservaCreate } from '@/types/reserva';
import LoadingSpinner from '@/components/LoadingSpinner';
import ProtectedRoute from '@/components/ProtectedRoute';
import { getLocalDateInputValue } from '@/utils/date';

function NuevaReservaForm() {
  const searchParams = useSearchParams();
  const { isAuthenticated } = useAuth();
  const [espacios, setEspacios] = useState<Espacio[]>([]);
  const [recursos, setRecursos] = useState<Recurso[]>([]);
  const [espacioId, setEspacioId] = useState(0);
  const [form, setForm] = useState<ReservaCreate>({
    recurso_id: Number(searchParams.get('recurso_id')) || 0,
    fecha: searchParams.get('fecha') || '',
    hora_inicio: '',
    hora_fin: '',
    asistentes: 1,
  });
  const [created, setCreated] = useState<Reserva | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const recursoInicial = Number(searchParams.get('recurso_id')) || 0;
    Promise.all([listarEspacios(), recursoInicial ? listarRecursos(true) : Promise.resolve([])])
      .then(([espaciosData, recursosData]) => {
        setEspacios(espaciosData.filter((espacio) => espacio.estado === 'activo'));
        const recursoSeleccionado = recursosData.find((recurso) => recurso.id === recursoInicial);
        if (recursoSeleccionado) {
          setEspacioId(recursoSeleccionado.espacio_id);
          setRecursos(recursosData.filter((recurso) => recurso.espacio_id === recursoSeleccionado.espacio_id));
        }
      })
      .catch((err: Error) => setError(err.message));
  }, [searchParams]);

  async function handleEspacioChange(nuevoEspacioId: number) {
    setEspacioId(nuevoEspacioId);
    setForm((current) => ({ ...current, recurso_id: 0 }));
    setRecursos([]);
    setError(null);
    if (!nuevoEspacioId) return;
    try {
      const data = await listarRecursos(true, nuevoEspacioId);
      setRecursos(data);
      setForm((current) => ({ ...current, recurso_id: data[0]?.id || 0 }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron cargar los recursos');
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setCreated(await crearReserva(form));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo crear la reserva');
    } finally {
      setLoading(false);
    }
  }

  return (
    <ProtectedRoute>
    <div className="mx-auto max-w-lg px-4 py-8 sm:px-6">
      <h1 className="text-2xl font-bold">Nueva reserva de recurso</h1>
      <p className="mt-1 text-sm text-text-secondary">El estado de la solicitud dependerá del espacio seleccionado.</p>
      {error && <div className="message-error mt-4">{error}</div>}
      {created && (
        <div className="message-success mt-4">
          Reserva #{created.id} creada para {created.recurso.nombre}
          {created.estado === 'aprobada' ? ' y aprobada automáticamente.' : ' y pendiente de aprobación.'}
        </div>
      )}
      <form className="card mt-6 flex flex-col gap-4" onSubmit={handleSubmit}>
        <label className="input-label">
          Espacio
          <select className="input" value={espacioId} onChange={(event) => void handleEspacioChange(Number(event.target.value))} required>
            <option value={0} disabled>Seleccioná un espacio</option>
            {espacios.map((espacio) => (
              <option key={espacio.id} value={espacio.id}>
                {espacio.nombre} · {espacio.ubicacion}
              </option>
            ))}
          </select>
        </label>
        <label className="input-label">
          Recurso
          <select className="input" value={form.recurso_id} onChange={(event) => setForm({ ...form, recurso_id: Number(event.target.value) })} disabled={!espacioId} required>
            <option value={0} disabled>
              {espacioId ? 'Seleccioná un recurso' : 'Primero seleccioná un espacio'}
            </option>
            {recursos.map((recurso) => (
              <option key={recurso.id} value={recurso.id}>
                {recurso.nombre} · Cap. {recurso.capacidad}
              </option>
            ))}
          </select>
          {espacioId > 0 && recursos.length === 0 && (
            <span className="mt-1 text-sm font-normal text-text-muted">Este espacio no tiene recursos activos disponibles.</span>
          )}
        </label>
        <label className="input-label">Fecha<input className="input" type="date" min={getLocalDateInputValue()} value={form.fecha} onChange={(event) => setForm({ ...form, fecha: event.target.value })} required /></label>
        <div className="grid grid-cols-2 gap-4">
          <label className="input-label">Hora inicio<input className="input" type="time" value={form.hora_inicio} onChange={(event) => setForm({ ...form, hora_inicio: event.target.value })} required /></label>
          <label className="input-label">Hora fin<input className="input" type="time" value={form.hora_fin} onChange={(event) => setForm({ ...form, hora_fin: event.target.value })} required /></label>
        </div>
        <label className="input-label">Asistentes<input className="input" type="number" min={1} value={form.asistentes} onChange={(event) => setForm({ ...form, asistentes: Number(event.target.value) })} required /></label>
        <button className="btn btn-primary w-full justify-center" disabled={loading || !espacioId || !form.recurso_id} type="submit">
          {loading ? 'Creando...' : 'Solicitar reserva'}
        </button>
      </form>
    </div>
    </ProtectedRoute>
  );
}

export default function NuevaReservaPage() {
  return <Suspense fallback={<LoadingSpinner />}><NuevaReservaForm /></Suspense>;
}
