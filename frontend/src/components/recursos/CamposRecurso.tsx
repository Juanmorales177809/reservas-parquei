"use client";

import { Field } from "@/src/components/ui/Field";
import type { TipoRecurso } from "@/src/lib/recursos-types";

/** Valores del formulario de un recurso (texto y casillas). Un campo vacío no se envía. */
export interface ValoresRecurso {
  nombre: string;
  descripcion: string;
  placa: string;
  serial: string;
  marca: string;
  modelo: string;
  guia_rapida: string;
  instalador: string;
  proxima_fecha_calibracion: string;
  proxima_fecha_mantenimiento: string;
  requiere_apoyo: boolean;
  acreditado: boolean;
  operativo: boolean;
  requiere_calibracion: boolean;
}

const s = (v: unknown) => (v === null || v === undefined ? "" : String(v));

export function valoresIniciales(tipo: TipoRecurso, esp: Record<string, unknown> = {}): ValoresRecurso {
  const equipo = tipo === "EQUIPO";
  return {
    nombre: s(equipo ? esp.nombre_equipo : esp.nombre),
    descripcion: s(esp.descripcion),
    placa: s(esp.placa),
    serial: s(esp.serial),
    marca: s(esp.marca),
    modelo: s(esp.modelo),
    guia_rapida: s(esp.guia_rapida),
    instalador: s(esp.instalador),
    proxima_fecha_calibracion: s(esp.proxima_fecha_calibracion),
    proxima_fecha_mantenimiento: s(esp.proxima_fecha_mantenimiento),
    requiere_apoyo: esp.requiere_apoyo === true,
    acreditado: esp.acreditado === true,
    // Un equipo nuevo nace operativo; el estado guardado manda cuando existe.
    operativo: esp.estado === undefined || esp.estado === null ? true : esp.estado === true,
    requiere_calibracion: esp.requiere_calibracion === true,
  };
}

const TEXTOS_EQUIPO = ["placa", "serial", "marca", "modelo", "guia_rapida", "instalador", "proxima_fecha_calibracion", "proxima_fecha_mantenimiento"] as const;

/**
 * Cuerpo `especializacion` del contrato (resources §2.1 y §2.4). Al crear se envía lo diligenciado; al editar,
 * solo lo que cambió respecto de `previos`, y un texto que se vació viaja como `null` para borrarlo.
 */
export function especializacionDe(
  tipo: TipoRecurso,
  v: ValoresRecurso,
  previos?: ValoresRecurso
): Record<string, unknown> {
  const salida: Record<string, unknown> = {};
  const cambio = <K extends keyof ValoresRecurso>(k: K) => !previos || previos[k] !== v[k];
  const texto = (campoApi: string, k: keyof ValoresRecurso) => {
    if (!cambio(k)) return;
    const valor = String(v[k]).trim();
    if (valor !== "") salida[campoApi] = valor;
    else if (previos) salida[campoApi] = null;
  };

  if (tipo === "EQUIPO") {
    if (cambio("nombre")) salida.nombre_equipo = v.nombre.trim();
    for (const k of TEXTOS_EQUIPO) texto(k, k);
    if (cambio("requiere_apoyo") || !previos) salida.requiere_apoyo = v.requiere_apoyo;
    if (cambio("acreditado") || !previos) salida.acreditado = v.acreditado;
    if (cambio("operativo") || !previos) salida.estado = v.operativo;
    if (cambio("requiere_calibracion") || !previos) salida.requiere_calibracion = v.requiere_calibracion;
  } else {
    if (cambio("nombre")) salida.nombre = v.nombre.trim();
    texto("descripcion", "descripcion");
  }
  return salida;
}

/** Campos de un recurso según su tipo (RN-EQP, RN-MOB, RN-OTR). */
export function CamposRecurso({
  tipo,
  valores,
  onChange,
  prefijo,
}: {
  tipo: TipoRecurso;
  valores: ValoresRecurso;
  onChange: (v: ValoresRecurso) => void;
  prefijo: string;
}) {
  const poner = (k: keyof ValoresRecurso) => (e: { target: { value: string } }) => onChange({ ...valores, [k]: e.target.value });
  const casilla = (k: keyof ValoresRecurso, etiqueta: string, ayuda?: string) => (
    <label className="flex flex-col gap-0.5 text-sm text-text">
      <span className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={Boolean(valores[k])}
          onChange={(e) => onChange({ ...valores, [k]: e.target.checked })}
        />
        {etiqueta}
      </span>
      {ayuda && <span className="ml-6 text-muted">{ayuda}</span>}
    </label>
  );

  if (tipo !== "EQUIPO") {
    return (
      <>
        <Field id={`${prefijo}-nombre`} label="Nombre" value={valores.nombre} onChange={poner("nombre")} required />
        <Field id={`${prefijo}-descripcion`} label="Descripción (opcional)" value={valores.descripcion} onChange={poner("descripcion")} />
      </>
    );
  }

  return (
    <>
      <Field id={`${prefijo}-nombre`} label="Nombre del equipo" value={valores.nombre} onChange={poner("nombre")} required />
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <Field id={`${prefijo}-placa`} label="Placa" value={valores.placa} onChange={poner("placa")} />
        <Field id={`${prefijo}-serial`} label="Serial" value={valores.serial} onChange={poner("serial")} />
        <Field id={`${prefijo}-marca`} label="Marca" value={valores.marca} onChange={poner("marca")} />
        <Field id={`${prefijo}-modelo`} label="Modelo" value={valores.modelo} onChange={poner("modelo")} />
      </div>
      <div className="flex flex-col gap-2">
        {casilla("operativo", "Operativo", "Un equipo no operativo no se puede reservar.")}
        {casilla("requiere_apoyo", "Exige acompañamiento técnico", "Toda reserva que lo incluya llevará apoyo técnico.")}
        {casilla("acreditado", "Acreditado", "Destinado a ensayos certificados: no es reservable.")}
        {casilla("requiere_calibracion", "Requiere calibración")}
      </div>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <Field id={`${prefijo}-calibracion`} label="Próxima calibración" type="date"
          value={valores.proxima_fecha_calibracion} onChange={poner("proxima_fecha_calibracion")} />
        <Field id={`${prefijo}-mantenimiento`} label="Próximo mantenimiento" type="date"
          value={valores.proxima_fecha_mantenimiento} onChange={poner("proxima_fecha_mantenimiento")} />
      </div>
      <Field id={`${prefijo}-instalador`} label="Instalador (opcional)" value={valores.instalador} onChange={poner("instalador")} />
      <Field id={`${prefijo}-guia`} label="Guía rápida (opcional)" value={valores.guia_rapida} onChange={poner("guia_rapida")} />
    </>
  );
}
