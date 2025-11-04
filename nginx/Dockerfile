FROM nginx:alpine

# Copy SSL certificates
COPY ssl/ /etc/nginx/ssl/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose ports
EXPOSE 80 443 5173 5174

CMD ["nginx", "-g", "daemon off;"]
