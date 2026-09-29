import { screen, within } from "@testing-library/react";
import type { UserEvent } from "@testing-library/user-event";

/** Elige una opción de un selector por su nombre visible (espera a que la lista cargue). */
export async function elegir(usuario: UserEvent, etiqueta: string, nombre: string) {
  const selector = await screen.findByLabelText(etiqueta);
  await within(selector).findByRole("option", { name: nombre });
  await usuario.selectOptions(selector, nombre);
}
