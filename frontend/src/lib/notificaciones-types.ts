/**
 * Formas del contrato de notifications (§2 y §3) compartidas entre servidor
 * y cliente. Sin `next/headers` — seguro para ambos lados, igual que
 * `auth-types.ts` de FE-07.
 */

export interface TipoEventoRef {
  codigo: string;
  nombre: string;
}

export interface NotificacionItem {
  id: number;
  tipo_evento: TipoEventoRef;
  titulo: string;
  cuerpo: string;
  reserva_id: number | null;
  leida_at: string | null;
  created_at: string;
}

export interface LecturaRespuesta {
  id: number;
  leida_at: string;
}

export interface TipoEventoItem {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string | null;
}

export interface PreferenciaEvento {
  tipo_evento: TipoEventoRef;
  correo_habilitado: boolean;
}

export interface Preferencias {
  general: { correo_habilitado: boolean };
  por_evento: PreferenciaEvento[];
}
