import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SeccionVinculaciones } from "@/src/components/usuarios/SeccionVinculaciones";
import type { Vinculaciones } from "@/src/lib/usuarios-types";

const desactivarMock = vi.fn();
const perfilMock = vi.fn();

vi.mock("@/src/lib/usuarios-api", async () => {
  const actual = await vi.importActual<typeof import("@/src/lib/usuarios-api")>(
    "@/src/lib/usuarios-api"
  );
  return {
    ...actual,
    desactivarVinculacion: (...args: unknown[]) => desactivarMock(...args),
    obtenerPerfil: () => perfilMock(),
  };
});

const VACIAS: Vinculaciones = { proyectos: [], semilleros: [], pasantias: [], trabajos_grado: [] };

// FE-09 (WF-USR-05, RN-USR-11): desactivar la última avisa del bloqueo.
describe("SeccionVinculaciones", () => {
  beforeEach(() => {
    desactivarMock.mockReset();
    perfilMock.mockReset();
  });

  it("desactivar la última vinculación muestra el aviso de bloqueo", async () => {
    const usuario = userEvent.setup();
    const iniciales: Vinculaciones = {
      ...VACIAS,
      proyectos: [{ id_proyecto: 12, codigo: "PRY-001", nombre: "Ensayos", activa: true }],
    };
    desactivarMock.mockResolvedValue({ sin_vinculaciones_activas: true });
    perfilMock.mockResolvedValue({ vinculaciones: VACIAS });

    render(
      <SeccionVinculaciones iniciales={iniciales} permiteDesactivar={true} alCambiar={() => {}} />
    );
    await usuario.click(screen.getByRole("button", { name: "Desactivar" }));
    await waitFor(() => {
      expect(desactivarMock).toHaveBeenCalledWith("proyectos", 12);
    });
    expect(
      await screen.findByText(/no podrás crear nuevas reservas/i)
    ).toBeInTheDocument();
  });
});
