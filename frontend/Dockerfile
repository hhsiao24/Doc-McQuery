FROM oven/bun

# Set the working directory inside the container
WORKDIR /usr/src/app

# Install dependencies
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

# Copy the rest of your application code
COPY . .

# Start server
EXPOSE 5173
CMD ["bun", "run", "dev"] 
