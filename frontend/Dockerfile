FROM node:20-alpine as build

WORKDIR /app

COPY package*.json ./
# Use .npmrc for security if needed (we created one previously)
COPY .npmrc ./

# Install dependencies (ignoring scripts as per .npmrc)
RUN npm install

# Copy source code
COPY . .

# Build the frontend
RUN npm run build

# Production stage using Nginx
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx configuration to handle React router and proxy to backend
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    \
    location /api/ { \
        proxy_pass http://nedaf-backend:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
