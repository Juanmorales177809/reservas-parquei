import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import PaginaAuditoria from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

const listarMock = vi.fn();

vi.mock("@/src/lib/administracion-api", () => ({
  listarAuditoria: (...args: unknown[]) => listarMock(...args),
}));

// FE-11 (WF-ADM-05, SEC-AUD-03): la vista jamás expone secretos.
describe("administracion/auditoria/page.tsx", () => {
  beforeEach(() => {
    listarMock.mockReset();
    listarMock.mockResolvedValue({
      datos: [
        {
          id: 4471,
          actor_cuenta_id: 1042,
          entidad: "auth.cuenta_permisos",
          entidad_id: "310",
          accion: "ASIGNAR_PERMISO",
          datos_anteriores: null,
          datos_nuevos: { codigo: "reservas.administrar", id_unidad: 7 },
          motivo: null,
          created_at: "2026-09-23T11:04:02Z",
        },
      ],
    });
  });

  it("muestra actor, acción y entidad sin secretos", async () => {
    const { container } = render(<PaginaAuditoria />);
    expect(await screen.findByText(/ASIGNAR_PERMISO/)).toBeInTheDocument();
    expect(await screen.findByText(/auth\.cuenta_permisos/)).toBeInTheDocument();
    const texto = (container.textContent ?? "").toLowerCase();
    for (const prohibida of ["password", "contraseña", "token", "hash", "secret"]) {
      expect(texto).not.toContain(prohibida);
    }
  });
});
