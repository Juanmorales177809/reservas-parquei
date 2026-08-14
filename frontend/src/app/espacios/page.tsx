'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { listarEspacios } from '@/services/espacios';
import { getDisponibilidadRecurso, listarRecursos } from '@/services/recursos';
import { crearReserva } from '@/services/reservas';
import type { DisponibilidadSlot, Espacio } from '@/types/espacio';
import type { Recurso } from '@/types/recurso';
import { getLocalDateInputValue } from '@/utils/date';

interface EspacioConRecursos {
  espacio: Espacio;
  recursos: Recurso[];
}

type PasoReserva = 'editar' | 'resumen' | 'exito';

export default function EspaciosPage() {
  const { isAuthenticated } = useAuth();
  const [espacios, setEspacios] = useState<EspacioConRecursos[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [seleccionado, setSeleccionado] = useState<EspacioConRecursos | null>(null);
  const [recursoId, setRecursoId] = useState(0);
  const [fecha, setFecha] = useState(() => getLocalDateInputValue());
  const [slots, setSlots] = useState<DisponibilidadSlot[]>([]);
  const [horasSeleccionadas, setHorasSeleccionadas] = useState<number[]>([]);
  const [asistentes, setAsistentes] = useState(1);
  const [paso, setPaso] = useState<PasoReserva>('editar');
  const [aceptaTerminos, setAceptaTerminos] = useState(false);
  const [guardandoReserva, setGuardandoReserva] = useState(false);
  const [reservaCreadaId, setReservaCreadaId] = useState<number | null>(null);
  const [reservaCreadaEstado, setReservaCreadaEstado] = useState<string | null>(null);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const botonCerrarRef = useRef<HTMLButtonElement>(null);
  const focoPrevioRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    Promise.all([listarEspacios(), listarRecursos(true)])
      .then(([espaciosData, recursosData]) => {
        setEspacios(
          espaciosData
            .filter((espacio) => espacio.estado === 'activo')
            .map((espacio) => ({
              espacio,
              recursos: recursosData.filter((recurso) => recurso.espacio_id === espacio.id),
            })),
        );
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function consultarDisponibilidad(id: number, nuevaFecha: string) {
    setRecursoId(id);
    setFecha(nuevaFecha);
    setHorasSeleccionadas([]);
    setPaso('editar');
    setAceptaTerminos(false);
    setLoadingSlots(true);
    setError(null);
    try {
      setSlots(await getDisponibilidadRecurso(id, nuevaFecha));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo cargar la disponibilidad');
      setSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  }

  function cerrarModal() {
    setSeleccionado(null);
    focoPrevioRef.current?.focus();
  }

  useEffect(() => {
    if (!seleccionado) return;
    botonCerrarRef.current?.focus();
    function alPresionarTecla(event: KeyboardEvent) {
      if (event.key === 'Escape') cerrarModal();
    }
    window.addEventListener('keydown', alPresionarTecla);
    return () => window.removeEventListener('keydown', alPresionarTecla);
  }, [seleccionado]);

  function abrirDisponibilidad(item: EspacioConRecursos) {
    focoPrevioRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    setSeleccionado(item);
    setSlots([]);
    setHorasSeleccionadas([]);
    setAsistentes(1);
    setPaso('editar');
    setAceptaTerminos(false);
    setReservaCreadaId(null);
    setReservaCreadaEstado(null);
    const primerRecurso = item.recursos[0];
    if (primerRecurso) {
      void consultarDisponibilidad(primerRecurso.id, fecha);
    } else {
      setRecursoId(0);
    }
  }

  const recursoSeleccionado = seleccionado?.recursos.find((recurso) => recurso.id === recursoId);
  const indicesOrdenados = [...horasSeleccionadas].sort((a, b) => a - b);
  const primerSlot = indicesOrdenados.length > 0 ? slots[indicesOrdenados[0]] : null;
  const ultimoSlot = indicesOrdenados.length > 0 ? slots[indicesOrdenados[indicesOrdenados.length - 1]] : null;

  function seleccionarHora(index: number) {
    if (slots[index]?.estado !== 'libre') return;
    setHorasSeleccionadas((actuales) => {
      if (actuales.length === 0) return [index];
      const ordenados = [...actuales].sort((a, b) => a - b);
      const primero = ordenados[0];
      const ultimo = ordenados[ordenados.length - 1];

      if (actuales.includes(index)) {
        if (actuales.length === 1) return [];
        if (index === primero || index === ultimo) return actuales.filter((item) => item !== index);
        return [index];
      }
      const esAnteriorConsecutiva =
        index === primero - 1 && slots[index]?.hora_fin === slots[primero]?.hora_inicio;
      const esSiguienteConsecutiva =
        index === ultimo + 1 && slots[ultimo]?.hora_fin === slots[index]?.hora_inicio;
      if (esAnteriorConsecutiva || esSiguienteConsecutiva) return [...actuales, index];
      return [index];
    });
  }

  async function confirmarReserva() {
    if (!recursoSeleccionado || !primerSlot || !ultimoSlot || !aceptaTerminos) return;
    setGuardandoReserva(true);
    setError(null);
    try {
      const reserva = await crearReserva({
        recurso_id: recursoSeleccionado.id,
        fecha,
        hora_inicio: primerSlot.hora_inicio,
        hora_fin: ultimoSlot.hora_fin,
        asistentes,
      });
      setReservaCreadaId(reserva.id);
      setReservaCreadaEstado(reserva.estado);
      setPaso('exito');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo crear la reserva');
      setPaso('editar');
    } finally {
      setGuardandoReserva(false);
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-text-primary sm:text-3xl">Espacios</h1>
        <p className="mt-1 text-text-secondary">
          Elegí un espacio para consultar la disponibilidad de sus recursos.
        </p>
      </div>

      {error && <div className="message-error mb-6">{error}</div>}
      {loading && <p className="py-12 text-center text-text-muted">Cargando espacios...</p>}
      {!loading && espacios.length === 0 && (
        <div className="card py-12 text-center text-text-muted">No hay espacios activos.</div>
      )}

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {espacios.map((item) => (
          <article key={item.espacio.id} className="card flex flex-col">
            <div className="flex items-start justify-between gap-3">
              <h2 className="text-lg font-semibold">{item.espacio.nombre}</h2>
              <span className="badge badge-success">Activo</span>
            </div>
            <dl className="mt-4 grid gap-2 text-sm">
              <div>
                <dt className="inline text-text-muted">Ubicación: </dt>
                <dd className="inline">{item.espacio.ubicacion}</dd>
              </div>
              <div>
                <dt className="inline text-text-muted">Capacidad: </dt>
                <dd className="inline">{item.espacio.capacidad} personas</dd>
              </div>
              <div>
                <dt className="inline text-text-muted">Recursos activos: </dt>
                <dd className="inline font-medium">{item.recursos.length}</dd>
              </div>
            </dl>
            <button
              className="btn btn-primary btn-sm mt-5 w-full justify-center"
              type="button"
              onClick={() => abrirDisponibilidad(item)}
            >
              Disponibilidad
            </button>
          </article>
        ))}
      </div>

      {seleccionado && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4"
          onClick={cerrarModal}
        >
          <div
            className="card max-h-[85vh] w-full max-w-lg overflow-y-auto"
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-disponibilidad-titulo"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 id="modal-disponibilidad-titulo" className="text-lg font-semibold">{seleccionado.espacio.nombre}</h2>
                <p className="text-sm text-text-muted">{seleccionado.espacio.ubicacion}</p>
              </div>
              <button
                ref={botonCerrarRef}
                className="btn btn-secondary btn-sm"
                type="button"
                onClick={cerrarModal}
              >
                Cerrar
              </button>
            </div>

            {paso === 'exito' ? (
              <div className="py-8 text-center">
                <div className="message-success">
                  Reserva #{reservaCreadaId} creada correctamente
                  {reservaCreadaEstado === 'aprobada'
                    ? ' y aprobada automáticamente.'
                    : ' y pendiente de aprobación.'}
                </div>
                <button className="btn btn-primary mt-5" type="button" onClick={cerrarModal}>
                  Finalizar
                </button>
              </div>
            ) : seleccionado.recursos.length === 0 ? (
              <p className="py-10 text-center text-text-muted">
                Este espacio no tiene recursos activos disponibles.
              </p>
            ) : paso === 'editar' ? (
              <>
                <label className="input-label mt-4">
                  Recurso
                  <select
                    className="input"
                    value={recursoId}
                    onChange={(event) => void consultarDisponibilidad(Number(event.target.value), fecha)}
                  >
                    {seleccionado.recursos.map((recurso) => (
                      <option key={recurso.id} value={recurso.id}>
                        {recurso.nombre} · {recurso.tipo.nombre} · Cap. {recurso.capacidad}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="input-label mt-4">
                  Fecha
                  <input
                    className="input"
                    type="date"
                    min={getLocalDateInputValue()}
                    value={fecha}
                    onChange={(event) => void consultarDisponibilidad(recursoId, event.target.value)}
                  />
                </label>

                {loadingSlots ? (
                  <p className="py-8 text-center text-text-muted">Cargando disponibilidad...</p>
                ) : (
                  <>
                    <p className="mt-4 text-sm text-text-muted">
                      Elegí una o varias horas libres consecutivas.
                    </p>
                    <div className="mt-2 grid grid-cols-2 gap-2">
                      {slots.map((slot, index) => {
                        const estaSeleccionado = horasSeleccionadas.includes(index);
                        const estaLibre = slot.estado === 'libre';
                        return (
                          <button
                            key={slot.hora_inicio}
                            type="button"
                            disabled={!estaLibre}
                            onClick={() => seleccionarHora(index)}
                            className={`rounded border px-3 py-2 text-sm font-medium transition-colors ${
                              estaSeleccionado
                                ? 'border-primary-600 bg-primary-600 text-white'
                                : estaLibre
                                  ? 'border-green-200 bg-green-50 text-green-800 hover:border-green-400'
                                  : slot.estado === 'mantenimiento'
                                    ? 'cursor-not-allowed border-yellow-200 bg-yellow-50 text-yellow-800'
                                    : 'cursor-not-allowed border-red-200 bg-red-50 text-red-800'
                            }`}
                          >
                            {slot.hora_inicio.slice(0, 5)} - {slot.hora_fin.slice(0, 5)} · {estaSeleccionado ? 'seleccionado' : slot.estado}
                          </button>
                        );
                      })}
                    </div>
                  </>
                )}

                {isAuthenticated && recursoSeleccionado && primerSlot && ultimoSlot && (
                  <>
                    <label className="input-label mt-4">
                      Asistentes
                      <input
                        className="input"
                        type="number"
                        min={1}
                        max={recursoSeleccionado.capacidad}
                        value={asistentes}
                        onChange={(event) => setAsistentes(Number(event.target.value))}
                      />
                    </label>
                    <button
                      className="btn btn-primary mt-4 w-full justify-center"
                      type="button"
                      onClick={() => {
                        setAceptaTerminos(false);
                        setPaso('resumen');
                      }}
                    >
                      Reservar recurso
                    </button>
                  </>
                )}
                {!isAuthenticated && (
                  <Link className="btn btn-primary mt-4 w-full justify-center" href="/login">
                    Iniciá sesión para reservar
                  </Link>
                )}
              </>
            ) : (
              <div className="mt-5">
                <h3 className="text-lg font-semibold">Resumen de la reserva</h3>
                <dl className="mt-4 grid gap-3 rounded-lg border border-border bg-surface-hover p-4 text-sm">
                  <div><dt className="text-text-muted">Espacio</dt><dd className="font-medium">{seleccionado.espacio.nombre}</dd></div>
                  <div><dt className="text-text-muted">Recurso</dt><dd className="font-medium">{recursoSeleccionado?.nombre}</dd></div>
                  <div><dt className="text-text-muted">Fecha</dt><dd className="font-medium">{fecha}</dd></div>
                  <div><dt className="text-text-muted">Horario</dt><dd className="font-medium">{primerSlot?.hora_inicio.slice(0, 5)} - {ultimoSlot?.hora_fin.slice(0, 5)}</dd></div>
                  <div><dt className="text-text-muted">Asistentes</dt><dd className="font-medium">{asistentes}</dd></div>
                </dl>
                <label className="mt-4 flex items-start gap-3 text-sm">
                  <input
                    className="mt-1 h-4 w-4"
                    type="checkbox"
                    checked={aceptaTerminos}
                    onChange={(event) => setAceptaTerminos(event.target.checked)}
                  />
                  <span>
                    Acepto los{' '}
                    <Link className="font-medium text-primary-600 hover:underline" href="/terminos" target="_blank">
                      términos de uso
                    </Link>.
                  </span>
                </label>
                <p className="mt-2 text-xs text-text-muted">
                  Los términos de uso aún no han sido publicados.
                </p>
                <div className="mt-5 flex gap-3">
                  <button className="btn btn-secondary flex-1 justify-center" type="button" onClick={() => setPaso('editar')}>
                    Editar reserva
                  </button>
                  <button
                    className="btn btn-primary flex-1 justify-center"
                    type="button"
                    disabled={!aceptaTerminos || guardandoReserva}
                    onClick={() => void confirmarReserva()}
                  >
                    {guardandoReserva ? 'Reservando...' : 'Aceptar y reservar'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
