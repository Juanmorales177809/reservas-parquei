/** Fecha y hora legibles (hora local de quien mira); si no es una fecha válida devuelve el texto tal cual. */
export function fechaHora(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" });
}
