export interface ControlCambio {
  id: number;
  usuario_id: number | null;
  usuario: string;
  accion: string;
  entidad: string;
  entidad_id: number | null;
  descripcion: string;
  created_at: string;
}
