import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="border-t border-border bg-surface-card">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary-600 text-[10px] font-bold text-white">
              IC
            </div>
            <span className="text-sm font-semibold text-text-primary">Reservas IC</span>
          </div>
          <div className="flex gap-6">
            <Link href="/espacios" className="text-sm text-text-muted hover:text-primary-600 transition-colors">
              Recursos
            </Link>
            <Link href="/login" className="text-sm text-text-muted hover:text-primary-600 transition-colors">
              Iniciar sesión
            </Link>
          </div>
          <p className="text-xs text-text-muted">
            &copy; {new Date().getFullYear()} Reservas IC. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </footer>
  );
}
