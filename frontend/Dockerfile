# Imagen de producción del frontend (Next.js en modo standalone).
FROM node:20-alpine AS deps
WORKDIR /code
COPY package.json package-lock.json* .npmrc ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /code
COPY --from=deps /code/node_modules ./node_modules
COPY . .
# Los rewrites de /api quedan fijados al compilar: apuntan al backend dentro de la red de compose, así que el
# navegador solo habla con este servidor (mismo origen, sin CORS) y este reenvía a `backend`.
ARG BACKEND_URL=http://backend:8000
ENV BACKEND_URL=$BACKEND_URL
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /code
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
# El servidor standalone escucha en el nombre del contenedor salvo que se le diga otra cosa: sin esto, el
# puerto publicado no responde desde fuera.
ENV HOSTNAME=0.0.0.0
ENV PORT=3000
ARG BACKEND_URL=http://backend:8000
ENV BACKEND_URL=$BACKEND_URL
COPY --from=builder --chown=node:node /code/.next/standalone ./
COPY --from=builder --chown=node:node /code/.next/static ./.next/static
COPY --from=builder --chown=node:node /code/public ./public
USER node
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD wget -q -O /dev/null http://127.0.0.1:3000/login || exit 1
CMD ["node", "server.js"]
