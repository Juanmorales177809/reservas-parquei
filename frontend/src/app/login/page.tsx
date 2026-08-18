'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated, canManageResources, loading: authLoading } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.replace(canManageResources ? '/admin' : '/dashboard');
    }
  }, [isAuthenticated, canManageResources, authLoading, router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      // Fase 9F-B: no leemos el usuario de localStorage (ya no se
      // persiste ahí). El useEffect de arriba reacciona a isAuthenticated/
      // canManageResources en cuanto AuthContext actualiza su estado tras
      // el login y hace el redirect correcto.
      await login(username, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg bg-primary-600 text-lg font-bold text-white">
            IC
          </div>
          <h1 className="mt-4 text-2xl font-bold text-text-primary">Iniciar sesión</h1>
          <p className="mt-1 text-sm text-text-secondary">
            Ingresá tus credenciales para continuar
          </p>
        </div>

        <div className="card">
          {error && <div className="message-error mb-4">{error}</div>}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <label className="input-label">
              Usuario
              <input
                className="input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Tu nombre de usuario"
                required
                minLength={3}
                maxLength={80}
              />
            </label>

            <label className="input-label">
              Contraseña
              <input
                className="input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={6}
              />
            </label>

            <button className="btn btn-primary w-full justify-center" disabled={loading} type="submit">
              {loading ? 'Ingresando...' : 'Ingresar'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
