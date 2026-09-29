/**
 * El `{mensaje}` de wireframes.md: región de respuesta en la misma
 * pantalla, ausente cuando no hay mensaje. `aria-live` para que un lector
 * de pantalla anuncie el resultado sin mover el foco.
 */
export function RegionMensaje({
  texto,
  tono = "muted",
}: {
  texto: string | null;
  tono?: "muted" | "error" | "exito";
}) {
  if (!texto) return null;
  const color =
    tono === "error"
      ? "text-error-2"
      : tono === "exito"
        ? "text-success-2"
        : "text-muted";
  return (
    <p role="status" aria-live="polite" className={`text-sm ${color}`}>
      {texto}
    </p>
  );
}
