import { apiRequest } from "./http";
import type {
  CatalogoEntidad,
  ConfirmacionInicial,
  DesactivarRespuesta,
  Perfil,
  PerfilCatalogoItem,
} from "./usuarios-types";

/**
 * Un envoltorio delgado por endpoint de usuarios (§2 a §4), tipado contra
 * specs/contratos/usuarios/api-contract.md. Ninguna pantalla llama a
 * `apiRequest` con una ruta escrita a mano. §5–§6 (administración de
 * identidades) pertenecen a administration y no tienen pantalla aquí.
 */

/** §2.1 */
export function obtenerPerfil() {
  return apiRequest<Perfil>("/api/perfil");
}

/** §2.2 */
export function actualizarPerfil(datos: {
  nombre: string;
  documento: string;
  telefono: string;
  institucion: string;
  dependencia: string;
}) {
  return apiRequest<Perfil>("/api/perfil", { method: "PATCH", body: datos });
}

/** §2.3 */
export function confirmarActualizacionInicial() {
  return apiRequest<ConfirmacionInicial>("/api/perfil/actualizacion-inicial", {
    method: "POST",
    body: {},
  });
}

/** §3.0 */
export function catalogoPerfiles() {
  return apiRequest<{ datos: PerfilCatalogoItem[] }>(
    "/api/perfil/perfiles/catalogo"
  );
}

/** §3.1 */
export function guardarPerfiles(perfiles: number[]) {
  return apiRequest<{ perfiles: PerfilCatalogoItem[] }>("/api/perfil/perfiles", {
    method: "PUT",
    body: { perfiles },
  });
}

/** §4.1 */
export function catalogoVinculaciones(
  tipo: "proyectos" | "semilleros",
  busqueda?: string
) {
  const consulta =
    busqueda && busqueda.trim()
      ? `?tipo=${tipo}&busqueda=${encodeURIComponent(busqueda.trim())}`
      : `?tipo=${tipo}`;
  return apiRequest<{ datos: CatalogoEntidad[] }>(
    `/api/perfil/vinculaciones/catalogo${consulta}`
  );
}

/** §4.2 */
export function asociarProyecto(id_proyecto: number) {
  return apiRequest<unknown>("/api/perfil/vinculaciones/proyectos", {
    method: "POST",
    body: { id_proyecto },
  });
}

/** §4.3 */
export function asociarSemillero(id_semillero: number) {
  return apiRequest<unknown>("/api/perfil/vinculaciones/semilleros", {
    method: "POST",
    body: { id_semillero },
  });
}

/** §4.4 */
export function registrarPasantia(datos: {
  universidad: string;
  docente_itm_nombre: string;
  docente_itm_correo: string;
}) {
  return apiRequest<unknown>("/api/perfil/vinculaciones/pasantias", {
    method: "POST",
    body: datos,
  });
}

/** §4.5 */
export function registrarTrabajoGrado(datos: {
  director_nombre: string;
  director_correo: string;
}) {
  return apiRequest<unknown>("/api/perfil/vinculaciones/trabajos-grado", {
    method: "POST",
    body: datos,
  });
}

/** §4.6 */
export function desactivarVinculacion(
  tipo: "proyectos" | "semilleros" | "pasantias" | "trabajos-grado",
  id: number
) {
  return apiRequest<DesactivarRespuesta>(
    `/api/perfil/vinculaciones/${tipo}/${id}`,
    { method: "DELETE" }
  );
}
