/**
 * Formas del contrato de espacios (§2 a §4) compartidas entre servidor y
 * cliente. Sin `next/headers` — seguro para ambos lados, igual que
 * `auth-types.ts` de FE-07.
 */

export type TipoCampo = "TEXTO" | "TEXTO_LARGO" | "NUMERO" | "BOOLEANO" | "SELECCION";

export interface EspacioResumen {
  id: number;
  id_unidad: number;
  nombre: string;
  capacidad: number;
  habilitado: boolean;
}

export interface RecursoAsociado {
  recurso_id: number;
  nombre: string | null;
  habilitado: boolean;
}

export interface EspacioCampoOpcion {
  id: number;
  valor: string;
  orden: number;
  habilitado: boolean;
}

export interface EspacioCampoDetalle {
  id: number;
  nombre: string;
  tipo: string;
  obligatorio: boolean;
  orden: number;
  habilitado: boolean;
  opciones?: EspacioCampoOpcion[];
}

export interface EspacioDetalle extends EspacioResumen {
  ubicacion: string | null;
  descripcion: string | null;
  horario_unidad: { hora_apertura: string; hora_cierre: string } | null;
  recursos?: RecursoAsociado[];
  campos?: EspacioCampoDetalle[];
}

export interface ImpactoEspacio {
  reservas_a_cancelar: number;
}

export interface EstadoEspacio {
  id: number;
  habilitado: boolean;
  reservas_canceladas: number;
}

export interface CampoCrear {
  nombre: string;
  tipo: TipoCampo;
  obligatorio?: boolean;
  orden?: number;
  opciones?: { valor: string; orden?: number }[];
}
