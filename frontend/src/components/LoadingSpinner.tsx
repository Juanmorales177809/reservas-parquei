export default function LoadingSpinner({ text = 'Cargando...' }: { text?: string }) {
  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-border border-t-primary-600" />
      <p className="text-sm text-text-muted">{text}</p>
    </div>
  );
}
