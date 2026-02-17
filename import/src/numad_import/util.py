import requests as req
import re

NOMISMA_ENDPOINT = "https://nomisma.org/query"

GENERAL_QUERY = """
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX nm:  <http://nomisma.org/id/>
PREFIX nmo:  <http://nomisma.org/ontology#>
PREFIX org:  <http://www.w3.org/ns/org#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos:  <http://www.w3.org/2004/02/skos/core#>

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

def get_nomisma_ruler(name: str, start_date: int, end_date: int)-> str | None:
    if name is None or start_date is None or end_date is None:
        return None

    sparql_query = GENERAL_QUERY.replace("<RULER_NAME>",  re.sub(r"[<>!,;]", "", name.lower().replace("-", " "))).replace("<START_DATE>", str(start_date)).replace("<END_DATE>", str(end_date))
    params = {
        "query": sparql_query,
        "output": "json"
    }

    res = req.get(NOMISMA_ENDPOINT, params=params)

    if res.status_code == 200:
        data = res.json()
        if len(data["results"]["bindings"]) == 1:
            return data["results"]["bindings"][0]["ruler"]["value"]
    else:
        print(res.status_code)
        print(res.text)
        print(res.json())
        print(params["query"])
    return None
