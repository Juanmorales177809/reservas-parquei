import { IndiceModulo } from "@/src/components/shell/IndiceModulo";

export default function PaginaInvestigacion() {
  return (
    <IndiceModulo
      titulo="Investigación"
      introduccion="Catálogos de contexto académico e investigativo con los que se justifica cada reserva."
      enlaces={[
        { href: "/investigacion/proyectos", titulo: "Proyectos y semilleros", descripcion: "Consultar el catálogo y habilitar o deshabilitar cada entrada. Se cargan por importación." },
        { href: "/investigacion/actividades", titulo: "Actividades institucionales", descripcion: "Crear y administrar las actividades que pueden justificar una reserva." },
        { href: "/investigacion/perfiles", titulo: "Perfiles académicos", descripcion: "Administrar el catálogo de perfiles que los usuarios pueden elegir." },
        { href: "/investigacion/vinculaciones", titulo: "Vinculaciones de usuarios", descripcion: "Ver y gestionar las vinculaciones de cualquier usuario." },
      ]}
    />
  );
}
