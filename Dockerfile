FROM node:22.17-slim AS base
WORKDIR /app

COPY custom_components .
RUN npm install --legacy-peer-deps

RUN npm run build

FROM ghcr.io/semanticcomputing/sampo-ui-combo:v4.0.1-dev as prod
COPY --from=base /app/dist/ /app/custom-components
COPY sampoConfigs/ /app/configs/
ENV NODE_ENV=production
