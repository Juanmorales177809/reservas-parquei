'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { listarEspacios } from '@/services/espacios';
import { listarZonas } from '@/services/zonas';
import { getDisponibilidadRecurso, listarRecursos } from '@/services/recursos';
import { listarEnsayos } from '@/services/ensayos';
import { crearReserva } from '@/services/reservas';
import type { AcompananteInput } from '@/types/reserva';
import type { DisponibilidadSlot, Espacio } from '@/types/espacio';
import type { Ensayo } from '@/types/ensayo';
import type { Recurso } from '@/types/recurso';
import type { TipoReserva } from '@/types/reserva';
import type { Zona } from '@/types/zona';
import { getLocalDateInputValue } from '@/utils/date';

interface EspacioConRecursos {
  espacio: Espacio;
  recursos: Recurso[];
  zonas: Zona[];
}

type PasoReserva = 'editar' | 'resumen' | 'exito';

function slotsDesdeHorario(espacio: Espacio, fecha: string): DisponibilidadSlot[] {
  // Fase 12C-6: no existe un endpoint de disponibilidad por zona; la grilla
  // se construye desde el horario de atención del espacio. La autoridad del
  // solapamiento real de una zona es el backend (409).
  const dia = new Date(`${fecha}T12:00:00`).getDay();
  const horas = espacio.horario_atencion[dia] ?? [];
  return horas.map((hora) => ({
    hora_inicio: `${String(hora).padStart(2, '0')}:00`,
    hora_fin: `${String(hora + 1).padStart(2, '0')}:00`,
    estado: 'libre',
  }));
}

export default function EspaciosPage() {
  const { isAuthenticated } = useAuth();
  const [espacios, setEspacios] = useState<EspacioConRecursos[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [seleccionado, setSeleccionado] = useState<EspacioConRecursos | null>(null);
  const [recursoIds, setRecursoIds] = useState<number[]>([]);
  const [zonaIds, setZonaIds] = useState<number[]>([]);
  const [ensayos, setEnsayos] = useState<Ensayo[]>([]);
  const [ensayoIds, setEnsayoIds] = useState<number[]>([]);
  const [acompanantes, setAcompanantes] = useState<AcompananteInput[]>([]);
  const [fecha, setFecha] = useState(() => getLocalDateInputValue());
  const [slots, setSlots] = useState<DisponibilidadSlot[]>([]);
  const [horasSeleccionadas, setHorasSeleccionadas] = useState<number[]>([]);
  const [asistentes, setAsistentes] = useState(1);
  const [tipo, setTipo] = useState<TipoReserva | ''>('');
  const [paso, setPaso] = useState<PasoReserva>('editar');
  const [aceptaTerminos, setAceptaTerminos] = useState(false);
  const [guardandoReserva, setGuardandoReserva] = useState(false);
  const [reservaCreadaId, setReservaCreadaId] = useState<number | null>(null);
  const [reservaCreadaEstado, setReservaCreadaEstado] = useState<string | null>(null);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const botonCerrarRef = useRef<HTMLButtonElement>(null);
  const focoPrevioRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    Promise.all([listarEspacios(), listarRecursos(true), listarZonas()])
      .then(([espaciosData, recursosData, zonasData]) => {
        setEspacios(
          espaciosData
            .filter((espacio) => espacio.estado === 'activo')
            .map((espacio) => ({
              espacio,
              recursos: recursosData.filter((recurso) => recurso.espacio_id === espacio.id),
              zonas: zonasData.filter((zona) => zona.espacio_id === espacio.id),
            })),
        );
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function recargarSlots(
    item: EspacioConRecursos,
    recs: number[],
    zonas: number[],
    nuevaFecha: string,
  ) {
    const primario = recs[0] ?? null;
    setLoadingSlots(true);
    setError(null);
    try {
      if (primario !== null) {
        setSlots(await getDisponibilidadRecurso(primario, nuevaFecha));
      } else if (item.espacio.modalidad_reserva !== 'equipos' && zonas.length > 0) {
        setSlots(slotsDesdeHorario(item.espacio, nuevaFecha));
      } else {
        setSlots([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo cargar la disponibilidad');
      setSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  }

  function cambiarFecha(nuevaFecha: string) {
    if (!seleccionado) return;
    setFecha(nuevaFecha);
    setHorasSeleccionadas([]);
    setPaso('editar');
    setAceptaTerminos(false);
    void recargarSlots(seleccionado, recursoIds, zonaIds, nuevaFecha);
  }

  function alternarRecurso(id: number) {
    const nuevos = recursoIds.includes(id) ? recursoIds.filter((item) => item !== id) : [...recursoIds, id];
    setRecursoIds(nuevos);
    setHorasSeleccionadas([]);
    setPaso('editar');
    setAceptaTerminos(false);
    if (seleccionado) void recargarSlots(seleccionado, nuevos, zonaIds, fecha);
  }

  function alternarZona(id: number) {
    const nuevos = zonaIds.includes(id) ? zonaIds.filter((item) => item !== id) : [...zonaIds, id];
    setZonaIds(nuevos);
    setHorasSeleccionadas([]);
    setPaso('editar');
    setAceptaTerminos(false);
    if (seleccionado) void recargarSlots(seleccionado, recursoIds, nuevos, fecha);
  }

  function alternarEnsayo(id: number) {
    setEnsayoIds((actuales) => (actuales.includes(id) ? actuales.filter((item) => item !== id) : [...actuales, id]));
    setPaso('editar');
    setAceptaTerminos(false);
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

  // Fase 12E: cargar ensayos de las zonas seleccionadas
  useEffect(() => {
    if (!seleccionado || zonaIds.length === 0) {
      setEnsayos([]);
      setEnsayoIds([]);
      return;
    }
    Promise.all(zonaIds.map((id) => listarEnsayos(id)))
      .then((listas) => {
        const todos = listas.flat();
        setEnsayos(todos);
        // limpiar ensayoIds huérfanos (ensayo de zona deseleccionada)
        setEnsayoIds((actuales) => actuales.filter((eid) => todos.some((e) => e.id === eid)));
      })
      .catch(() => setEnsayos([]));
  }, [zonaIds, seleccionado]);

  function abrirDisponibilidad(item: EspacioConRecursos) {
    focoPrevioRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    setSeleccionado(item);
    setSlots([]);
    setHorasSeleccionadas([]);
    setAsistentes(1);
    setTipo('');
    setPaso('editar');
    setAceptaTerminos(false);
    setReservaCreadaId(null);
    setReservaCreadaEstado(null);
    const recursosIniciales: number[] =
      item.espacio.modalidad_reserva !== 'zonas' && item.recursos.length > 0 ? [item.recursos[0].id] : [];
    // En mixto solo se preselecciona el primer recurso; las zonas se agregan
    // a elección del usuario. En modalidad zonas se preselecciona la primera.
    const zonasIniciales: number[] =
      recursosIniciales.length === 0 && item.espacio.modalidad_reserva !== 'equipos' && item.zonas.length > 0
        ? [item.zonas[0].id]
        : [];
    setRecursoIds(recursosIniciales);
    setZonaIds(zonasIniciales);
    setEnsayos([]);
    setEnsayoIds([]);
    setAcompanantes([]);
    void recargarSlots(item, recursosIniciales, zonasIniciales, fecha);
  }

  const recursosSeleccionados = seleccionado?.recursos.filter((recurso) => recursoIds.includes(recurso.id)) ?? [];
  const zonasSeleccionadas = seleccionado?.zonas.filter((zona) => zonaIds.includes(zona.id)) ?? [];
  const etiquetaObjetivo = [...zonasSeleccionadas, ...recursosSeleccionados]
    .map((item) => item.nombre)
    .sort()
    .join(', ');
  const capacidadMaxima = seleccionado
    ? (() => {
        const capacidades = [
          ...recursosSeleccionados.map((recurso) => recurso.capacidad).filter((valor): valor is number => valor !== null),
          ...zonasSeleccionadas.map((zona) => zona.capacidad).filter((valor): valor is number => valor !== null),
        ];
        // Fase 12E: capacidad ahora es opcional en espacio/recurso/zona.
        // `undefined` hace que React omita el atributo `max` del input
        // (sin límite conocido), igual que el backend se salta el chequeo
        // de aforo cuando no hay ningún dato de capacidad disponible.
        return capacidades.length > 0 ? Math.min(...capacidades) : (seleccionado.espacio.capacidad ?? undefined);
      })()
    : 1;
  const indicesOrdenados = [...horasSeleccionadas].sort((a, b) => a - b);
  const primerSlot = indicesOrdenados.length > 0 ? slots[indicesOrdenados[0]] : null;
  const ultimoSlot = indicesOrdenados.length > 0 ? slots[indicesOrdenados[indicesOrdenados.length - 1]] : null;
  const hayObjetivo = recursoIds.length > 0 || zonaIds.length > 0;
  const modalidad = seleccionado?.espacio.modalidad_reserva ?? 'equipos';

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
    if (!hayObjetivo || !primerSlot || !ultimoSlot || !aceptaTerminos) return;
    setGuardandoReserva(true);
    setError(null);
    try {
      const reserva = await crearReserva({
        recurso_ids: recursoIds,
        zona_ids: zonaIds,
        fecha,
        hora_inicio: primerSlot.hora_inicio,
        hora_fin: ultimoSlot.hora_fin,
        asistentes,
        // Fase 12D: solo se envía cuando el usuario eligió un tipo.
        ...(tipo ? { tipo } : {}),
        // Fase 12E: ensayos solo si hay zonas seleccionadas
        ...(ensayoIds.length > 0 ? { ensayo_ids: ensayoIds } : {}),
        // Fase 12E: acompañantes (se envía solo si hay filas con datos)
        ...(acompanantes.filter((a) => a.nombre.trim() && a.correo.trim()).length > 0
          ? { acompanantes: acompanantes.filter((a) => a.nombre.trim() && a.correo.trim()) }
          : {}),
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
          Elegí un espacio para consultar la disponibilidad de sus recursos y zonas.
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
                <dd className="inline">{item.espacio.capacidad !== null ? `${item.espacio.capacidad} personas` : 'Sin definir'}</dd>
              </div>
              <div>
                <dt className="inline text-text-muted">Recursos activos: </dt>
                <dd className="inline font-medium">{item.recursos.length}</dd>
              </div>
              {item.espacio.modalidad_reserva !== 'equipos' && (
                <div>
                  <dt className="inline text-text-muted">Zonas activas: </dt>
                  <dd className="inline font-medium">{item.zonas.length}</dd>
                </div>
              )}
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
            ) : !hayObjetivo && seleccionado.recursos.length === 0 && seleccionado.zonas.length === 0 ? (
              <p className="py-10 text-center text-text-muted">
                {modalidad === 'equipos'
                  ? 'Este espacio no tiene recursos activos disponibles.'
                  : modalidad === 'zonas'
                    ? 'Este espacio no tiene zonas activas disponibles.'
                    : 'Este espacio no tiene recursos ni zonas activos disponibles.'}
              </p>
            ) : paso === 'editar' ? (
              <>
                {modalidad !== 'zonas' && (
                  <fieldset className="mt-4">
                    <legend className="input-label">Recursos</legend>
                    {seleccionado.recursos.length === 0 ? (
                      <p className="text-sm text-text-muted">Este espacio no tiene recursos activos disponibles.</p>
                    ) : (
                      <div className="max-h-40 space-y-1 overflow-y-auto rounded border border-border p-2">
                        {seleccionado.recursos.map((recurso) => (
                          <label key={recurso.id} className="flex items-center gap-2 text-sm">
                            <input
                              type="checkbox"
                              className="h-4 w-4"
                              checked={recursoIds.includes(recurso.id)}
                              onChange={() => alternarRecurso(recurso.id)}
                            />
                            {recurso.nombre} · {recurso.tipo.nombre}
                            {recurso.capacidad !== null ? ` · Cap. ${recurso.capacidad}` : ''}
                          </label>
                        ))}
                      </div>
                    )}
                  </fieldset>
                )}

                {modalidad !== 'equipos' && (
                  <fieldset className="mt-4">
                    <legend className="input-label">Zonas</legend>
                    {seleccionado.zonas.length === 0 ? (
                      <p className="text-sm text-text-muted">Este espacio no tiene zonas activas disponibles.</p>
                    ) : (
                      <>
                        <div className="max-h-40 space-y-1 overflow-y-auto rounded border border-border p-2">
                          {seleccionado.zonas.map((zona) => (
                            <label key={zona.id} className="flex items-center gap-2 text-sm">
                              <input
                                type="checkbox"
                                className="h-4 w-4"
                                checked={zonaIds.includes(zona.id)}
                                onChange={() => alternarZona(zona.id)}
                              />
                              {zona.nombre}
                              {zona.capacidad !== null ? ` · Cap. ${zona.capacidad}` : ''}
                            </label>
                          ))}
                        </div>
                        {modalidad === 'zonas' && (
                          <p className="mt-1 text-xs text-text-muted">
                            Podés reservar una zona aunque no tenga recursos asociados.
                          </p>
                        )}
                      </>
                    )}
                  </fieldset>
                )}

                {zonaIds.length > 0 && ensayos.length > 0 && (
                  <fieldset className="mt-4">
                    <legend className="input-label">Ensayos (opcional)</legend>
                    <div className="max-h-40 space-y-1 overflow-y-auto rounded border border-border p-2">
                      {ensayos.map((ensayo) => (
                        <label key={ensayo.id} className="flex items-center gap-2 text-sm">
                          <input
                            type="checkbox"
                            className="h-4 w-4"
                            checked={ensayoIds.includes(ensayo.id)}
                            onChange={() => alternarEnsayo(ensayo.id)}
                          />
                          {ensayo.nombre}
                        </label>
                      ))}
                    </div>
                  </fieldset>
                )}

                <label className="input-label mt-4">
                  Fecha
                  <input
                    className="input"
                    type="date"
                    min={getLocalDateInputValue()}
                    value={fecha}
                    onChange={(event) => cambiarFecha(event.target.value)}
                  />
                </label>

                {!hayObjetivo ? (
                  <p className="py-6 text-center text-sm text-text-muted">
                    Seleccioná al menos un recurso o una zona.
                  </p>
                ) : loadingSlots ? (
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

                {isAuthenticated && hayObjetivo && primerSlot && ultimoSlot && (
                  <>
                    <label className="input-label mt-4">
                      Asistentes
                      <input
                        className="input"
                        type="number"
                        min={1}
                        max={capacidadMaxima}
                        value={asistentes}
                        onChange={(event) => setAsistentes(Number(event.target.value))}
                      />
                    </label>
                    <label className="input-label mt-4">
                      Tipo de reserva
                      <select
                        className="input"
                        value={tipo}
                        onChange={(event) => setTipo(event.target.value as TipoReserva | '')}
                      >
                        <option value="">Sin especificar</option>
                        <option value="trabajo_investigacion">Investigación</option>
                        <option value="trabajo_grado">Trabajo de grado</option>
                        <option value="servicio_de_ensayo">Servicio de ensayo</option>
                      </select>
                    </label>
                    <fieldset className="mt-4">
                      <legend className="input-label">Acompañantes (opcional)</legend>
                      {acompanantes.map((ac, idx) => (
                        <div key={idx} className="mb-2 flex gap-2">
                          <input
                            className="input flex-1"
                            placeholder="Nombre"
                            value={ac.nombre}
                            onChange={(event) =>
                              setAcompanantes((prev) =>
                                prev.map((item, i) => (i === idx ? { ...item, nombre: event.target.value } : item)),
                              )
                            }
                          />
                          <input
                            className="input flex-1"
                            placeholder="Correo"
                            value={ac.correo}
                            onChange={(event) =>
                              setAcompanantes((prev) =>
                                prev.map((item, i) => (i === idx ? { ...item, correo: event.target.value } : item)),
                              )
                            }
                          />
                          <button
                            type="button"
                            className="btn btn-secondary btn-sm"
                            onClick={() => setAcompanantes((prev) => prev.filter((_, i) => i !== idx))}
                          >
                            Quitar
                          </button>
                        </div>
                      ))}
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={() => setAcompanantes((prev) => [...prev, { nombre: '', correo: '' }])}
                      >
                        Agregar acompañante
                      </button>
                    </fieldset>
                    <button
                      className="btn btn-primary mt-4 w-full justify-center"
                      type="button"
                      onClick={() => {
                        setAceptaTerminos(false);
                        setPaso('resumen');
                      }}
                    >
                      {modalidad === 'equipos' ? 'Reservar recurso' : 'Reservar'}
                    </button>
                  </>
                )}
                {!isAuthenticated && hayObjetivo && (
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
                  <div><dt className="text-text-muted">Recursos / Zonas</dt><dd className="font-medium">{etiquetaObjetivo}</dd></div>
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