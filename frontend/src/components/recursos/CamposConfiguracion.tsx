"use client";

import { Field } from "@/src/components/ui/Field";
import type { ConfiguracionLaboratorio } from "@/src/lib/recursos-types";

/** Lo que se configura de un laboratorio (resources §3.2; RN-LAB-03, RN-LAB-04, RN-LAB-07, RN-APR-02, RN-REC-01). */
export interface ValoresConfig {
  habilitado: boolean;
  dias: number[];
  apertura: string;
  cierre: string;
  antelacion: string;
  aprobacion: boolean;
  recordatorio: string;
  correo: boolean;
}

/** `dias_atencion` numera 0 = domingo a 6 = sábado (contrato §3.1); se muestran de lunes a domingo. */
export const DIAS: { valor: number; nombre: string }[] = [
  { valor: 1, nombre: "Lunes" },
  { valor: 2, nombre: "Martes" },
  { valor: 3, nombre: "Miércoles" },
  { valor: 4, nombre: "Jueves" },
  { valor: 5, nombre: "Viernes" },
  { valor: 6, nombre: "Sábado" },
  { valor: 0, nombre: "Domingo" },
];

export const nombresDeDias = (dias: number[]) =>
  DIAS.filter((d) => dias.includes(d.valor)).map((d) => d.nombre).join(", ") || "ninguno";

/** Punto de partida de un laboratorio sin configuración: lunes a viernes, sin antelación ni aprobación automática. */
export const CONFIG_INICIAL: ValoresConfig = {
  habilitado: true, dias: [1, 2, 3, 4, 5], apertura: "", cierre: "", antelacion: "0",
  aprobacion: false, recordatorio: "24", correo: false,
};

export function desdeConfiguracion(c: ConfiguracionLaboratorio): ValoresConfig {
  return {
    habilitado: c.habilitado_reservas,
    dias: c.dias_atencion,
    apertura: c.hora_apertura.slice(0, 5),
    cierre: c.hora_cierre.slice(0, 5),
    antelacion: String(c.horas_antelacion),
    aprobacion: c.aprobacion_automatica,
    recordatorio: String(c.recordatorio_horas_antes),
    correo: c.notificar_por_correo === true,
  };
}

/** Motivo por el que no se puede guardar, o `null`. */
export function errorConfiguracion(v: ValoresConfig): string | null {
  if (v.dias.length === 0) return "Elige al menos un día de atención.";
  if (!v.apertura || !v.cierre) return "Indica la hora de apertura y la de cierre.";
  if (v.apertura >= v.cierre) return "La apertura debe ser anterior al cierre.";
  if (!/^\d+$/.test(v.antelacion)) return "La antelación mínima debe ser un número de horas, cero o más.";
  if (!/^\d+$/.test(v.recordatorio) || Number(v.recordatorio) <= 0) return "El recordatorio debe anticiparse una hora o más.";
  return null;
}

export function cuerpoConfiguracion(v: ValoresConfig) {
  return {
    habilitado_reservas: v.habilitado,
    dias_atencion: v.dias,
    hora_apertura: v.apertura,
    hora_cierre: v.cierre,
    horas_antelacion: Number(v.antelacion),
    aprobacion_automatica: v.aprobacion,
    recordatorio_horas_antes: Number(v.recordatorio),
    notificar_por_correo: v.correo,
  };
}

export function CamposConfiguracion({ valores, onChange }: { valores: ValoresConfig; onChange: (v: ValoresConfig) => void }) {
  const poner = (k: keyof ValoresConfig) => (e: { target: { value: string } }) => onChange({ ...valores, [k]: e.target.value });
  const casilla = (k: "habilitado" | "aprobacion" | "correo", etiqueta: string, ayuda: string) => (
    <label className="flex flex-col gap-0.5 text-sm text-text">
      <span className="flex items-center gap-2">
        <input type="checkbox" checked={valores[k]} onChange={(e) => onChange({ ...valores, [k]: e.target.checked })} />
        {etiqueta}
      </span>
      <span className="ml-6 text-muted">{ayuda}</span>
    </label>
  );

  return (
    <>
      {casilla("habilitado", "Acepta reservas", "Si se desactiva, no se crean reservas nuevas; las existentes no cambian.")}
      <fieldset className="flex flex-col gap-1">
        <legend className="text-sm font-bold text-text">Días de atención</legend>
        <div className="flex flex-wrap gap-x-4 gap-y-1">
          {DIAS.map((d) => (
            <label key={d.valor} className="flex items-center gap-1 text-sm text-text">
              <input
                type="checkbox"
                checked={valores.dias.includes(d.valor)}
                onChange={(e) =>
                  onChange({
                    ...valores,
                    dias: e.target.checked ? [...valores.dias, d.valor] : valores.dias.filter((x) => x !== d.valor),
                  })
                }
              />
              {d.nombre}
            </label>
          ))}
        </div>
      </fieldset>
      <div className="flex gap-2">
        <Field id="lab-apertura" label="Apertura" type="time" value={valores.apertura} onChange={poner("apertura")} required />
        <Field id="lab-cierre" label="Cierre" type="time" value={valores.cierre} onChange={poner("cierre")} required />
      </div>
      <div className="flex gap-2">
        <Field id="lab-antelacion" label="Antelación mínima (horas)" type="number" value={valores.antelacion} onChange={poner("antelacion")} />
        <Field id="lab-recordatorio" label="Recordatorio (horas antes)" type="number" value={valores.recordatorio} onChange={poner("recordatorio")} />
      </div>
      {casilla("aprobacion", "Aprobación automática", "Las reservas de los usuarios nacen aprobadas si cumplen las validaciones (no aplica a lista de espera).")}
      {casilla("correo", "Enviar avisos por correo", "Habilita el correo de las notificaciones de este laboratorio; los avisos en pantalla se generan igual.")}
    </>
  );
}
