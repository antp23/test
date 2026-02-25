FROM node:{{node_version}}-alpine

WORKDIR /app

# Install dependencies first for better layer caching
COPY package*.json ./
COPY yarn.lock* ./
COPY pnpm-lock.yaml* ./
RUN {{install}}

# Copy source and build
COPY . .
RUN {{build}}

EXPOSE {{port}}

CMD ["sh", "-c", "{{start}}"]
