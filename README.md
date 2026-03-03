# NuMAD

sparql endpoint and sampo-ui interface for NuMAD coin finds data.

## Architecture

### Import script
load initial data from csv into postgres database. Cleans up data
to be imported in a more usable way.

### Posgtres database
Source of truth for the data

### Ontop vkg
Maps the data in real time from the database to a sparql endpoint using
the nomisma ontology for the most part.

### Sampo UI

#### Sampo client
The sampo client sends requests to the sampo server to get results and facets etc.

#### Sampo server
The sampo server takes requests from the client and sends sparql
queries to the ontop endpoint to get data from the VKG.

---
## Requirements

Install ``just`` to be able to run commands from the justfile.

Download postgres jdbc driver for ontop:
```shell
curl -o ontop/jdbc/postgresql-42.7.8.jar https://jdbc.postgresql.org/download/postgresql-42.7.8.jar
```


## Usage

Rebuild, run import script and rerun everything:
```shell
just reinit
```

Rerun import script:
```shell
just import
```

Run everything
```shell
docker compose up -d
```

Stop running
```shell
docker compose down
```

---
