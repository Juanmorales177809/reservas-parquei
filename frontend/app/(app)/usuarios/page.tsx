import { redirect } from "next/navigation";
import { IndiceModulo } from "@/src/components/shell/IndiceModulo";
import { obtenerSesionActual } from "@/src/lib/auth";

export default async function PaginaUsuarios() {
  const sesion = await obtenerSesionActual();
  if (!sesion) redirect("/login?motivo=sesion_vencida");
  return (
    <IndiceModulo
      titulo="Usuarios"
      introduccion="Personas que reservan y personal institucional."
      enlaces={[
        { href: "/administracion/personas", titulo: "Personas", descripcion: "Consultar, editar y activar o desactivar usuarios y personal." },
        { href: "/administracion/identidades", titulo: "Identidades e invitaciones", descripcion: "Registrar usuarios y personal e invitarlos a crear su cuenta." },
        { href: "/investigacion/vinculaciones", titulo: "Vinculaciones de usuarios", descripcion: "Ver y gestionar las vinculaciones académicas o investigativas de un usuario." },
        { href: "/usuarios/perfil", titulo: "Mi perfil", descripcion: "Mis datos personales, perfiles y vinculaciones." },
      ]}
    />
  );
}
