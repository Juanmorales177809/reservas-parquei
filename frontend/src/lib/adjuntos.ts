/** Tipos de archivo admitidos como adjunto de lista de espera (contrato reservations §2.5). */
export const EXTENSIONES_ADJUNTO: Record<string, "PLANO" | "IMAGEN" | "DOCUMENTO"> = {
  dwg: "PLANO",
  dxf: "PLANO",
  step: "PLANO",
  stp: "PLANO",
  stl: "PLANO",
  png: "IMAGEN",
  jpg: "IMAGEN",
  jpeg: "IMAGEN",
  pdf: "DOCUMENTO",
};

export const ACEPTA_ADJUNTOS = Object.keys(EXTENSIONES_ADJUNTO).map((e) => `.${e}`).join(",");
export const TAMANO_MAXIMO_ADJUNTO = 5 * 1024 * 1024;

export const NOMBRE_TIPO_ADJUNTO = { PLANO: "Plano", IMAGEN: "Imagen", DOCUMENTO: "Documento" } as const;

/** Tipo de adjunto según la extensión, o `null` si el formato no se admite. */
export function tipoAdjuntoDe(nombre: string): "PLANO" | "IMAGEN" | "DOCUMENTO" | null {
  const extension = nombre.split(".").pop()?.toLowerCase() ?? "";
  return EXTENSIONES_ADJUNTO[extension] ?? null;
}

/** Motivo por el que un archivo no puede subirse, o `null` si es válido. */
export function problemaAdjunto(archivo: File): string | null {
  if (!tipoAdjuntoDe(archivo.name))
    return `«${archivo.name}»: formato no admitido. Usa DWG, DXF, STEP, STL, PNG, JPG o PDF.`;
  if (archivo.size === 0) return `«${archivo.name}» está vacío.`;
  if (archivo.size > TAMANO_MAXIMO_ADJUNTO) return `«${archivo.name}» pesa más de 5 MB.`;
  return null;
}
