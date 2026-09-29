"use client";

import {
  forwardRef,
  useEffect,
  useRef,
  useState,
  type ButtonHTMLAttributes,
  type ReactNode,
} from "react";

/**
 * specs/ui/components.md#botones — siete variantes, tres tamaños,
 * fullWidth y los seis estados fijos (default/hover/pressed/focus-visible/
 * disabled/loading). destructiveConfirm añade su propio patrón de doble
 * confirmación (specs/ui/components.md#caso-especial-destructive-confirm).
 */
export type ButtonVariant =
  | "primary"
  | "secondary"
  | "success"
  | "danger"
  | "warning"
  | "ghost"
  | "destructiveConfirm";

export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps
  extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "children"> {
  variant: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  /** Antepone el spinner sin perder el texto; deshabilita el botón funcionalmente. */
  loading?: boolean;
  children: ReactNode;
  /** Solo con `variant="destructiveConfirm"`: texto mientras el botón está armado. */
  confirmLabel?: string;
}

const ARMED_WINDOW_MS = 4000;

/**
 * Transición completa de design-tokens.md ("Otros valores reutilizables"),
 * con su duración y easing por propiedad — no se tokenizó en FE-02 porque
 * es específica de Button, no transversal.
 */
const TRANSITION =
  "[transition:box-shadow_.18s_ease,transform_.08s_ease,background-color_.18s_ease,opacity_.15s_ease]";

const BASE_CLASSES = [
  "inline-flex items-center justify-center gap-2",
  "rounded-control font-display font-bold",
  TRANSITION,
  "disabled:!bg-none disabled:!bg-disabled-bg disabled:!text-disabled-text disabled:!shadow-none disabled:cursor-not-allowed",
  "focus-visible:outline-none focus-visible:ring-4",
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]",
].join(" ");

const SIZE_CLASSES: Record<ButtonSize, string> = {
  sm: "h-[34px] px-4 text-[12.5px]",
  md: "h-11 px-[22px] text-[14px]",
  lg: "h-[52px] px-7 text-[15.5px]",
};

/**
 * Cada variante de relleno sólido cambia el segundo extremo del degradado en
 * hover (`-hover-2`) salvo `primary`, que también tiene `-hover-1` propio —
 * es la única familia con ambos tokens (ver design-tokens.md#colores).
 */
const VARIANT_CLASSES: Record<ButtonVariant, string> = {
  primary:
    "uppercase tracking-wide text-white " +
    "bg-gradient-to-br from-primary-1 to-primary-2 shadow-default " +
    "hover:from-primary-hover1 hover:to-primary-hover2 hover:shadow-hover " +
    "active:translate-y-px active:bg-none active:bg-primary-pressed active:shadow-pressed",
  secondary:
    "bg-primary-tint text-primary-2 " +
    "hover:bg-[color-mix(in_srgb,var(--color-primary-tint)_60%,var(--color-primary-1)_15%)] " +
    "active:translate-y-px active:bg-[color-mix(in_srgb,var(--color-primary-tint)_40%,var(--color-primary-1)_25%)]",
  success:
    "text-white bg-gradient-to-br from-success-1 to-success-2 shadow-default " +
    "hover:to-success-hover2 hover:shadow-hover " +
    "active:translate-y-px active:bg-none active:bg-success-pressed active:shadow-pressed",
  danger:
    "text-white bg-gradient-to-br from-error-1 to-error-2 shadow-default " +
    "hover:to-error-hover2 hover:shadow-hover " +
    "active:translate-y-px active:bg-none active:bg-error-pressed active:shadow-pressed",
  warning:
    "text-white bg-gradient-to-br from-warning-1 to-warning-2 shadow-default " +
    "hover:to-warning-hover2 hover:shadow-hover " +
    "active:translate-y-px active:bg-none active:bg-warning-pressed active:shadow-pressed",
  ghost:
    "font-bold text-muted bg-transparent " +
    "hover:bg-primary-tint hover:text-primary-2 " +
    "active:translate-y-px active:bg-[color-mix(in_srgb,var(--color-primary-tint)_60%,var(--color-primary-1)_10%)] active:text-primary-2",
  destructiveConfirm:
    "text-white bg-gradient-to-br from-error-1 to-error-2 shadow-default " +
    "hover:to-error-hover2 hover:shadow-hover " +
    "active:translate-y-px active:bg-none active:bg-error-pressed active:shadow-pressed " +
    // Armado: color sólido + anillo de foco siempre visible, no solo con :focus-visible.
    "data-[armed=true]:bg-none data-[armed=true]:bg-error-pressed " +
    "data-[armed=true]:ring-4 data-[armed=true]:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]",
};

function Spinner() {
  return (
    <span
      aria-hidden="true"
      className="h-3.5 w-3.5 flex-none animate-spin rounded-full border-[2.5px] border-[color-mix(in_srgb,currentColor_40%,transparent)] border-t-current"
    />
  );
}

function cx(...classes: Array<string | false | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  function Button(
    {
      variant,
      size = "md",
      fullWidth = false,
      loading = false,
      confirmLabel,
      children,
      disabled,
      type = "button",
      className,
      onClick,
      ...rest
    },
    ref
  ) {
    const [armed, setArmed] = useState(false);
    const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    useEffect(() => {
      return () => {
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
      };
    }, []);

    const isDestructiveConfirm = variant === "destructiveConfirm";
    const isDisabled = disabled || loading;

    function handleClick(event: React.MouseEvent<HTMLButtonElement>) {
      if (!isDestructiveConfirm) {
        onClick?.(event);
        return;
      }

      if (!armed) {
        setArmed(true);
        timeoutRef.current = setTimeout(() => {
          setArmed(false);
          timeoutRef.current = null;
        }, ARMED_WINDOW_MS);
        return;
      }

      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      setArmed(false);
      onClick?.(event);
    }

    return (
      <button
        {...rest}
        ref={ref}
        type={type}
        disabled={isDisabled}
        onClick={handleClick}
        data-armed={isDestructiveConfirm ? (armed ? "true" : "false") : undefined}
        className={cx(
          BASE_CLASSES,
          SIZE_CLASSES[size],
          VARIANT_CLASSES[variant],
          fullWidth && "w-full",
          className
        )}
      >
        {loading && <Spinner />}
        {isDestructiveConfirm && armed ? confirmLabel ?? "¿Confirmar?" : children}
      </button>
    );
  }
);
