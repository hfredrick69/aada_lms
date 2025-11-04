# Use an official Node.js runtime as the base image
FROM node:20-alpine

# Set working directory inside the container
WORKDIR /app

# Copy dependency files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the project files
COPY . .

# Expose the dev server port
EXPOSE 5173

# Default command to start Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
