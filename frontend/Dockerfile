# FE-01: imagen de producción del frontend. Sin servicio en
# docker-compose.yml todavía: se cablea al construirlo de nuevo.
FROM node:20-alpine AS deps
WORKDIR /code
COPY package.json package-lock.json* .npmrc ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /code
COPY --from=deps /code/node_modules ./node_modules
COPY . .
# Los rewrites de /api quedan fijados al compilar: apunta al backend de la red de compose.
ARG BACKEND_URL=http://backend:8000
ENV BACKEND_URL=$BACKEND_URL
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /code
ENV NODE_ENV=production
ARG BACKEND_URL=http://backend:8000
ENV BACKEND_URL=$BACKEND_URL
COPY --from=builder /code/.next/standalone ./
COPY --from=builder /code/.next/static ./.next/static
COPY --from=builder /code/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
