export const coinProperties = `
{
    ?id rdf:type nmo:Find ;
        rdfs:label ?coinId__prefLabel .
    bind(?id as ?uri__id)
    bind(?id as ?uri__prefLabel)
    bind(?id as ?coinId__id)
    bind(concat("/coins/page/", str(?coinId__prefLabel)) as ?uri__dataProviderUrl)
    bind(?uri__dataProviderUrl as ?coinId__dataProviderUrl)
    
    bind(?uri__dataProviderUrl as ?prefLabel__dataProviderUrl)
}
union
{
    ?id nmo:hasDenomination ?denomination__id .
    ?denomination__id rdfs:label ?denomination__prefLabel .
    bind(concat("/denominations/page/", STRAFTER(str(?denomination__id), "denomination/")) as ?denomination__dataProviderUrl)
    
    ?id rdfs:label ?coinIdLabel .
    bind(concat(?coinIdLabel, " - ", ?denomination__prefLabel) as ?prefLabel__prefLabel)
}
union
{
    ?id nmd:hasIdentifier ?identifier__id .
    ?identifier__id foaf:name ?identifier__prefLabel .
    bind(concat("/identifiers/page/", STRAFTER(str(?identifier__id), "identifier/")) as ?identifier__dataProviderUrl)
}
union
{
    ?id nmo:hasAuthority ?authority__id .
    ?authority__id rdfs:label ?authority__prefLabel .
    bind(concat("/authorities/page/", STRAFTER(str(?authority__id), "ruler/")) as ?authority__dataProviderUrl)
}
union
{
    ?id nmo:hasMint ?mint__id .
    ?mint__id rdfs:label ?mint__prefLabel .
    bind(concat("/mints/page/", STRAFTER(str(?mint__id), "mint/")) as ?mint__dataProviderUrl)
}
union
{
    ?id nmo:hasMaterial ?material__id .
    ?material__id skos:prefLabel ?material__prefLabel .
    bind(concat("/materials/page/", STRAFTER(str(?material__id), "material/")) as ?material__dataProviderUrl)
}
union
{
    ?id nmo:hasFindContext/nmo:hasDate ?findDate__id .
    bind(str(?findDate__id) as ?findDate__prefLabel)
}
union
{
    ?id nmd:hasLocalAdminUnit ?localAdminUnit__id .
    ?localAdminUnit__id rdfs:label ?localAdminUnit__prefLabel .
    bind(concat("/localadminunits/page/", STRAFTER(str(?localAdminUnit__id), "localadminunit/")) as ?localAdminUnit__dataProviderUrl)
}
union
{
    ?id nmo:hasStartDate ?yearStart__id .
    bind(?yearStart__id as ?yearStart__prefLabel)
}
union
{
    ?id nmo:hasEndDate ?yearEnd__id .
    bind(?yearEnd__id as ?yearEnd__prefLabel)
}
union
{
    ?id nmo:hasWeight ?weight__id .
    bind(?weight__id as ?weight__prefLabel)
}
union
{
    ?id nmo:hasDiameter ?diameter__id .
    bind(?diameter__id as ?diameter__prefLabel)
}
union
{
    ?id nmo:hasAxis ?axis__id .
    bind(?axis__id as ?axis__prefLabel)
}
union
{
    ?id owl:sameAs ?nomismaUri__id .
    bind(?nomismaUri__id as ?nomismaUri__prefLabel)
    bind(?nomismaUri__id as ?nomismaUri__dataProviderUrl)
}
`

export const coinPlaces = `
SELECT DISTINCT ?id ?lat ?long ?markerColor
(1 as ?instanceCount) # for heatmap
WHERE {
    <FILTER>
    ?id a nmo:Find ;
        nmd:hasLocalAdminUnit ?lau .
    ?lau schema:geo ?geo .
    ?geo schema:latitude ?lat ;
         schema:longitude ?long .
    BIND("Red" AS ?markerColor)
}
`

export const mintPlaces = `
SELECT DISTINCT ?id ?lat ?long ?markerColor
(1 as ?instanceCount) # for heatmap
WHERE {
    <FILTER>
    ?id a nmo:Find ;
        nmo:hasMint ?mint .
    ?mint schema:geo ?geo .
    ?geo schema:latitude ?lat ;
         schema:longitude ?long .
    BIND("Red" AS ?markerColor)
}
`

export const migrations = `
SELECT ?id
    ?from__id ?from__prefLabel ?from__lat ?from__long ?from__dataProviderUrl
    ?to__id ?to__prefLabel ?to__lat ?to__long ?to__dataProviderUrl
(COUNT(DISTINCT ?coin) as ?instanceCount)
WHERE {
    <FILTER>
    ?coin a nmo:Find ;
        nmo:hasMint ?from__id ;
        nmd:hasLocalAdminUnit ?to__id .
          
    ?from__id rdfs:label ?from__prefLabel ;
              schema:geo/schema:latitude ?from__lat ;
              schema:geo/schema:longitude ?from__long .
    bind(concat("/mints/page/", STRAFTER(str(?from__id), "mint/")) as ?from__dataProviderUrl)
              
    ?to__id rdfs:label ?to__prefLabel ;
            schema:geo/schema:latitude ?to__lat ;
            schema:geo/schema:longitude ?to__long .
    bind(concat("/localadminunits/page/", STRAFTER(str(?to__id), "localadminunit/")) as ?to__dataProviderUrl)
    
  bind(IRI(concat(str(?from__id), "-", replace(str(?to__id), "http://numad.ugent.be/resource/localadminunit/", ""))) as ?id)
  filter(?to__id != ?from__id)
}
GROUP BY ?id ?from__id ?from__prefLabel ?from__lat ?from__long ?from__dataProviderUrl 
?to__id ?to__prefLabel ?to__lat ?to__long ?to__dataProviderUrl
ORDER BY desc(?instanceCount)
`

export const facetResultSetQueryOntop = `
SELECT *
WHERE {
{
  SELECT DISTINCT * {
    <FILTER>
    VALUES ?facetClass { <FACET_CLASS> }
    ?id <FACET_CLASS_PREDICATE> ?facetClass .
    <ORDER_BY_TRIPLE>
  }
  <ORDER_BY>
  <PAGE>
}
FILTER(BOUND(?id))
<RESULT_SET_PROPERTIES>
}
<ORDER_BY>
`