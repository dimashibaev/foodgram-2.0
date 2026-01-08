# build env
FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build
CMD sh -c "mkdir -p /frontend_static && rm -rf /frontend_static/* && cp -r build/. /frontend_static/"
