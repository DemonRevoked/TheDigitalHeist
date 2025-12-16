FROM node:20 AS builder
WORKDIR /app

# Install dependencies
COPY webapp/package.json ./package.json
COPY webapp/server/package.json ./server/package.json
COPY webapp/client/package.json ./client/package.json
RUN npm --prefix server install && npm --prefix client install

# Copy source and build client
COPY webapp/server ./server
COPY webapp/client ./client
RUN npm --prefix client run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=80

# Copy server runtime
COPY --from=builder /app/server/package.json ./server/package.json
COPY --from=builder /app/server/node_modules ./server/node_modules
COPY --from=builder /app/server/src ./server/src

# Copy built client assets
COPY --from=builder /app/client/dist ./client/dist

EXPOSE 80
CMD ["node", "server/src/index.js"]
