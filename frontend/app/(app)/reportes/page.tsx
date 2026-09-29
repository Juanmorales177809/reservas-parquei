import { IndiceModulo } from "@/src/components/shell/IndiceModulo";

// Portada de reportes (specs/modules/reports/screen-flow.md): solo lleva a las tres pantallas.
export default function PaginaReportes() {
  return (
    <IndiceModulo
      titulo="Reportes"
      introduccion="Consultas de solo lectura sobre lo ya registrado. Cada una se puede exportar a CSV o Excel."
      enlaces={[
        { href: "/reportes/ocupacion", titulo: "Ocupación", descripcion: "Uso de laboratorios, espacios y recursos, u horas por proyecto o semillero." },
        { href: "/reportes/solicitudes", titulo: "Solicitudes", descripcion: "Reservas por estado en cada laboratorio." },
        { href: "/reportes/lista-espera", titulo: "Lista de espera", descripcion: "Reservas y horas de lista de espera por unidad." },
      ]}
    />
  );
}
