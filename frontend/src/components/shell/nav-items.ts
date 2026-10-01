import type { Rol } from "@/src/lib/auth-types";

/**
 * specs/ui/layout.md#navegación — los destinos del menú, en este orden. «Inicio» es el aterrizaje tras el
 * login para los tres roles (el Usuario solo ve accesos, sin sección de reportes); el resto sigue la regla
 * de roles fijos: el usuario solo reserva, el técnico gestiona su laboratorio y el administrador todo. Las
 * notificaciones ya no son un destino: viven en la campanita de la cabecera.
 */
export interface DestinoNav {
  href: string;
  etiqueta: string;
  /** Roles para los que aparece este destino (aproximación de grano grueso: ver layout.md). */
  roles: Rol[];
}

const TODOS_LOS_ROLES: Rol[] = ["USUARIO", "TECNICO", "ADMINISTRADOR"];
const QUIEN_GESTIONA: Rol[] = ["TECNICO", "ADMINISTRADOR"];

export const DESTINOS_NAV: DestinoNav[] = [
  { href: "/inicio", etiqueta: "Inicio", roles: TODOS_LOS_ROLES },
  { href: "/reservas", etiqueta: "Reservas", roles: TODOS_LOS_ROLES },
  { href: "/recursos", etiqueta: "Recursos", roles: QUIEN_GESTIONA },
  { href: "/espacios", etiqueta: "Espacios", roles: QUIEN_GESTIONA },
  // Todo `/api/investigacion/*` es del administrador: antes se ofrecía a todos y redirigía.
  { href: "/investigacion", etiqueta: "Investigación", roles: ["ADMINISTRADOR"] },
  { href: "/usuarios", etiqueta: "Usuarios", roles: ["ADMINISTRADOR"] },
  { href: "/administracion", etiqueta: "Administración", roles: ["ADMINISTRADOR"] },
  { href: "/reportes", etiqueta: "Reportes", roles: QUIEN_GESTIONA },
];

export function destinosVisiblesPara(rol: Rol): DestinoNav[] {
  return DESTINOS_NAV.filter((destino) => destino.roles.includes(rol));
}
