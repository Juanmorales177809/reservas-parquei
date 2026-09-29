import { IndiceModulo } from "@/src/components/shell/IndiceModulo";

export default function PaginaAdministracion() {
  return (
    <IndiceModulo
      titulo="Administración"
      introduccion="Estructura institucional, cuentas, permisos e importaciones."
      enlaces={[
        { href: "/administracion/unidades", titulo: "Unidades y cargos", descripcion: "Crear laboratorios y dependencias, y los cargos de cada una. Desde aquí se configura cada laboratorio." },
        { href: "/administracion/personas", titulo: "Personas", descripcion: "Consultar, editar y activar o desactivar usuarios y personal." },
        { href: "/administracion/identidades", titulo: "Identidades e invitaciones", descripcion: "Registrar usuarios y personal e invitarlos a crear su cuenta." },
        { href: "/administracion/permisos", titulo: "Permisos", descripcion: "Otorgar y retirar permisos administrativos a una cuenta." },
        { href: "/administracion/importaciones", titulo: "Importaciones", descripcion: "Cargar proyectos, semilleros y equipos desde una planilla." },
        { href: "/administracion/auditoria", titulo: "Auditoría", descripcion: "Consultar quién hizo qué en las operaciones administrativas." },
      ]}
    />
  );
}
