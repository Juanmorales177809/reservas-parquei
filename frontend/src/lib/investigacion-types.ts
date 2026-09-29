/**
 * Formas del contrato de researchs (§2 a §5) compartidas entre servidor y
 * cliente. Sin `next/headers` — seguro para ambos lados, igual que
 * `auth-types.ts` de FE-07.
 */

export interface Proyecto {
  id_proyecto: number;
  codigo: string;
  nombre: string;
  estado: boolean;
}

export interface Semillero {
  id_semillero: number;
  codigo: string;
  nombre: string;
  estado: boolean;
}

export interface Actividad {
  id_actividad: number;
  nombre: string;
  dependencia: string;
  estado: boolean;
}

export interface PerfilInv {
  id_perfil: number;
  nombre: string;
  descripcion: string | null;
  estado: boolean;
}

export interface VinculacionAjenas {
  proyectos: { id_proyecto: number; codigo: string; nombre: string; activa: boolean }[];
  semilleros: { id_semillero: number; codigo: string; nombre: string; activa: boolean }[];
  pasantias: { id_pasantia: number; universidad: string; activa: boolean }[];
  trabajos_grado: { id_trabajo_grado: number; activa: boolean }[];
}
