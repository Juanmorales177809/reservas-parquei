"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/src/components/ui/Button";
import { Field } from "@/src/components/ui/Field";
import { Select } from "@/src/components/ui/Select";
import {
  agregarOpciones,
  cambiarEstadoCampo,
  crearCampo,
  editarCampo,
  editarOpcion,
  reordenarCampos,
} from "@/src/lib/espacios-api";
import type { EspacioCampoDetalle, TipoCampo } from "@/src/lib/espacios-types";

export const NOMBRE_TIPO_CAMPO: Record<string, string> = {
  TEXTO: "Texto",
  TEXTO_LARGO: "Texto largo",
  NUMERO: "Número",
  BOOLEANO: "Sí / no",
  SELECCION: "Lista de opciones",
};

type Actuar = (accion: () => Promise<unknown>, exito: string) => Promise<void>;

function FilaOpcion({
  espacioId, campoId, opcion, ocupada, actuar,
}: {
  espacioId: number;
  campoId: number;
  opcion: NonNullable<EspacioCampoDetalle["opciones"]>[number];
  ocupada: boolean;
  actuar: Actuar;
}) {
  const [valor, setValor] = useState(opcion.valor);
  return (
    <li className="flex items-end gap-2">
      <Field id={`opc-${opcion.id}`} label={opcion.habilitado ? "Opción" : "Opción (deshabilitada)"} value={valor}
        onChange={(e) => setValor(e.target.value)} />
      <Button variant="ghost" size="sm" disabled={ocupada || valor.trim() === "" || valor === opcion.valor}
        onClick={() => void actuar(() => editarOpcion(espacioId, campoId, opcion.id, { valor: valor.trim() }), "Opción actualizada.")}>
        Guardar nombre
      </Button>
      <Button variant="ghost" size="sm" disabled={ocupada}
        onClick={() => void actuar(
          () => editarOpcion(espacioId, campoId, opcion.id, { habilitado: !opcion.habilitado }),
          opcion.habilitado ? "Opción deshabilitada." : "Opción habilitada."
        )}>
        {opcion.habilitado ? "Deshabilitar" : "Habilitar"}
      </Button>
    </li>
  );
}

function FilaCampo({
  espacioId, campo, indice, ordenados, ocupada, actuar,
}: {
  espacioId: number;
  campo: EspacioCampoDetalle;
  indice: number;
  ordenados: EspacioCampoDetalle[];
  ocupada: boolean;
  actuar: Actuar;
}) {
  const [nombre, setNombre] = useState(campo.nombre);
  const [nuevaOpcion, setNuevaOpcion] = useState("");

  const mover = (hacia: -1 | 1) => {
    const otro = ordenados[indice + hacia];
    return actuar(
      () => reordenarCampos(espacioId, [
        { campo_id: campo.id, orden: otro.orden },
        { campo_id: otro.id, orden: campo.orden },
      ]),
      "Orden actualizado."
    );
  };

  return (
    <li className="flex flex-col gap-2 border-b border-border pb-3">
      <div className="flex flex-wrap items-end gap-2">
        <Field id={`campo-${campo.id}`} label={`${NOMBRE_TIPO_CAMPO[campo.tipo] ?? campo.tipo}${campo.habilitado ? "" : " (deshabilitado)"}`}
          value={nombre} onChange={(e) => setNombre(e.target.value)} />
        <Button variant="ghost" size="sm" disabled={ocupada || nombre.trim() === "" || nombre === campo.nombre}
          onClick={() => void actuar(() => editarCampo(espacioId, campo.id, { nombre: nombre.trim() }), "Campo actualizado.")}>
          Guardar nombre
        </Button>
        <label className="flex items-center gap-2 pb-2 text-sm text-text">
          <input type="checkbox" checked={campo.obligatorio} disabled={ocupada}
            onChange={(e) => void actuar(
              () => editarCampo(espacioId, campo.id, { obligatorio: e.target.checked }),
              e.target.checked ? "El campo ahora es obligatorio." : "El campo ahora es opcional."
            )} />
          Obligatorio
        </label>
        <Button variant="ghost" size="sm" disabled={ocupada || indice === 0} onClick={() => void mover(-1)}>Subir</Button>
        <Button variant="ghost" size="sm" disabled={ocupada || indice === ordenados.length - 1} onClick={() => void mover(1)}>Bajar</Button>
        <Button variant="ghost" size="sm" disabled={ocupada}
          onClick={() => void actuar(() => cambiarEstadoCampo(espacioId, campo.id, !campo.habilitado), "Campo actualizado.")}>
          {campo.habilitado ? "Deshabilitar" : "Habilitar"}
        </Button>
      </div>
      {campo.tipo === "SELECCION" && (
        <div className="ml-4 flex flex-col gap-2">
          <ul className="flex flex-col gap-1">
            {[...(campo.opciones ?? [])].sort((a, b) => a.orden - b.orden).map((o) => (
              <FilaOpcion key={`${o.id}-${o.valor}`} espacioId={espacioId} campoId={campo.id} opcion={o} ocupada={ocupada} actuar={actuar} />
            ))}
          </ul>
          <div className="flex items-end gap-2">
            <Field id={`nueva-opcion-${campo.id}`} label="Agregar opción" value={nuevaOpcion} onChange={(e) => setNuevaOpcion(e.target.value)} />
            <Button variant="secondary" size="sm" disabled={ocupada || nuevaOpcion.trim() === ""}
              onClick={() => void actuar(() => agregarOpciones(espacioId, campo.id, [{ valor: nuevaOpcion.trim() }]), "Opción agregada.").then(() => setNuevaOpcion(""))}>
              Agregar
            </Button>
          </div>
        </div>
      )}
    </li>
  );
}

/** Campos adicionales que un espacio pide al reservar (WF-ESP-03; RN-ESP-CAM-01 a RN-ESP-CAM-05). */
export function CamposDelEspacio({
  espacioId, campos, puedeGestionar, ocupada, actuar,
}: {
  espacioId: number;
  campos: EspacioCampoDetalle[];
  puedeGestionar: boolean;
  ocupada: boolean;
  actuar: Actuar;
}) {
  const ordenados = [...campos].sort((a, b) => a.orden - b.orden);
  const [nombre, setNombre] = useState("");
  const [tipo, setTipo] = useState<TipoCampo>("TEXTO");
  const [obligatorio, setObligatorio] = useState(false);
  const [opcion, setOpcion] = useState("");

  function agregar(evento: FormEvent) {
    evento.preventDefault();
    void actuar(
      () => crearCampo(espacioId, {
        nombre: nombre.trim(),
        tipo,
        obligatorio,
        ...(tipo === "SELECCION" && opcion.trim() ? { opciones: [{ valor: opcion.trim() }] } : {}),
      }),
      "Campo creado."
    ).then(() => {
      setNombre("");
      setOpcion("");
      setObligatorio(false);
    });
  }

  return (
    <section aria-label="Campos adicionales" className="flex flex-col gap-3">
      <h2 className="text-base font-bold text-text">Campos adicionales</h2>
      {ordenados.length === 0 && <p className="text-sm text-muted">Este espacio no pide información adicional al reservar.</p>}
      {puedeGestionar ? (
        <ul className="flex flex-col gap-3">
          {ordenados.map((c, i) => (
            <FilaCampo key={`${c.id}-${c.nombre}`} espacioId={espacioId} campo={c} indice={i} ordenados={ordenados} ocupada={ocupada} actuar={actuar} />
          ))}
        </ul>
      ) : (
        <ul className="flex flex-col gap-1 text-sm text-text">
          {ordenados.filter((c) => c.habilitado).map((c) => (
            <li key={c.id}>{c.nombre} ({NOMBRE_TIPO_CAMPO[c.tipo] ?? c.tipo}){c.obligatorio ? " · obligatorio" : ""}</li>
          ))}
        </ul>
      )}
      {puedeGestionar && (
        <form onSubmit={agregar} className="flex flex-col gap-2">
          <h3 className="text-sm font-bold text-text">Agregar campo</h3>
          <Field id="campo-nombre" label="Nombre" value={nombre} onChange={(e) => setNombre(e.target.value)} required />
          <Select id="campo-tipo" label="Tipo" value={tipo} onChange={(e) => setTipo(e.target.value as TipoCampo)}>
            {Object.entries(NOMBRE_TIPO_CAMPO).map(([codigo, texto]) => (
              <option key={codigo} value={codigo}>{texto}</option>
            ))}
          </Select>
          {tipo === "SELECCION" && (
            <Field id="campo-opcion" label="Primera opción (obligatoria para listas)" value={opcion} onChange={(e) => setOpcion(e.target.value)} />
          )}
          <label className="flex items-center gap-2 text-sm text-text">
            <input type="checkbox" checked={obligatorio} onChange={(e) => setObligatorio(e.target.checked)} />
            Obligatorio al reservar
          </label>
          <div>
            <Button type="submit" variant="secondary" loading={ocupada}>Agregar campo</Button>
          </div>
        </form>
      )}
    </section>
  );
}
