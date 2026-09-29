"use client";

import { listarPersonal, listarUnidades, listarUsuarios } from "@/src/lib/administracion-api";
import { listarEspacios } from "@/src/lib/espacios-api";
import { listarProyectos, listarSemilleros } from "@/src/lib/investigacion-api";
import { ApiRequestError } from "@/src/lib/http";
import { listarLaboratorios, listarRecursos } from "@/src/lib/recursos-api";
import { SelectorEntidad, type OpcionSelector } from "./SelectorEntidad";

interface Base {
  id: string;
  label: string;
  value: string;
  onChange: (valor: string) => void;
  requerido?: boolean;
}

const NOMBRE_TIPO_RECURSO: Record<string, string> = { EQUIPO: "Equipo", MOBILIARIO: "Mobiliario", OTRO: "Otro" };

// `GET /api/unidades` exige permiso de administración: una cuenta sin él recibe 403 y se pasa al catálogo de
// laboratorios (resources §3.0), que puede leer cualquiera. Se recuerda para no repetir la petición fallida.
let usarCatalogoDeLaboratorios = false;

async function unidadesVisibles(tipo?: string, soloIds?: number[]): Promise<OpcionSelector[]> {
  const opciones = await todasLasUnidades(tipo);
  return soloIds ? opciones.filter((o) => soloIds.includes(Number(o.valor))) : opciones;
}

async function todasLasUnidades(tipo?: string): Promise<OpcionSelector[]> {
  if (!usarCatalogoDeLaboratorios) {
    try {
      return (await listarUnidades()).datos
        .filter((u) => u.estado && (!tipo || u.tipo === tipo))
        .map((u) => ({ valor: String(u.id_unidad), etiqueta: u.nombre }));
    } catch (error) {
      if (!(error instanceof ApiRequestError && error.status === 403)) throw error;
      usarCatalogoDeLaboratorios = true;
    }
  }
  return (await listarLaboratorios()).datos.map((l) => ({ valor: String(l.id_unidad), etiqueta: l.nombre }));
}

/** Solo para las pruebas: vuelve a intentar primero la lista administrativa. */
export function reiniciarCatalogoDeUnidades() {
  usarCatalogoDeLaboratorios = false;
}

/** `soloIds`: quien tiene alcance por unidad ve ofrecidas solo las suyas (el servidor sigue acotando). */
export function SelectorUnidad({
  tipo,
  soloIds,
  textoVacio = "Seleccionar unidad",
  ...base
}: Base & { tipo?: string; soloIds?: number[]; textoVacio?: string }) {
  return (
    <SelectorEntidad
      {...base}
      textoVacio={textoVacio}
      clave={`${tipo ?? ""}|${soloIds?.join(",") ?? ""}`}
      cargar={() => unidadesVisibles(tipo, soloIds)}
    />
  );
}

export function SelectorEspacio({ idUnidad, ...base }: Base & { idUnidad: string }) {
  return (
    <SelectorEntidad
      {...base}
      clave={idUnidad}
      deshabilitado={!idUnidad}
      textoVacio={idUnidad ? "Seleccionar espacio" : "Elige primero la unidad"}
      cargar={async () =>
        (await listarEspacios({ id_unidad: Number(idUnidad), habilitado: true })).datos.map((e) => ({
          valor: String(e.id),
          etiqueta: `${e.nombre} (cap. ${e.capacidad})`,
        }))
      }
    />
  );
}

export function SelectorRecurso({ idUnidad, reservable = true, ...base }: Base & { idUnidad: string; reservable?: boolean }) {
  return (
    <SelectorEntidad
      {...base}
      clave={`${idUnidad}-${reservable}`}
      deshabilitado={!idUnidad}
      textoVacio={idUnidad ? "Seleccionar recurso" : "Elige primero la unidad"}
      cargar={async () =>
        (await listarRecursos({ id_unidad: Number(idUnidad), ...(reservable ? { reservable: true } : {}) })).datos
          .filter((r) => r.habilitado)
          .map((r) => ({
            valor: String(r.id),
            etiqueta: `${r.nombre ?? "Sin nombre"} · ${NOMBRE_TIPO_RECURSO[r.tipo] ?? r.tipo}`,
          }))
      }
    />
  );
}


export function SelectorProyecto({ textoVacio = "Sin proyecto", ...base }: Base & { textoVacio?: string }) {
  return (
    <SelectorEntidad
      {...base}
      textoVacio={textoVacio}
      cargar={async () =>
        (await listarProyectos()).datos
          .filter((p) => p.estado)
          .map((p) => ({ valor: String(p.id_proyecto), etiqueta: `${p.nombre} (${p.codigo})` }))
      }
    />
  );
}

export function SelectorSemillero({ textoVacio = "Seleccionar semillero", ...base }: Base & { textoVacio?: string }) {
  return (
    <SelectorEntidad
      {...base}
      textoVacio={textoVacio}
      cargar={async () =>
        (await listarSemilleros()).datos
          .filter((s) => s.estado)
          .map((s) => ({ valor: String(s.id_semillero), etiqueta: `${s.nombre} (${s.codigo})` }))
      }
    />
  );
}

/** Cuentas por el nombre de su titular (personal y usuarios). */
export function SelectorCuenta({ textoVacio = "Seleccionar cuenta", ...base }: Base & { textoVacio?: string }) {
  return (
    <SelectorEntidad
      {...base}
      textoVacio={textoVacio}
      cargar={async (): Promise<OpcionSelector[]> => {
        const [personal, usuarios] = await Promise.all([listarPersonal(), listarUsuarios()]);
        return [...personal.datos, ...usuarios.datos]
          .filter((i) => i.id_cuenta !== null && i.id_cuenta !== undefined)
          .map((i) => ({ valor: String(i.id_cuenta), etiqueta: `${i.nombre} · ${i.correo}` }))
          .sort((a, b) => a.etiqueta.localeCompare(b.etiqueta, "es"));
      }}
    />
  );
}

export function SelectorUsuario(base: Base) {
  return (
    <SelectorEntidad
      {...base}
      textoVacio="Seleccionar usuario"
      cargar={async () =>
        (await listarUsuarios()).datos
          .filter((u) => u.estado && u.id_usuario !== undefined)
          .map((u) => ({ valor: String(u.id_usuario), etiqueta: `${u.nombre} · ${u.correo}` }))
      }
    />
  );
}
