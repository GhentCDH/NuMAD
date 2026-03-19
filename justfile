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

kottster:
    docker compose up -d db kottster

kottster-dev:
    docker compose exec -d kottster /dev.sh

reinit: rebuild import
    
jdbc:
    curl https://jdbc.postgresql.org/download/postgresql-42.7.9.jar -O --output-dir ./ontop/jdbc
