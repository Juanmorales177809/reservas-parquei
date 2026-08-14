'use client';

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { AdminDashboardSummary } from '@/types/admin-dashboard';

const COLORES_ESTADO = ['#f59e0b', '#22c55e', '#ef4444', '#94a3b8'];
const COLORES_OCUPACION = ['#0891b2', '#e2e8f0'];
const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
const HORAS = Array.from({ length: 13 }, (_, index) => index + 7);

function EmptyChart({ message }: { message: string }) {
  return (
    <div className="flex h-72 items-center justify-center text-center text-sm text-text-muted">
      {message}
    </div>
  );
}

function intensidad(cantidad: number, maximo: number): string {
  if (cantidad === 0 || maximo === 0) return '#f1f5f9';
  const alpha = 0.2 + (cantidad / maximo) * 0.8;
  return `rgba(8, 145, 178, ${alpha})`;
}

export default function AdminDashboardCharts({
  summary,
  showSpaces = false,
}: {
  summary: AdminDashboardSummary;
  showSpaces?: boolean;
}) {
  const estados = [
    { nombre: 'Pendientes', cantidad: summary.reservas_por_estado.pendientes },
    { nombre: 'Aprobadas', cantidad: summary.reservas_por_estado.aprobadas },
    { nombre: 'Rechazadas', cantidad: summary.reservas_por_estado.rechazadas },
    { nombre: 'Canceladas', cantidad: summary.reservas_por_estado.canceladas },
  ];
  const tieneEstados = estados.some((item) => item.cantidad > 0);
  const fechas = summary.reservas_por_fecha.slice(-30).map((item) => ({
    ...item,
    etiqueta: new Date(`${item.fecha}T00:00:00`).toLocaleDateString('es', {
      day: '2-digit',
      month: 'short',
    }),
  }));
  const maxOcupacion = Math.max(0, ...summary.ocupacion_por_dia_hora.map((item) => item.cantidad));
  const ocupacion = new Map(
    summary.ocupacion_por_dia_hora.map((item) => [`${item.dia_orden}-${item.hora}`, item.cantidad]),
  );
  const ocupacionGlobal = [
    { nombre: 'Ocupadas', cantidad: summary.ocupacion_global.horas_ocupadas },
    {
      nombre: 'Disponibles',
      cantidad: Math.max(
        0,
        summary.ocupacion_global.horas_disponibles - summary.ocupacion_global.horas_ocupadas,
      ),
    },
  ];

  return (
    <section className="mb-8" aria-labelledby="dashboard-charts-title">
      <h2 id="dashboard-charts-title" className="mb-4 text-xl font-semibold text-text-primary">
        Análisis de reservas
      </h2>

      <div className="grid gap-4 lg:grid-cols-2">
        {showSpaces && (
          <>
            <article className="card">
              <h3 className="mb-1 font-semibold text-text-primary">Ocupación global</h3>
              <p className="mb-4 text-sm text-text-muted">
                Horas reservadas en todos los recursos y espacios.
              </p>
              {summary.ocupacion_global.horas_disponibles === 0 ? (
                <EmptyChart message="No hay ocupación registrada." />
              ) : (
                <div className="relative h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={ocupacionGlobal}
                        dataKey="cantidad"
                        nameKey="nombre"
                        innerRadius={65}
                        outerRadius={95}
                      >
                        {ocupacionGlobal.map((item, index) => (
                          <Cell key={item.nombre} fill={COLORES_OCUPACION[index]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [`${Number(value).toFixed(1)} h`, 'Horas']} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="pointer-events-none absolute inset-0 flex items-center justify-center pb-7">
                    <div className="text-center">
                      <p className="text-3xl font-bold text-primary-600">
                        {summary.ocupacion_global.porcentaje}%
                      </p>
                      <p className="text-xs text-text-muted">ocupación</p>
                    </div>
                  </div>
                </div>
              )}
            </article>

            <article className="card">
              <h3 className="mb-1 font-semibold text-text-primary">Reservas por espacio</h3>
              <p className="mb-4 text-sm text-text-muted">
                Incluye las reservas de todos los recursos de cada espacio.
              </p>
              {summary.reservas_por_espacio.length === 0 ? (
                <EmptyChart message="No hay espacios con reservas." />
              ) : (
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={summary.reservas_por_espacio}
                      layout="vertical"
                      margin={{ top: 8, right: 20, left: 40, bottom: 8 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis type="number" allowDecimals={false} />
                      <YAxis type="category" dataKey="nombre" width={180} tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <Bar dataKey="cantidad" name="Reservas de recursos" fill="#6366f1" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </article>
          </>
        )}

        <article className="card">
          <h3 className="mb-4 font-semibold text-text-primary">Reservas por estado</h3>
          {!tieneEstados ? (
            <EmptyChart message="No hay reservas para representar." />
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={estados} dataKey="cantidad" nameKey="nombre" innerRadius={55} outerRadius={90}>
                    {estados.map((item, index) => (
                      <Cell key={item.nombre} fill={COLORES_ESTADO[index]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </article>

        <article className="card">
          <h3 className="mb-4 font-semibold text-text-primary">Reservas por fecha</h3>
          {fechas.length === 0 ? (
            <EmptyChart message="No hay fechas con reservas." />
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={fechas} margin={{ top: 8, right: 12, left: -20, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="etiqueta" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="cantidad" name="Reservas" stroke="#0891b2" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </article>

        <article className="card lg:col-span-2">
          <h3 className="mb-4 font-semibold text-text-primary">Recursos más reservados</h3>
          {summary.recursos_mas_reservados.length === 0 ? (
            <EmptyChart message="No hay recursos con reservas." />
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={summary.recursos_mas_reservados}
                  layout="vertical"
                  margin={{ top: 8, right: 20, left: 40, bottom: 8 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis type="number" allowDecimals={false} />
                  <YAxis type="category" dataKey="nombre" width={150} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="cantidad" name="Reservas" fill="#0891b2" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </article>

        <article className="card overflow-hidden lg:col-span-2">
          <h3 className="mb-1 font-semibold text-text-primary">Ocupación por día y hora</h3>
          <p className="mb-4 text-sm text-text-muted">
            Heatmap visual: 07:00–19:00. El porcentaje global considera el horario completo
            configurado.
          </p>
          {maxOcupacion === 0 ? (
            <EmptyChart message="No hay ocupación registrada." />
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-[820px] border-separate border-spacing-1 text-center text-xs">
                <thead>
                  <tr>
                    <th className="px-2 py-2 text-left">Día</th>
                    {HORAS.map((hora) => (
                      <th key={hora} className="px-2 py-2 font-medium">{`${hora}:00`}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {DIAS.map((dia, diaIndex) => (
                    <tr key={dia}>
                      <th className="whitespace-nowrap px-2 py-2 text-left font-medium">{dia}</th>
                      {HORAS.map((hora) => {
                        const cantidad = ocupacion.get(`${diaIndex}-${hora}`) ?? 0;
                        return (
                          <td
                            key={hora}
                            className={`h-9 min-w-10 rounded ${cantidad > 0 ? 'text-white' : 'text-text-muted'}`}
                            style={{ backgroundColor: intensidad(cantidad, maxOcupacion) }}
                            title={`${dia} ${hora}:00: ${cantidad} reserva${cantidad === 1 ? '' : 's'}`}
                          >
                            {cantidad}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </article>
      </div>
    </section>
  );
}
