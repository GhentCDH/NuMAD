reset-db:
    docker volume rm numad_pgdata || echo "pg_data already removed"

up:
    docker compose up -d 

down:
    docker compose down

# restart and rebuild all containers, and start with fresh database
rebuild:
    docker compose down -t 1
    @just reset-db
    # docker compose build --no-cache import
    docker compose up -d --build

import:
    docker compose exec import uv run import

drop:
    docker compose exec import uv run drop

drop-db:
    docker compose run --rm --no-deps --build import uv run drop-db



reinit: rebuild import
    
jdbc:
    curl https://jdbc.postgresql.org/download/postgresql-42.7.9.jar -O --output-dir ./ontop/jdbc
