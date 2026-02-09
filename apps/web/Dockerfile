# Stage 1: Build
FROM node:20-alpine AS build
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Use npx to securely execute the build without permission issues
RUN npx ng build --configuration production

# Stage 2: Serve
FROM nginx:alpine
# Copy the build output to the nginx path
COPY --from=build /app/dist/web/browser /usr/share/nginx/html
# Copy your custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
