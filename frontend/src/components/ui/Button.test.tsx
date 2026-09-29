import { act, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Button } from "./Button";

describe("Button", () => {
  it("renderiza el texto de las siete variantes", () => {
    const variants: Array<Parameters<typeof Button>[0]["variant"]> = [
      "primary",
      "secondary",
      "success",
      "danger",
      "warning",
      "ghost",
      "destructiveConfirm",
    ];
    for (const variant of variants) {
      render(
        <Button variant={variant}>{`Texto ${variant}`}</Button>
      );
    }
    for (const variant of variants) {
      expect(screen.getByText(`Texto ${variant}`)).toBeInTheDocument();
    }
  });

  it("aplica fullWidth como ancho completo", () => {
    render(
      <Button variant="primary" fullWidth>
        Reservar
      </Button>
    );
    expect(screen.getByRole("button", { name: "Reservar" }).className).toMatch(
      /\bw-full\b/
    );
  });

  it("disabled usa el atributo nativo y bloquea el clic", async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(
      <Button variant="primary" disabled onClick={onClick}>
        Reservar
      </Button>
    );
    const boton = screen.getByRole("button", { name: "Reservar" });
    expect(boton).toBeDisabled();

    await user.click(boton);
    expect(onClick).not.toHaveBeenCalled();
  });

  it("loading antepone el spinner sin perder el texto y deshabilita el botón", () => {
    render(
      <Button variant="primary" loading>
        Reservar
      </Button>
    );
    const boton = screen.getByRole("button", { name: "Reservar" });
    expect(boton).toBeDisabled();
    expect(boton.querySelector('[aria-hidden="true"]')).not.toBeNull();
    expect(boton).toHaveTextContent("Reservar");
  });

  describe("destructiveConfirm", () => {
    afterEach(() => {
      vi.useRealTimers();
    });

    it("arma con el primer clic sin ejecutar la acción", async () => {
      const user = userEvent.setup();
      const onClick = vi.fn();
      render(
        <Button
          variant="destructiveConfirm"
          confirmLabel="¿Confirmar cancelación?"
          onClick={onClick}
        >
          Cancelar reserva
        </Button>
      );
      const boton = screen.getByRole("button", { name: "Cancelar reserva" });

      await user.click(boton);

      expect(onClick).not.toHaveBeenCalled();
      expect(boton).toHaveAttribute("data-armed", "true");
      expect(screen.getByText("¿Confirmar cancelación?")).toBeInTheDocument();
    });

    it("ejecuta la acción con el segundo clic dentro de la ventana y se desarma", async () => {
      const user = userEvent.setup();
      const onClick = vi.fn();
      render(
        <Button variant="destructiveConfirm" onClick={onClick}>
          Cancelar reserva
        </Button>
      );
      const boton = screen.getByRole("button");

      await user.click(boton);
      await user.click(boton);

      expect(onClick).toHaveBeenCalledTimes(1);
      expect(boton).toHaveAttribute("data-armed", "false");
      expect(screen.getByText("Cancelar reserva")).toBeInTheDocument();
    });

    it("se desarma solo pasados los 4s sin ejecutar la acción", () => {
      vi.useFakeTimers();
      const onClick = vi.fn();
      render(
        <Button variant="destructiveConfirm" onClick={onClick}>
          Cancelar reserva
        </Button>
      );
      const boton = screen.getByRole("button");

      fireEvent.click(boton);
      expect(boton).toHaveAttribute("data-armed", "true");

      act(() => {
        vi.advanceTimersByTime(3999);
      });
      expect(boton).toHaveAttribute("data-armed", "true");

      act(() => {
        vi.advanceTimersByTime(1);
      });
      expect(boton).toHaveAttribute("data-armed", "false");
      expect(onClick).not.toHaveBeenCalled();
    });
  });
});
