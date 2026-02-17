reset-db:
    docker volume rm numad_pgdata || echo "pg_data already removed"

# restart and rebuild all containers, and start with fresh database
rebuild:
    docker compose down -t 1
    @just reset-db
    # docker compose build --no-cache import
    docker compose up -d --build

import:
    docker compose exec import uv run import

kottster:
    docker compose exec -d kottster /dev.sh

reinit: rebuild import
    
jdbc:
    curl https://jdbc.postgresql.org/download/postgresql-42.7.8.jar -O --output-dir ./ontop/jdbc
