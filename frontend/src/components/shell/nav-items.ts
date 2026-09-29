import type { Rol } from "@/src/lib/auth";

/** specs/ui/layout.md#navegación — los ocho destinos, en este orden. */
export interface DestinoNav {
  href: string;
  etiqueta: string;
  /** Roles para los que aparece este destino (aproximación de grano grueso: ver layout.md). */
  roles: Rol[];
}

const TODOS_LOS_ROLES: Rol[] = ["USUARIO", "TECNICO", "ADMINISTRADOR"];

export const DESTINOS_NAV: DestinoNav[] = [
  { href: "/reservas", etiqueta: "Reservas", roles: TODOS_LOS_ROLES },
  { href: "/recursos", etiqueta: "Recursos", roles: TODOS_LOS_ROLES },
  { href: "/espacios", etiqueta: "Espacios", roles: TODOS_LOS_ROLES },
  { href: "/investigacion", etiqueta: "Investigación", roles: TODOS_LOS_ROLES },
  { href: "/usuarios", etiqueta: "Usuarios", roles: ["ADMINISTRADOR"] },
  { href: "/administracion", etiqueta: "Administración", roles: ["ADMINISTRADOR"] },
  { href: "/notificaciones", etiqueta: "Notificaciones", roles: TODOS_LOS_ROLES },
  { href: "/reportes", etiqueta: "Reportes", roles: ["TECNICO", "ADMINISTRADOR"] },
];

export function destinosVisiblesPara(rol: Rol): DestinoNav[] {
  return DESTINOS_NAV.filter((destino) => destino.roles.includes(rol));
}
