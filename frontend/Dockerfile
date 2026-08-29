# Dockerfile de desenvolvimento: corre o servidor Vite com hot-reload.
# Uma imagem de produção (build estático + nginx) fica para a Fase 14, quando
# fizer sentido falar de deployment — não é necessária para desenvolvimento local.
FROM node:22-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
