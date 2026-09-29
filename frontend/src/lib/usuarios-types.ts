/**
 * Formas del contrato de usuarios (§2 a §4) compartidas entre servidor y
 * cliente. Sin `next/headers` — seguro para ambos lados, igual que
 * `auth-types.ts` de FE-07.
 */

export interface PerfilVinculado {
  id_perfil: number;
  nombre: string;
}

export interface VinculacionProyecto {
  id_proyecto: number;
  codigo: string;
  nombre: string;
  activa: boolean;
}

export interface VinculacionSemillero {
  id_semillero: number;
  codigo: string;
  nombre: string;
  activa: boolean;
}

export interface VinculacionPasantia {
  id_pasantia: number;
  universidad: string;
  docente_itm_nombre?: string;
  docente_itm_correo?: string;
  activa: boolean;
}

export interface VinculacionTrabajoGrado {
  id_trabajo_grado: number;
  director_nombre?: string;
  director_correo?: string;
  activa: boolean;
}

export interface Vinculaciones {
  proyectos: VinculacionProyecto[];
  semilleros: VinculacionSemillero[];
  pasantias: VinculacionPasantia[];
  trabajos_grado: VinculacionTrabajoGrado[];
}

export interface Perfil {
  id_usuario: number;
  nombre: string;
  documento: string;
  telefono: string;
  institucion: string;
  dependencia: string;
  correo: string;
  actualizacion_inicial_pendiente: boolean;
  perfil_actualizado_at: string | null;
  perfiles: PerfilVinculado[];
  vinculaciones: Vinculaciones;
}

export interface PerfilCatalogoItem {
  id_perfil: number;
  nombre: string;
}

export interface CatalogoEntidad {
  id: number;
  codigo: string;
  nombre: string;
}

export interface ConfirmacionInicial {
  perfil_actualizado_at: string;
  actualizacion_inicial_pendiente: false;
}

export interface DesactivarRespuesta {
  sin_vinculaciones_activas: boolean;
}
