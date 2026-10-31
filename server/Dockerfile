# Use Node.js 22 LTS version
FROM node:22-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including devDependencies for tsx)
RUN npm ci

# Copy source code
COPY tsconfig.json ./
COPY src ./src

# Expose port (Cloud Run uses PORT env variable)
EXPOSE 8484

# Set environment to production
ENV NODE_ENV=production

# Start the application using tsx (no build step needed)
CMD ["npx", "tsx", "src/index.ts"]
