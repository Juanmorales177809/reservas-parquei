import { apiRequest } from "./http";
import type {
  Actividad,
  PerfilInv,
  Proyecto,
  Semillero,
  VinculacionAjenas,
} from "./investigacion-types";

/**
 * Un envoltorio delgado por endpoint de researchs (§2 a §5), tipado contra
 * specs/contratos/researchs/api-contract.md. Ninguna pantalla llama a
 * `apiRequest` con una ruta escrita a mano.
 */

/** §2.1 */
export function listarProyectos() {
  return apiRequest<{ datos: Proyecto[] }>("/api/investigacion/proyectos?tamano=100");
}

/** §2.1 */
export function listarSemilleros() {
  return apiRequest<{ datos: Semillero[] }>("/api/investigacion/semilleros?tamano=100");
}

/** §2.2 */
export function cambiarEstadoProyecto(id: number, estado: boolean) {
  return apiRequest<Proyecto>(`/api/investigacion/proyectos/${id}/estado`, {
    method: "PATCH",
    body: { estado },
  });
}

/** §2.2 */
export function cambiarEstadoSemillero(id: number, estado: boolean) {
  return apiRequest<Semillero>(`/api/investigacion/semilleros/${id}/estado`, {
    method: "PATCH",
    body: { estado },
  });
}

/** §3.1 */
export function crearActividad(datos: { nombre: string; dependencia: string }) {
  return apiRequest<Actividad>("/api/investigacion/actividades", {
    method: "POST",
    body: datos,
  });
}

/** §3.2 */
export function listarActividades() {
  return apiRequest<{ datos: Actividad[] }>("/api/investigacion/actividades?tamano=100");
}

/** §3.3 */
export function editarActividad(id: number, datos: { nombre?: string; dependencia?: string }) {
  return apiRequest<Actividad>(`/api/investigacion/actividades/${id}`, {
    method: "PATCH",
    body: datos,
  });
}

/** §3.4 */
export function cambiarEstadoActividad(id: number, estado: boolean) {
  return apiRequest<Actividad>(`/api/investigacion/actividades/${id}/estado`, {
    method: "PATCH",
    body: { estado },
  });
}

/** §4.1 */
export function crearPerfil(datos: { nombre: string; descripcion?: string }) {
  return apiRequest<PerfilInv>("/api/investigacion/perfiles", {
    method: "POST",
    body: datos,
  });
}

/** §4.2 */
export function listarPerfiles() {
  return apiRequest<{ datos: PerfilInv[] }>("/api/investigacion/perfiles?tamano=100");
}

/** §4.3 */
export function editarPerfil(id: number, datos: { nombre?: string; descripcion?: string }) {
  return apiRequest<PerfilInv>(`/api/investigacion/perfiles/${id}`, {
    method: "PATCH",
    body: datos,
  });
}

/** §4.3 */
export function cambiarEstadoPerfil(id: number, estado: boolean) {
  return apiRequest<PerfilInv>(`/api/investigacion/perfiles/${id}/estado`, {
    method: "PATCH",
    body: { estado },
  });
}

/** §5.1 */
export function vinculacionesDe(idUsuario: number) {
  return apiRequest<VinculacionAjenas>(`/api/investigacion/usuarios/${idUsuario}/vinculaciones`);
}

/** §5.2 */
export function crearVinculacionAjena(
  idUsuario: number,
  tipo: "proyectos" | "semilleros",
  idEntidad: number
) {
  const cuerpo = tipo === "proyectos" ? { id_proyecto: idEntidad } : { id_semillero: idEntidad };
  return apiRequest<unknown>(`/api/investigacion/usuarios/${idUsuario}/vinculaciones/${tipo}`, {
    method: "POST",
    body: cuerpo,
  });
}

/** §5.3 */
export function desactivarVinculacionAjena(
  idUsuario: number,
  tipo: "proyectos" | "semilleros",
  idEntidad: number
) {
  return apiRequest<void>(
    `/api/investigacion/usuarios/${idUsuario}/vinculaciones/${tipo}/${idEntidad}`,
    { method: "DELETE" }
  );
}
