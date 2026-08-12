export interface AuthUser {
  id: number;
  username: string;
  email: string;
  rol: 'admin' | 'gestor' | 'usuario';
  espacio: {
    id: number;
    nombre: string;
    ubicacion: string;
  } | null;
}
