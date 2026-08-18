'use client';

import { FormEvent, Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { listarRecursos } from '@/services/recursos';
import { listarZonas } from '@/services/zonas';
import { listarEspacios } from '@/services/espacios';
import { crearReserva } from '@/services/reservas';
import type { Espacio, ModalidadEspacio } from '@/types/espacio';
import type { Recurso } from '@/types/recurso';
import type { Reserva } from '@/types/reserva';
import type { Zona } from '@/types/zona';
import LoadingSpinner from '@/components/LoadingSpinner';
import ProtectedRoute from '@/components/ProtectedRoute';
import { getLocalDateInputValue } from '@/utils/date';

function NuevaReservaForm() {
  const searchParams = useSearchParams();
  const fechaInicial = searchParams.get('fecha') || '';
  const recursoInicial = Number(searchParams.get('recurso_id')) || 0;
  const { isAuthenticated } = useAuth();
  const [espacios, setEspacios] = useState<Espacio[]>([]);
  const [recursos, setRecursos] = useState<Recurso[]>([]);
  const [zonas, setZonas] = useState<Zona[]>([]);
  const [espacioId, setEspacioId] = useState(0);
  const [modalidad, setModalidad] = useState<ModalidadEspacio | null>(null);
  const [recursoIds, setRecursoIds] = useState<number[]>(recursoInicial ? [recursoInicial] : []);
  const [zonaIds, setZonaIds] = useState<number[]>([]);
  const [form, setForm] = useState({ fecha: fechaInicial, hora_inicio: '', hora_fin: '', asistentes: 1 });
  const [created, setCreated] = useState<Reserva | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([listarEspacios(), recursoInicial ? listarRecursos(true) : Promise.resolve([]), listarZonas()])
      .then(([espaciosData, recursosData, zonasData]) => {
        const activos = espaciosData.filter((espacio) => espacio.estado === 'activo');
        setEspacios(activos);
        if (!recursoInicial) return;
        const recursoSeleccionado = recursosData.find((recurso) => recurso.id === recursoInicial);
        if (recursoSeleccionado) {
          const esp = activos.find((espacio) => espacio.id === recursoSeleccionado.espacio_id);
          setEspacioId(recursoSeleccionado.espacio_id);
          setModalidad(esp?.modalidad_reserva ?? 'equipos');
          setRecursos(recursosData.filter((recurso) => recurso.espacio_id === recursoSeleccionado.espacio_id));
          setZonas(zonasData.filter((zona) => zona.espacio_id === recursoSeleccionado.espacio_id));
          setRecursoIds([recursoInicial]);
        }
      })
      .catch((err: Error) => setError(err.message));
  }, [searchParams, recursoInicial]);

  async function handleEspacioChange(nuevoEspacioId: number) {
    setEspacioId(nuevoEspacioId);
    setRecursoIds([]);
    setZonaIds([]);
    setRecursos([]);
    setZonas([]);
    setModalidad(null);
    setError(null);
    if (!nuevoEspacioId) return;
    const esp = espacios.find((espacio) => espacio.id === nuevoEspacioId);
    const modalidadEspacio = esp?.modalidad_reserva ?? 'equipos';
    setModalidad(modalidadEspacio);
    try {
      const [dataRecursos, dataZonas] = await Promise.all([
        listarRecursos(true, nuevoEspacioId),
        listarZonas(nuevoEspacioId),
      ]);
      setRecursos(dataRecursos);
      setZonas(dataZonas);
      if (modalidadEspacio !== 'zonas' && dataRecursos.length > 0) {
        setRecursoIds([dataRecursos[0].id]);
      } else if (modalidadEspacio !== 'equipos' && dataZonas.length > 0) {
        setZonaIds([dataZonas[0].id]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron cargar los recursos');
    }
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setCreated(
        await crearReserva({
          recurso_ids: recursoIds,
          zona_ids: zonaIds,
          fecha: form.fecha,
          hora_inicio: form.hora_inicio,
          hora_fin: form.hora_fin,
          asistentes: form.asistentes,
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo crear la reserva');
    } finally {
      setLoading(false);
    }
  }

  const hayObjetivo = recursoIds.length > 0 || zonaIds.length > 0;
  const condicionesValidas = Boolean(espacioId) && hayObjetivo && Boolean(form.fecha) && Boolean(form.hora_inicio) && Boolean(form.hora_fin);

  return (
    <ProtectedRoute>
    <div className="mx-auto max-w-lg px-4 py-8 sm:px-6">
      <h1 className="text-2xl font-bold">Nueva reserva de recurso</h1>
      <p className="mt-1 text-sm text-text-secondary">El estado de la solicitud dependerá del espacio seleccionado.</p>
      {error && <div className="message-error mt-4">{error}</div>}
      {created && (
        <div className="message-success mt-4">
          Reserva #{created.id} creada correctamente
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
        {modalidad !== 'zonas' && (
          <fieldset className="input-label">
            <legend>Recursos</legend>
            {recursos.length === 0 ? (
              <span className="mt-1 block text-sm font-normal text-text-muted">Este espacio no tiene recursos activos disponibles.</span>
            ) : (
              <div className="max-h-40 space-y-1 overflow-y-auto rounded border border-border p-2">
                {recursos.map((recurso) => (
                  <label key={recurso.id} className="flex items-center gap-2 text-sm font-normal">
                    <input
                      type="checkbox"
                      className="h-4 w-4"
                      checked={recursoIds.includes(recurso.id)}
                      onChange={() =>
                        setRecursoIds((actuales) =>
                          actuales.includes(recurso.id)
                            ? actuales.filter((item) => item !== recurso.id)
                            : [...actuales, recurso.id],
                        )
                      }
                    />
                    {recurso.nombre} · Cap. {recurso.capacidad}
                  </label>
                ))}
              </div>
            )}
          </fieldset>
        )}
        {modalidad !== 'equipos' && (
          <fieldset className="input-label">
            <legend>Zonas</legend>
            {zonas.length === 0 ? (
              <span className="mt-1 block text-sm font-normal text-text-muted">Este espacio no tiene zonas activas disponibles.</span>
            ) : (
              <>
                <div className="max-h-40 space-y-1 overflow-y-auto rounded border border-border p-2">
                  {zonas.map((zona) => (
                    <label key={zona.id} className="flex items-center gap-2 text-sm font-normal">
                      <input
                        type="checkbox"
                        className="h-4 w-4"
                        checked={zonaIds.includes(zona.id)}
                        onChange={() =>
                          setZonaIds((actuales) =>
                            actuales.includes(zona.id)
                              ? actuales.filter((item) => item !== zona.id)
                              : [...actuales, zona.id],
                          )
                        }
                      />
                      {zona.nombre}
                      {zona.capacidad !== null ? ` · Cap. ${zona.capacidad}` : ''}
                    </label>
                  ))}
                </div>
                {modalidad === 'zonas' && (
                  <p className="mt-1 text-xs font-normal text-text-muted">
                    Podés reservar una zona aunque no tenga recursos asociados.
                  </p>
                )}
              </>
            )}
          </fieldset>
        )}
        <label className="input-label">Fecha<input className="input" type="date" min={getLocalDateInputValue()} value={form.fecha} onChange={(event) => setForm({ ...form, fecha: event.target.value })} required /></label>
        <div className="grid grid-cols-2 gap-4">
          <label className="input-label">Hora inicio<input className="input" type="time" value={form.hora_inicio} onChange={(event) => setForm({ ...form, hora_inicio: event.target.value })} required /></label>
          <label className="input-label">Hora fin<input className="input" type="time" value={form.hora_fin} onChange={(event) => setForm({ ...form, hora_fin: event.target.value })} required /></label>
        </div>
        <label className="input-label">Asistentes<input className="input" type="number" min={1} value={form.asistentes} onChange={(event) => setForm({ ...form, asistentes: Number(event.target.value) })} required /></label>
        <button className="btn btn-primary w-full justify-center" disabled={loading || !condicionesValidas} type="submit">
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