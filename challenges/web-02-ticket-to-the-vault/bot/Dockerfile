FROM mcr.microsoft.com/playwright:v1.57.0-jammy

WORKDIR /bot

COPY package*.json ./
RUN npm install --omit=dev

COPY . .

ENV NODE_ENV=production
CMD ["node", "bot.js"]
