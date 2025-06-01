FROM node:18
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./
RUN npm ci

# Copy source files
COPY . .

# Expose the port
EXPOSE 3000

# Start the development server
CMD ["npm", "run", "dev"] 