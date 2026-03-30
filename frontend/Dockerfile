# ===========================================
# PCQVP Frontend - Dockerfile
# Nuxt 4 + pnpm (multi-stage build)
# ===========================================

# --- Stage 1: Build ---
FROM node:20-alpine AS build

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Install dependencies
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Copy source and build
COPY . .

ARG NUXT_BACKEND_URL=http://backend:8000
ENV NUXT_BACKEND_URL=${NUXT_BACKEND_URL}

RUN pnpm build

# --- Stage 2: Production ---
FROM node:20-alpine AS production

WORKDIR /app

# Copy built output
COPY --from=build /app/.output .output

EXPOSE 3000

ENV HOST=0.0.0.0
ENV PORT=3000

CMD ["node", ".output/server/index.mjs"]
