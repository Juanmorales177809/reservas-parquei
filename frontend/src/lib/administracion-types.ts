/**
 * Formas del contrato de administration (§2 a §5) compartidas entre
 * servidor y cliente. Sin `next/headers` — seguro para ambos lados, igual
 * que `auth-types.ts` de FE-07.
 */

export interface Unidad {
  id_unidad: number;
  nombre: string;
  tipo: string;
  id_unidad_padre: number | null;
  estado: boolean;
}

export interface Cargo {
  id_cargo: number;
  nombre_cargo: string;
  id_unidad: number;
}

export interface PermisoCatalogo {
  codigo: string;
  descripcion: string;
  ambito: string;
}

export interface Asignacion {
  id_cuenta: number;
  codigo: string;
  id_unidad: number | null;
}

export interface FilaImportacion {
  numero_fila: number;
  codigo: string | null;
  resultado: string;
  detalle: string | null;
}

export interface ValidacionImportacion {
  id: number;
  catalogo: string;
  id_unidad: number | null;
  confirmable: boolean;
  totales: { a_crear: number; a_actualizar: number; desactivados: number; con_error: number };
  resultados: FilaImportacion[];
}

export interface AuditoriaFila {
  id: number;
  actor_cuenta_id: number;
  entidad: string;
  entidad_id: string;
  accion: string;
  datos_anteriores: unknown;
  datos_nuevos: unknown;
  motivo: string | null;
  created_at: string;
}

/** Identidad con su cuenta (contratos/usuarios §5.2 y §6.2): sirve para elegir una cuenta por nombre. */
export interface IdentidadConCuenta {
  id_usuario?: number;
  id_persona?: number;
  id_cuenta: number | null;
  nombre: string;
  correo: string;
  estado: boolean;
}

/** Identidad de un usuario (contrato usuarios §5). */
export interface UsuarioIdentidad {
  id_usuario: number;
  id_cuenta: number | null;
  nombre: string;
  documento: string;
  telefono: string;
  institucion: string;
  dependencia: string;
  correo: string;
  estado: boolean;
}

/** Ficha de personal con su cargo y unidad (contrato usuarios §6). */
export interface FichaPersonal {
  id_persona: number;
  id_cuenta: number | null;
  nombre: string;
  documento: string;
  telefono: string;
  correo: string;
  estado: boolean;
  id_cargo: number;
  cargo: { id_cargo: number; nombre_cargo: string } | null;
  unidad: { id_unidad: number; nombre: string } | null;
}
