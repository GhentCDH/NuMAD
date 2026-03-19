# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NuMAD is a SPARQL endpoint and Sampo-UI interface for numismatic (coin finds) data, developed by Ghent Centre for Digital Humanities. It combines a relational PostgreSQL database with a Virtual Knowledge Graph (Ontop) that exposes data as RDF via SPARQL using the Nomisma ontology.

## Architecture

The system runs as Docker Compose services:

- **db** — PostgreSQL 17 + PostGIS (port 5432)
- **import** — Python 3.13 data pipeline that loads CSV into PostgreSQL (`import/`)
- **ontop** — Virtual Knowledge Graph mapping PostgreSQL → SPARQL endpoint (port 8080) (`ontop/`)
- **client/server** — Sampo UI frontend (port 3000) and backend (port 3001) for semantic search (`sampoConfigs/`)
- **kottster** — React/Vite app for structured data browsing (port 5480/5481) (`kottster/`)

Data flows: CSV → import script → PostgreSQL → Ontop VKG → SPARQL → Sampo UI. Kottster connects directly to PostgreSQL via Knex.js.

## Commands

All commands require Docker and `just` (task runner).

```shell
# Full rebuild: reset DB, rebuild containers, run import
just reinit

# Reset DB and rebuild containers only
just rebuild

# Run data import only
just import

# Download PostgreSQL JDBC driver for Ontop
just jdbc

# Start Kottster dev server
just kottster

# Start/stop all services
docker compose up -d
docker compose down

# Run import manually inside container
docker compose exec import uv run import
```

## Key Directories

- `import/` — Python import pipeline (uv package manager, SQLModel ORM, GeoAlchemy2)
  - `src/numad_import/cli.py` — CLI entry point
  - `src/numad_import/model.py` — Database models (20+ tables: Coin, Mint, Ruler, FindSpot, etc.)
- `ontop/input/` — Semantic web configuration
  - `mapping.ttl` — R2RML mappings from PostgreSQL tables to RDF
  - `ontology.ttl` — NuMAD custom ontology extending Nomisma
- `sampoConfigs/` — Sampo UI configuration (search perspectives, SPARQL queries, translations)
- `kottster/` — React frontend with Kottster framework
- `data/` — CSV data files and SQL init scripts

## Environment

Copy `dev.env` to `.env` for local development. Key variables: database credentials, Ontop JDBC config, SPARQL endpoint URL, Sampo API URL.

## Ontology Notes

The Nomisma ontology (`nmo:`) is extremely loosely defined with no domains or ranges. The project takes some liberty in assigning literal properties while following Nomisma conventions. Key prefixes: `nmd:` (NuMAD custom), `nmo:` (Nomisma), `schema:` (Schema.org). If Nomisma releases a better-defined version, migration is recommended.

## Prerequisites

- Docker & Docker Compose
- `just` command runner
- CSV data file `numad-data-20251208.csv` in `data/`
- PostgreSQL JDBC driver (run `just jdbc`)
- Optional: `belgium.pmtiles` and `europe.pmtiles` in `sampoConfigs/sampo/assets/maps/` for map base layers
