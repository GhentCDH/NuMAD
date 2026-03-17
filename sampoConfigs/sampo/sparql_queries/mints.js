export const mintProperties = `
{
    ?id a nmo:Mint ;
        rdfs:label ?prefLabel__prefLabel .
    bind(?id as ?prefLabel__id)
    bind(?id as ?uri__id)
    bind(?id as ?uri__prefLabel)
    
    bind(concat("/mints/page/", STRAFTER(str(?id), "mint/")) as ?prefLabel__dataProviderUrl)
    bind(?mint_dataProviderUrl as ?uri__dataProviderUrl)
}
union
{
    ?id owl:sameAs ?nomismaUri__id .
    bind(?nomismaUri__id as ?nomismaUri__prefLabel)
    bind(?nomismaUri__id as ?nomismaUri__dataProviderUrl)
}
`

export const mintPropertiesDetail = `
{
    ?id a nmo:Mint ;
        rdfs:label ?name__prefLabel .
    bind(?id as ?name__id)
    bind(?id as ?uri__id)
    bind(?id as ?uri__prefLabel)
    
    bind(?name__prefLabel as ?prefLabel__prefLabel)
    bind(?name__prefLabel as ?prefLabel__id)
    
    bind(concat("/mints/page/", STRAFTER(str(?id), "mint/")) as ?name__dataProviderUrl)
    bind(?name__dataProviderUrl as ?uri__dataProviderUrl)
    
    bind(?name__dataProviderUrl as ?prefLabel__dataProviderUrl)
}
union
{
    ?id owl:sameAs ?nomismaUri__id .
    bind(?nomismaUri__id as ?nomismaUri__prefLabel)
    bind(?nomismaUri__id as ?nomismaUri__dataProviderUrl)
}
union
{
    ?coin__id nmo:hasMint ?id ;
              rdfs:label ?coin__label .
  
    optional {
      ?coin__id nmo:hasDenomination ?denomination__id .
        ?denomination__id rdfs:label ?denomination__prefLabel .
        bind(concat("/denominations/page/", STRAFTER(str(?denomination__id), "denomination/")) as ?denomination__dataProviderUrl)
    }
    
    bind(concat(?coin__label, ", ", COALESCE(?denomination__prefLabel, " - ")) as ?coin__prefLabel)
    
    bind(concat("/coins/page/", STRAFTER(str(?coin__id), "coin/")) as ?coin__dataProviderUrl)
    bind(concat("/denominations/page/", STRAFTER(str(?denomination__id), "denomination/")) as ?denomination__dataProviderUrl)
    optional {
      ?coin__id nmo:hasAuthority ?authority__id .
      ?authority__id rdfs:label ?authority__prefLabel .
      bind(concat("/authorities/page/", STRAFTER(str(?authority__id), "ruler/")) as ?authority__dataProviderUrl)
    }
    
    optional {
      ?coin__id nmo:hasMaterial ?material__id .
      ?material__id skos:prefLabel ?material__prefLabel .
      bind(concat("/materials/page/", STRAFTER(str(?material__id), "material/")) as ?material__dataProviderUrl)
    }      
}
`

export const mintPlaces = `
SELECT DISTINCT ?id ?lat ?long ?markerColor
(1 as ?instanceCount) # for heatmap
WHERE {
    <FILTER>
    ?id a nmo:Mint ;
        schema:geo ?geo .
    ?geo schema:latitude ?lat ;
         schema:longitude ?long .
    BIND("Green" AS ?markerColor)
}
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