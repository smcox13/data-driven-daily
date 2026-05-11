FROM node:20-alpine

WORKDIR /app

COPY package.json tsconfig.json next.config.mjs postcss.config.js tailwind.config.ts next-env.d.ts /app/
COPY app /app/app
COPY components /app/components
COPY lib /app/lib
COPY middleware.ts /app/middleware.ts

RUN npm install
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]
