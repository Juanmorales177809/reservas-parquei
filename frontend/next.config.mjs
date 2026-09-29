/** @type {import('next').NextConfig} */
// BACKEND_URL se lee al compilar (los rewrites quedan fijados en el build).
const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

const nextConfig = {
  output: "standalone",
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${BACKEND_URL}/api/:path*` }];
  },
};

export default nextConfig;
