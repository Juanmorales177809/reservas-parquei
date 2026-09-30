import Link from "next/link";

export interface EnlaceIndice {
  href: string;
  titulo: string;
  descripcion: string;
}

const ANILLO_FOCO =
  "focus-visible:outline-none focus-visible:ring-4 " +
  "focus-visible:ring-[color-mix(in_srgb,var(--color-sky)_55%,transparent)]";

/** Portada de un módulo del menú: lleva a sus pantallas, cada una con una línea que dice para qué sirve. */
export function IndiceModulo({
  titulo,
  introduccion,
  enlaces,
}: {
  titulo: string;
  introduccion?: string;
  enlaces: EnlaceIndice[];
}) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-1">
        <h1 className="font-display text-[1.85rem] font-bold leading-tight tracking-tight text-text">{titulo}</h1>
        {introduccion && <p className="max-w-[60ch] text-[15px] text-muted">{introduccion}</p>}
      </div>
      <ul className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {enlaces.map((e) => (
          <li key={e.href}>
            <Link
              href={e.href}
              className={`group flex h-full flex-col gap-1.5 rounded-card border border-border bg-surface p-5 shadow-card transition-[transform,border-color] duration-150 hover:-translate-y-0.5 hover:border-primary-1 ${ANILLO_FOCO}`}
            >
              <span className="font-display text-lg font-bold text-primary-2">{e.titulo}</span>
              <span className="text-sm text-muted">{e.descripcion}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
