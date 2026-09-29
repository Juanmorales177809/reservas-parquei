"use client";

import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import type { EspacioCampoDetalle } from "@/src/lib/espacios-types";

export type ValoresCampos = Record<number, { texto: string; opcion: string }>;

/** Campos habilitados de un espacio, en su orden (RN-ESP-CAM-01, RN-TIP-PE-12). */
export function camposHabilitados(campos: EspacioCampoDetalle[] | undefined): EspacioCampoDetalle[] {
  return [...(campos ?? [])].filter((c) => c.habilitado).sort((a, b) => a.orden - b.orden);
}

function vacio(campo: EspacioCampoDetalle, v: { texto: string; opcion: string } | undefined): boolean {
  if (!v) return true;
  if (campo.tipo === "SELECCION") return v.opcion === "";
  if (campo.tipo === "BOOLEANO") return v.texto === "";
  return v.texto.trim() === "";
}

/** Nombres de los campos obligatorios sin diligenciar (RN-TIP-PE-18). */
export function faltantes(campos: EspacioCampoDetalle[], valores: ValoresCampos): string[] {
  return campos.filter((c) => c.obligatorio && vacio(c, valores[c.id])).map((c) => c.nombre);
}

/** Cuerpo `campos_adicionales` del contrato §2.1: solo los campos con valor. */
export function camposParaEnviar(campos: EspacioCampoDetalle[], valores: ValoresCampos) {
  return campos
    .filter((c) => !vacio(c, valores[c.id]))
    .map((c) =>
      c.tipo === "SELECCION"
        ? { campo_id: c.id, opcion_id: Number(valores[c.id].opcion) }
        : { campo_id: c.id, valor_texto: valores[c.id].texto.trim() }
    );
}

/** Formulario de los campos adicionales que el espacio pide al reservar. */
export function CamposAdicionalesReserva({
  campos,
  valores,
  onChange,
}: {
  campos: EspacioCampoDetalle[];
  valores: ValoresCampos;
  onChange: (v: ValoresCampos) => void;
}) {
  if (campos.length === 0) return null;
  const poner = (id: number, parcial: Partial<{ texto: string; opcion: string }>) =>
    onChange({ ...valores, [id]: { ...(valores[id] ?? { texto: "", opcion: "" }), ...parcial } });

  return (
    <fieldset className="flex flex-col gap-3">
      <legend className="text-sm font-bold text-text">Información que pide este espacio</legend>
      {campos.map((c) => {
        const etiqueta = c.obligatorio ? c.nombre : `${c.nombre} (opcional)`;
        const id = `res-campo-${c.id}`;
        const v = valores[c.id] ?? { texto: "", opcion: "" };
        switch (c.tipo) {
          case "TEXTO_LARGO":
            return (
              <div key={c.id} className="flex flex-col gap-1">
                <label htmlFor={id} className="text-sm font-bold text-text">{etiqueta}</label>
                <textarea id={id} rows={3} value={v.texto} onChange={(e) => poner(c.id, { texto: e.target.value })}
                  className="rounded-control border border-border bg-surface px-4 py-2 text-[14px] text-text" />
              </div>
            );
          case "NUMERO":
            return (
              <Field key={c.id} id={id} label={etiqueta} type="number" value={v.texto}
                onChange={(e) => poner(c.id, { texto: e.target.value })} />
            );
          case "BOOLEANO":
            return (
              <Select key={c.id} id={id} label={etiqueta} value={v.texto}
                onChange={(e) => poner(c.id, { texto: e.target.value })}>
                <option value="">Seleccionar…</option>
                <option value="true">Sí</option>
                <option value="false">No</option>
              </Select>
            );
          case "SELECCION":
            return (
              <Select key={c.id} id={id} label={etiqueta} value={v.opcion}
                onChange={(e) => poner(c.id, { opcion: e.target.value })}>
                <option value="">Seleccionar…</option>
                {[...(c.opciones ?? [])].filter((o) => o.habilitado).sort((a, b) => a.orden - b.orden).map((o) => (
                  <option key={o.id} value={o.id}>{o.valor}</option>
                ))}
              </Select>
            );
          default:
            return (
              <Field key={c.id} id={id} label={etiqueta} value={v.texto}
                onChange={(e) => poner(c.id, { texto: e.target.value })} />
            );
        }
      })}
    </fieldset>
  );
}
