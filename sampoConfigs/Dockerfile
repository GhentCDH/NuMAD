FROM node:22.17-slim AS base
WORKDIR /app

COPY ../custom_components .
RUN npm install --legacy-peer-deps

RUN npm run build

FROM ghcr.io/ghentcdh/sampo-ui-combo:v4.3.3 as prod
COPY --from=base /app/dist/ /app/custom-components
COPY sampoConfigs/ /app/configs/
ENV NODE_ENV=production
