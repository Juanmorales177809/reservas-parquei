import { IndiceModulo } from "@/src/components/shell/IndiceModulo";

export default function PaginaAdministracion() {
  return (
    <IndiceModulo
      titulo="Administración"
      introduccion="Estructura institucional, cuentas e importaciones."
      enlaces={[
        { href: "/administracion/unidades", titulo: "Laboratorios y cargos", descripcion: "Consulta los laboratorios y sus cargos, que llegan de la base institucional. Desde aquí se configura cada laboratorio." },
        { href: "/administracion/personas", titulo: "Personas", descripcion: "Consultar, editar y activar o desactivar usuarios y personal." },
        { href: "/administracion/identidades", titulo: "Identidades e invitaciones", descripcion: "Registrar usuarios e invitarlos a crear su cuenta." },
        { href: "/administracion/importaciones", titulo: "Importaciones", descripcion: "Cargar proyectos, semilleros y equipos desde una planilla." },
        { href: "/administracion/auditoria", titulo: "Auditoría", descripcion: "Consultar quién hizo qué en las operaciones administrativas." },
      ]}
    />
  );
}
