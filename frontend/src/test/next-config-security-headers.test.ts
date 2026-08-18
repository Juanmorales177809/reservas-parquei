import { afterEach, describe, expect, it, vi } from 'vitest';

const CSP_SOURCE_SIN_DOCS = '/:path((?!docs$|openapi\\.json$).*)';

async function cargarConfig() {
  vi.resetModules();
  const mod = await import('../../next.config.js');
  return mod.default as {
    headers: () => Promise<Array<{ source: string; headers: Array<{ key: string; value: string }> }>>;
  };
}

describe('next.config.js — cabeceras de seguridad', () => {
  const originalNodeEnv = process.env.NODE_ENV;
  const originalEnvironment = process.env.ENVIRONMENT;

  afterEach(() => {
    vi.stubEnv('NODE_ENV', originalNodeEnv ?? 'test');
    if (originalEnvironment === undefined) {
      delete process.env.ENVIRONMENT;
    } else {
      vi.stubEnv('ENVIRONMENT', originalEnvironment);
    }
  });

  it('aplica las cabeceras comunes a todas las rutas', async () => {
    const config = await cargarConfig();
    const [comunes] = await config.headers();

    expect(comunes.source).toBe('/:path*');
    const porClave = Object.fromEntries(comunes.headers.map((h) => [h.key, h.value]));
    expect(porClave['X-Content-Type-Options']).toBe('nosniff');
    expect(porClave['X-Frame-Options']).toBe('DENY');
    expect(porClave['Referrer-Policy']).toBe('strict-origin-when-cross-origin');
    expect(porClave['Permissions-Policy']).toBe('camera=(), microphone=(), geolocation=()');
  });

  it('no envía HSTS ni COOP sin ENVIRONMENT=production explícito', async () => {
    delete process.env.ENVIRONMENT;
    const config = await cargarConfig();
    const [comunes] = await config.headers();

    const claves = comunes.headers.map((h) => h.key);
    expect(claves).not.toContain('Strict-Transport-Security');
    expect(claves).not.toContain('Cross-Origin-Opener-Policy');
  });

  it('NODE_ENV=production por sí solo (docker-compose.yml) no activa HSTS', async () => {
    vi.stubEnv('NODE_ENV', 'production');
    delete process.env.ENVIRONMENT;
    const config = await cargarConfig();
    const [comunes] = await config.headers();

    expect(comunes.headers.map((h) => h.key)).not.toContain('Strict-Transport-Security');
  });

  it('activa HSTS y COOP solo con ENVIRONMENT=production', async () => {
    vi.stubEnv('ENVIRONMENT', 'production');
    const config = await cargarConfig();
    const [comunes] = await config.headers();

    const porClave = Object.fromEntries(comunes.headers.map((h) => [h.key, h.value]));
    expect(porClave['Strict-Transport-Security']).toBe('max-age=63072000; includeSubDomains');
    expect(porClave['Cross-Origin-Opener-Policy']).toBe('same-origin');
  });

  it('excluye /docs y /openapi.json del bloque de CSP', async () => {
    const config = await cargarConfig();
    const [, csp] = await config.headers();

    expect(csp.source).toBe(CSP_SOURCE_SIN_DOCS);
    expect(csp.headers).toHaveLength(1);
    expect(csp.headers[0].key).toBe('Content-Security-Policy');
  });

  it('la CSP de desarrollo permite eval/inline y ws: para Fast Refresh', async () => {
    vi.stubEnv('NODE_ENV', 'development');
    const config = await cargarConfig();
    const [, csp] = await config.headers();

    expect(csp.headers[0].value).toContain("script-src 'self' 'unsafe-eval' 'unsafe-inline'");
    expect(csp.headers[0].value).toContain('connect-src \'self\' ws:');
  });

  it('la CSP de producción no incluye unsafe-eval ni ws:', async () => {
    vi.stubEnv('NODE_ENV', 'production');
    const config = await cargarConfig();
    const [, csp] = await config.headers();

    expect(csp.headers[0].value).toContain("script-src 'self'");
    expect(csp.headers[0].value).not.toContain('unsafe-eval');
    expect(csp.headers[0].value).not.toContain('ws:');
  });

  it('la CSP (dev y prod) permite unsafe-inline en style-src para Recharts/heatmap', async () => {
    for (const env of ['development', 'production']) {
      vi.stubEnv('NODE_ENV', env);
      const config = await cargarConfig();
      const [, csp] = await config.headers();
      expect(csp.headers[0].value).toContain("style-src 'self' 'unsafe-inline'");
    }
  });
});
