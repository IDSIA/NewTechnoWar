FROM node:14 AS base
FROM node:14 AS builder

# build stage

# app work directory
WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install

COPY . . 

RUN npm run build

# deploy stage
FROM base

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/package*.json ./
COPY --from=builder /usr/src/app/dist/* ./

EXPOSE 8080

CMD ["node", "index.js"]
