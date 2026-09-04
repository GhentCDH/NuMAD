FROM node:22.17-slim AS base
WORKDIR /app

COPY custom_components .
RUN npm install --legacy-peer-deps

RUN npm run build

FROM ghcr.io/semanticcomputing/sampo-ui-combo:v4.0.1-dev AS prod
COPY --from=base /app/dist/ /app/custom-components
COPY sampoConfigs/ /app/configs/
COPY sampoConfigs/sampo/assets/custom.css /usr/share/nginx/html/custom.css
COPY sampoConfigs/sampo/assets/logos/ghentcdh_banner.svg /usr/share/nginx/html/about-assets/ghentcdh-logo.svg
RUN sed -i 's#</head>#<link rel="stylesheet" href="/custom.css"></head>#' /usr/share/nginx/html/index.html
ENV NODE_ENV=production

FROM ghcr.io/ghentcdh/sampo-ui-client:latest AS client
COPY sampoConfigs/sampo/assets/custom.css /usr/share/nginx/html/custom.css
COPY sampoConfigs/sampo/assets/logos/ghentcdh_banner.svg /usr/share/nginx/html/about-assets/ghentcdh-logo.svg
RUN sed -i 's#</head>#<link rel="stylesheet" href="/custom.css"></head>#' /usr/share/nginx/html/index.html
