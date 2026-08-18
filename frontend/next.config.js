const esProduccion = process.env.NODE_ENV === 'production';
// Distinto de NODE_ENV a propósito: docker-compose.yml fija NODE_ENV=production
// también para el stack local sobre HTTP simple (sin TLS documentado en este
// repo). HSTS/COOP solo deben forzarse cuando el operador confirma HTTPS real
// vía esta variable explícita (mismo patrón que `environment` en
// backend/app/config.py, que tampoco se activa con docker-compose.yml tal cual).
const httpsConfirmado = process.env.ENVIRONMENT === 'production';

// Cabeceras comunes: no rompen /docs (Swagger UI, proxied desde el backend),
// así que se aplican a todas las rutas.
const cabecerasComunes = [
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
  ...(httpsConfirmado
    ? [
        { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains' },
        { key: 'Cross-Origin-Opener-Policy', value: 'same-origin' },
      ]
    : []),
];

// CSP de la app:
// - 'unsafe-inline' en script-src es obligatorio incluso en build de
//   producción: el App Router de Next.js 14 inyecta <script> inline para
//   streamear e hidratar Server Components (self.__next_f.push(...)); sin
//   nonce (no implementado en esta fase), un script-src estricto rompe la
//   hidratación de toda página. Verificado manualmente: con script-src 'self'
//   a secas, el navegador bloquea esos scripts y la app no hidrata.
// - 'unsafe-inline' en style-src es necesario para los estilos inline de
//   Recharts y del heatmap del dashboard (AdminDashboardCharts.tsx).
// - 'unsafe-eval' en script-src y ws: en connect-src solo en desarrollo,
//   porque el Fast Refresh de Next.js los necesita; no se aplican en build
//   de producción.
const cspApp = esProduccion
  ? "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
  : "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' ws:; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'";

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/:path*`,
      },
      {
        source: '/docs',
        destination: `${backendUrl}/docs`,
      },
      {
        source: '/openapi.json',
        destination: `${backendUrl}/openapi.json`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: cabecerasComunes,
      },
      {
        // Excluye /docs y /openapi.json: son el proxy a Swagger UI del
        // backend, que carga script/CSS desde cdn.jsdelivr.net y usa un
        // <script> inline de inicialización; la CSP de la app los bloquearía.
        source: '/:path((?!docs$|openapi\\.json$).*)',
        headers: [{ key: 'Content-Security-Policy', value: cspApp }],
      },
    ];
  },
};

module.exports = nextConfig;
