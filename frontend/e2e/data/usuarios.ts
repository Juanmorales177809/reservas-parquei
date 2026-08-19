// Credenciales FICTICIAS de prueba. No son secretos reales; solo existen
// dentro del entorno local de pruebas (ver playwright.config.ts y README).

export type RolUsuario = 'admin' | 'gestor' | 'usuario';

export interface UsuarioPrueba {
  username: string;
  email: string;
  password: string;
  rol: RolUsuario;
}

export const USUARIOS: Record<RolUsuario, UsuarioPrueba> = {
  admin: {
    username: 'e2e-admin',
    email: 'e2e-admin@example.com',
    password: 'E2e-Admin-123!',
    rol: 'admin',
  },
  gestor: {
    username: 'e2e-gestor',
    email: 'e2e-gestor@example.com',
    password: 'E2e-Gestor-123!',
    rol: 'gestor',
  },
  usuario: {
    username: 'e2e-usuario',
    email: 'e2e-usuario@example.com',
    password: 'E2e-Usuario-123!',
    rol: 'usuario',
  },
};

/** Fecha futura en formato YYYY-MM-DD que supera la anticipación de 24 h y
 *  evita el domingo (sin horario de atención por defecto).
 *  `intento` desplaza la fecha para que los reintentos de Playwright no
 *  colisionen con reservas creadas por el intento anterior del mismo test. */
export function fechaFutura(diasAdelante = 8, intento = 0): string {
  const fecha = new Date();
  fecha.setDate(fecha.getDate() + diasAdelante + intento * 20);
  while (fecha.getDay() === 0) fecha.setDate(fecha.getDate() + 1);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${fecha.getFullYear()}-${pad(fecha.getMonth() + 1)}-${pad(fecha.getDate())}`;
}

/** Próximo domingo en formato YYYY-MM-DD (día sin atención por defecto). */
export function proximoDomingo(): string {
  const fecha = new Date();
  while (fecha.getDay() !== 0) fecha.setDate(fecha.getDate() + 1);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${fecha.getFullYear()}-${pad(fecha.getMonth() + 1)}-${pad(fecha.getDate())}`;
}

/** Sufijo único para nombres de datos de prueba (sin dependencia de orden). */
export function sufijoUnico(): string {
  return `${Date.now()}`;
}
