FROM node:24-alpine

WORKDIR /app

COPY website/package*.json ./website/
RUN cd website && npm ci

COPY backoffice/package*.json ./backoffice/
RUN cd backoffice && npm ci

COPY . .

RUN sed -i 's/\r$//' /app/start.sh && chmod +x /app/start.sh

CMD ["sh", "/app/start.sh"]