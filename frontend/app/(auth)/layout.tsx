import type { ReactNode } from "react";

// Las pantallas públicas comparten una portada de marca: a la izquierda, para qué sirve el sistema;
// a la derecha, el formulario. En pantallas angostas solo queda el formulario.
export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen bg-bg">
      <aside className="hidden w-[42%] max-w-[560px] flex-col justify-between bg-ink p-12 lg:flex">
        <div className="flex items-center gap-3">
          <span
            aria-hidden="true"
            className="flex h-10 w-10 items-center justify-center rounded-control bg-primary-1 font-display text-xl font-bold text-white"
          >
            R
          </span>
          <span className="font-display text-lg font-bold text-white">Reservas Parquei</span>
        </div>
        <div className="flex flex-col gap-4">
          <p className="font-display text-[2.4rem] font-bold leading-[1.1] tracking-tight text-white">
            Reserva el laboratorio, el espacio o el equipo que necesitas.
          </p>
          <p className="max-w-[38ch] text-[15px] text-ink-text">
            Pide un cupo, sigue su aprobación y recibe el aviso cuando cambie de estado.
          </p>
        </div>
        <p className="text-sm text-ink-text">Parque i · Instituto Tecnológico Metropolitano</p>
      </aside>
      <div className="flex flex-1 items-center justify-center px-5 py-11">{children}</div>
    </div>
  );
}
