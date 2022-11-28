FROM node:19.1.0-alpine3.16

WORKDIR /app

ADD package.json package-lock.json ./

RUN apk add --no-cache python3 g++ make && \
    npm install
