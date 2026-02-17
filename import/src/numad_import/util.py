import requests as req
import re

NOMISMA_ENDPOINT = "https://nomisma.org/query"

PREFIXES = """
PREFIX crm:  <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX dcterms:  <http://purl.org/dc/terms/>
PREFIX dcmitype:  <http://purl.org/dc/dcmitype/>
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX geo:  <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX nm:  <http://nomisma.org/id/>
PREFIX nmo:  <http://nomisma.org/ontology#>
PREFIX org:  <http://www.w3.org/ns/org#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos:  <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

"""

RULER_QUERY = """
SELECT distinct ?ruler WHERE {
  ?ruler a foaf:Person .
  ?ruler skos:prefLabel ?label .
  FILTER(CONTAINS(LCASE(?label), "<RULER_NAME>")) .
  ?ruler org:hasMembership/nmo:hasStartDate ?sd ;
         org:hasMembership/nmo:hasEndDate ?ed .
  FILTER(year(?sd) = <START_DATE>) .
  FILTER(year(?ed) = <END_DATE>) .
  
} LIMIT 1
"""

DENOMINATION_QUERY = """
SELECT distinct ?denomination WHERE {
  ?denomination a nmo:Denomination ;
         skos:prefLabel ?label.
  FILTER(LCASE(?label) = "<DENOMINATION_NAME>"@en) .
} LIMIT 1
"""

MINT_QUERY = """
SELECT distinct ?mint WHERE {
  ?mint a nmo:Mint ;
         skos:prefLabel ?label.
  FILTER(LCASE(?label) = "<MINT_NAME>"@en) .
} LIMIT 1
"""

MATERIALS = {
    "ae": {
        "nmo": "http://nomisma.org/id/ae",
        "label": "Bronze"
    },
    "ar": {
        "nmo": "http://nomisma.org/id/ar",
        "label": "Silver"
    },
    "potin": {
        "nmo": "http://nomisma.org/id/potin",
        "label": "Potin"
    },
    "pb": {
        "nmo": "http://nomisma.org/id/pb",
        "label": "Lead"
    },
    "au": {
        "nmo": "http://nomisma.org/id/av",
        "label": "Gold"
    },
    "el": {
        "nmo": "http://nomisma.org/id/el",
        "label": "Electrum"
    },
    "zn": {
        "nmo": "http://nomisma.org/id/zn",
        "label": "Zinc"
    },
    "billon": {
        "nmo": "http://nomisma.org/id/billon",
        "label": "Billon"
    },
    "nickel": {
        "nmo": "http://nomisma.org/id/ni",
        "label": "Nickel"
    }
}


def clean_name(name:str) -> str :
    return re.sub(r"[<>!;?]", "", name.lower().replace("-", " ").replace(",", " "))


def get_nomisma_ruler(name: str, start_date: int, end_date: int) -> str | None:
    if name is None or start_date is None or end_date is None:
        return None

    sparql_query = PREFIXES + RULER_QUERY.replace("<RULER_NAME>", clean_name(name)).replace("<START_DATE>", str(start_date)).replace("<END_DATE>", str(end_date))
    params = {
        "query": sparql_query,
        "output": "json"
    }

    res = req.get(NOMISMA_ENDPOINT, params=params)

    if res.status_code == 200:
        data = res.json()
        if len(data["results"]["bindings"]) == 1:
            return f"<{data["results"]["bindings"][0]["ruler"]["value"]}>"
    else:
        print(res.status_code)
        print(res.text)
        print(res.json())
        print(params["query"])
    return None


def get_nomisma_denomination(name: str) -> str | None:
    if name is None:
        return None

    sparql_query = PREFIXES + DENOMINATION_QUERY.replace("<DENOMINATION_NAME>", clean_name(name))
    params = {
        "query": sparql_query,
        "output": "json"
    }

    res = req.get(NOMISMA_ENDPOINT, params=params)

    if res.status_code == 200:
        data = res.json()
        if len(data["results"]["bindings"]) == 1:
            return f"<{data["results"]["bindings"][0]["denomination"]["value"]}>"
    else:
        print(res.status_code)
        print(res.text)
        print(res.json())
        print(params["query"])
    return None


def get_nomisma_mint(name: str) -> str | None:
    if name is None:
        return None

    sparql_query = PREFIXES + MINT_QUERY.replace("<MINT_NAME>", clean_name(name))
    params = {
        "query": sparql_query,
        "output": "json"
    }

    res = req.get(NOMISMA_ENDPOINT, params=params)

    if res.status_code == 200:
        data = res.json()
        if len(data["results"]["bindings"]) == 1:
            return f"<{data["results"]["bindings"][0]["mint"]["value"]}>"
    else:
        print(res.status_code)
        print(res.text)
        print(res.json())
        print(params["query"])
    return None


def get_nomisma_material(material: str):
    return MATERIALS.get(material.lower())


if __name__ == '__main__':
    print(get_nomisma_denomination("potin"))