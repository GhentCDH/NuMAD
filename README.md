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

You also need the original csv file named `numad-data-20251208.csv` in the `data` directory.

### Maps
This config uses local pmtiles files for the base layers of maps. For this to work you either need
to download the files `belgium.pmtiles` and `europe.pmtiles` into `sampoConfigs/sampo/assets/maps` or edit
the configs of the `coins.json` search perspective to point to where your base layer files are hosted.

The pmtiles files were downloaded using scripts from 
[this repository.](https://github.com/GhentCDH/ghentcdh-local-maps)


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

## Credits

Development by [Ghent Centre for Digital Humanities - Ghent University](https://www.ghentcdh.ugent.be/). Funded by the [GhentCDH research projects](https://www.ghentcdh.ugent.be/projects).

<img src="https://www.ghentcdh.ugent.be/ghentcdh_logo_blue_text_transparent_bg_landscape.svg" alt="Landscape" width="500">