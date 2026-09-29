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
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl font-bold text-text">{titulo}</h1>
      {introduccion && <p className="text-sm text-muted">{introduccion}</p>}
      <ul className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {enlaces.map((e) => (
          <li key={e.href}>
            <Link
              href={e.href}
              className={`flex h-full flex-col gap-1 rounded-control border border-border bg-surface p-4 hover:bg-primary-tint ${ANILLO_FOCO}`}
            >
              <span className="text-base font-bold text-primary-2">{e.titulo}</span>
              <span className="text-sm text-muted">{e.descripcion}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
