'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import LoadingSpinner from '@/components/LoadingSpinner';
import { useAuth } from '@/context/AuthContext';
import {
  actualizarConfiguracionEspacio,
  obtenerConfiguracionEspacio,
} from '@/services/espacios';
import type { ConfiguracionEspacioUpdate } from '@/types/espacio';

const diasSemana = [
  { value: 0, label: 'Lun' },
  { value: 1, label: 'Mar' },
  { value: 2, label: 'Mié' },
  { value: 3, label: 'Jue' },
  { value: 4, label: 'Vie' },
  { value: 5, label: 'Sáb' },
  { value: 6, label: 'Dom' },
];

const horas = Array.from({ length: 16 }, (_, index) => index + 6);

const initialForm: ConfiguracionEspacioUpdate = {
  horario_atencion: {},
  horas_antelacion: 24,
  aprobacion_automatica: false,
};

export default function ConfiguracionEspacioPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [espacioNombre, setEspacioNombre] = useState('');
  const [form, setForm] = useState<ConfiguracionEspacioUpdate>(initialForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      router.replace('/login');
      return;
    }
    if (user?.rol !== 'gestor') {
      router.replace(user?.rol === 'admin' ? '/admin' : '/dashboard');
      return;
    }

    obtenerConfiguracionEspacio()
      .then((data) => {
        setEspacioNombre(data.espacio_nombre);
        setForm({
          horario_atencion: data.horario_atencion,
          horas_antelacion: data.horas_antelacion,
          aprobacion_automatica: data.aprobacion_automatica,
        });
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [authLoading, isAuthenticated, router, user?.rol]);

  function toggleFranja(dia: number, hora: number) {
    setSuccess(null);
    setForm((current) => ({
      ...current,
      horario_atencion: {
        ...current.horario_atencion,
        [dia]: (current.horario_atencion[dia] ?? []).includes(hora)
          ? (current.horario_atencion[dia] ?? []).filter((item) => item !== hora)
          : [...(current.horario_atencion[dia] ?? []), hora].sort((a, b) => a - b),
      },
    }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    if (!Object.values(form.horario_atencion).some((horasDia) => horasDia.length > 0)) {
      setError('Seleccioná al menos una franja de atención.');
      return;
    }

    setSaving(true);
    try {
      const data = await actualizarConfiguracionEspacio(form);
      setForm({
        horario_atencion: data.horario_atencion,
        horas_antelacion: data.horas_antelacion,
        aprobacion_automatica: data.aprobacion_automatica,
      });
      setSuccess('La configuración de atención fue actualizada.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo guardar la configuración');
    } finally {
      setSaving(false);
    }
  }

  if (authLoading || loading || !isAuthenticated || user?.rol !== 'gestor') {
    return <LoadingSpinner />;
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-text-primary sm:text-3xl">Configuración</h1>
        <p className="mt-1 text-text-secondary">
          Definí cuándo se pueden reservar los recursos de {espacioNombre}.
        </p>
      </div>

      {error && <div className="message-error mb-6">{error}</div>}
      {success && <div className="message-success mb-6">{success}</div>}

      <form className="card space-y-6" onSubmit={handleSubmit}>
        <fieldset>
          <legend className="font-semibold text-text-primary">Horario semanal de atención</legend>
          <p className="mt-1 text-sm text-text-muted">
            Seleccioná las franjas disponibles. Las celdas verdes permiten reservas; podés dejar
            espacios libres para almuerzo u otras pausas.
          </p>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-[720px] border-separate border-spacing-1 text-center text-sm">
              <thead>
                <tr>
                  <th className="sticky left-0 z-10 bg-surface-card px-3 py-2 text-left">Hora</th>
                  {diasSemana.map((dia) => (
                    <th key={dia.value} className="min-w-20 px-3 py-2 font-semibold">
                      {dia.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {horas.map((hora) => (
                  <tr key={hora}>
                    <th className="sticky left-0 z-10 whitespace-nowrap bg-surface-card px-3 py-2 text-left font-medium">
                      {String(hora).padStart(2, '0')}:00–{String(hora + 1).padStart(2, '0')}:00
                    </th>
                    {diasSemana.map((dia) => {
                      const seleccionada = (form.horario_atencion[dia.value] ?? []).includes(hora);
                      return (
                        <td key={dia.value} className="p-0.5">
                          <button
                            type="button"
                            aria-label={`${dia.label} de ${hora}:00 a ${hora + 1}:00`}
                            aria-pressed={seleccionada}
                            onClick={() => toggleFranja(dia.value, hora)}
                            className={`h-10 w-full rounded border transition-colors ${
                              seleccionada
                                ? 'border-green-500 bg-green-500 text-white hover:bg-green-600'
                                : 'border-border bg-surface-card hover:border-green-300 hover:bg-green-50'
                            }`}
                          >
                            {seleccionada ? 'Disponible' : ''}
                          </button>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </fieldset>

        <label className="input-label">
          Horas mínimas de antelación
          <input
            className="input mt-2 max-w-xs"
            type="number"
            min={0}
            max={8760}
            value={form.horas_antelacion}
            onChange={(event) => setForm({ ...form, horas_antelacion: Number(event.target.value) })}
            required
          />
          <span className="mt-2 block text-sm font-normal text-text-muted">
            Una reserva deberá solicitarse al menos con esta cantidad de horas.
          </span>
        </label>

        <div className="flex items-center gap-2">
          <label className="flex cursor-pointer items-center gap-3 text-sm font-medium text-text-primary" htmlFor="aprobacion-automatica">
            <input
              id="aprobacion-automatica"
              className="h-4 w-4 accent-primary-600"
              type="checkbox"
              checked={form.aprobacion_automatica}
              onChange={(event) => setForm({ ...form, aprobacion_automatica: event.target.checked })}
            />
            Aprobar automáticamente las solicitudes
          </label>
          <span className="group relative inline-flex">
            <button
              className="flex h-4 w-4 items-center justify-center rounded-full border border-text-muted text-[10px] text-text-muted"
              type="button"
              aria-label="Información sobre aprobación automática"
            >
              i
            </button>
            <span className="pointer-events-none absolute bottom-full left-1/2 z-20 mb-2 hidden w-72 -translate-x-1/2 rounded-md bg-slate-800 px-3 py-2 text-xs font-normal text-white shadow-lg group-hover:block group-focus-within:block">
              Al activarla, las solicitudes de los usuarios se aprueban al crearse. Si está desactivada,
              quedan pendientes para revisión. Las reservas del gestor en su propio espacio siempre se
              aprueban automáticamente.
            </span>
          </span>
        </div>

        <div className="flex justify-end">
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? 'Guardando...' : 'Guardar configuración'}
          </button>
        </div>
      </form>
    </div>
  );
}
