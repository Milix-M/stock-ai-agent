FROM node:20-alpine

WORKDIR /app

# パッケージマネージャのキャッシュ
COPY package*.json ./
RUN npm ci

# アプリケーションコード
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
