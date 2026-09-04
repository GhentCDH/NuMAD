# Numad import workflow

## Requirements

You are expected to have a copy of the UTF-8 encoded `csv` exported by Excel.
This file should be located at `../data/numad-data.csv`.

## Usage

To run this import script from scratch (with a fresh PostgresQL database), run `just reinit` if you have `just` installed.
Otherwise, run the `reinit` recipe directly:

```sh
docker compose down -t 1
docker volume rm numad_pgdata || echo "pg_data already removed"
docker compose up -d --build
```

To drop only current and known legacy NuMAD tables, run `just drop`. The command checks whether
each table exists and can therefore also be run against an empty database.
