# Frontend Stage - Nginx server
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package.json (if any build tools are needed in future)
COPY package*.json ./

# Install dependencies if needed
RUN npm ci --only=production 2>/dev/null || true

# Copy frontend files
COPY . .

# Final stage
FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy frontend files to nginx
COPY --from=builder /app /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/index.html || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
