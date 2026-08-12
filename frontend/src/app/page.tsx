'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Footer from '@/components/Footer';
import LoadingSpinner from '@/components/LoadingSpinner';
import { useAuth } from '@/context/AuthContext';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, canManageResources, loading } = useAuth();

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.replace(canManageResources ? '/admin' : '/dashboard');
    }
  }, [isAuthenticated, canManageResources, loading, router]);

  if (loading || isAuthenticated) {
    return <LoadingSpinner text="Redirigiendo..." />;
  }

  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
              Reserva de recursos laboratorios de Investigación.
            </h1>
            <p className="mt-4 text-lg text-primary-100">
              Reserve aquí los recursos de Laboratorios que requieras para adelantar tu investigación.
            </p>
            <div className="mt-8 flex items-center justify-center gap-4">
              <Link href="/login" className="btn border-2 border-white/40 text-white hover:bg-white/10">
                Iniciar sesión
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-xl text-center">
          <h2 className="text-2xl font-bold text-text-primary sm:text-3xl">
            Gestión de reservas institucionales
          </h2>
          <p className="mt-2 text-text-secondary">
            Una plataforma simple para gestionar reservas institucionales.
          </p>
        </div>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[
            {
              title: 'Reservá recursos',
              desc: 'Elegí fecha, horario y recurso en simples pasos. Consultá disponibilidad en tiempo real.',
              icon: (
                <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
                </svg>
              ),
            },
            {
              title: 'Seguimiento',
              desc: 'Consultá el estado de tus reservas: aprobadas, pendientes o rechazadas desde tu panel.',
              icon: (
                <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15a2.25 2.25 0 012.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
                </svg>
              ),
            },
            {
              title: 'Administración',
              desc: 'Administradores y gestores controlan recursos y aprueban o rechazan solicitudes.',
              icon: (
                <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                </svg>
              ),
            },
          ].map((feature) => (
            <div key={feature.title} className="card">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-50">
                {feature.icon}
              </div>
              <h3 className="mt-4 font-semibold text-text-primary">{feature.title}</h3>
              <p className="mt-1 text-sm text-text-secondary">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-border bg-surface-card">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="grid gap-8 text-center sm:grid-cols-3">
            {[
              { label: 'Recursos disponibles', value: 'Múltiples' },
              { label: 'Reservas gestionadas', value: 'Todas' },
              { label: 'Gestión simple', value: '100%' },
            ].map((stat) => (
              <div key={stat.label}>
                <p className="text-3xl font-bold text-primary-600">{stat.value}</p>
                <p className="mt-1 text-sm text-text-muted">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-7xl px-4 py-16 text-center sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-text-primary">
          ¿Listo para empezar?
        </h2>
        <p className="mt-2 text-text-secondary">
          Iniciá sesión con la cuenta asignada por administración.
        </p>
      </section>

      <Footer />
    </>
  );
}
