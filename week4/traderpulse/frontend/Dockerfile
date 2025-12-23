FROM node:20-alpine

WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci

# Copy the source code
COPY . .

# Expose port (Next.js defaults to 3000)
EXPOSE 3000

# Start the development server
CMD ["npm", "run", "dev"]
