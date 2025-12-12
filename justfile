reset-db:
    docker volume rm numad_pgdata || echo "pg_data already removed"

# restart and rebuild all containers, and start with fresh database
rebuild:
    docker compose down -t 1
    @just reset-db
    # docker compose build --no-cache import
    docker compose up -d --build

import:
    docker compose exec import uv run main.py

kottster:
    docker compose exec kottster /dev.sh

reinit: rebuild import
    
