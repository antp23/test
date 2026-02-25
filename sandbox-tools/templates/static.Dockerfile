FROM nginx:alpine

# Copy built static files into nginx html directory
COPY {{build_dir}} /usr/share/nginx/html

# Copy custom nginx config if provided
COPY nginx.conf /etc/nginx/conf.d/default.conf 2>/dev/null || true

EXPOSE {{port}}

CMD ["nginx", "-g", "daemon off;"]
