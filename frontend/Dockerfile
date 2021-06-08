# build stage
FROM node:14 AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . . 

RUN npm run build

# server stage
FROM nginx:1.21

COPY --from=builder /app/dist/ /usr/share/nginx/html
COPY --from=builder /app/src/index.html /usr/share/nginx/html/index.html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
