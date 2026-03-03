export const authorityProperties = `
{
    ?id rdf:type nmd:Authority .
    ?id rdfs:label ?name__prefLabel .
    bind(?id as ?uri__id)
    bind(?id as ?uri__prefLabel)
    bind(?id as ?name__id)
    bind(concat("/authorities/page/", STRAFTER(str(?id), "ruler/")) as ?uri__dataProviderUrl)
    bind(?uri__dataProviderUrl as ?name__dataProviderUrl)
}
union
{
    ?id owl:sameAs ?nomismaUri__id .
    bind(?nomismaUri__id as ?nomismaUri__prefLabel)
    bind(?nomismaUri__id as ?nomismaUri__dataProviderUrl)
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
`

export const authorityPropertiesDetail = `
{
    ?id rdf:type nmd:Authority .
    ?id rdfs:label ?name__prefLabel .
    bind(?id as ?uri__id)
    bind(?id as ?uri__prefLabel)
    bind(?id as ?name__id)
    bind(concat("/authorities/page/", STRAFTER(str(?id), "ruler/")) as ?uri__dataProviderUrl)
    bind(?uri__dataProviderUrl as ?name__dataProviderUrl)
}
union
{
    ?id owl:sameAs ?nomismaUri__id .
    bind(?nomismaUri__id as ?nomismaUri__prefLabel)
    bind(?nomismaUri__id as ?nomismaUri__dataProviderUrl)
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
    ?coin__id nmo:hasAuthority ?id ;
              nmo:hasDenomination ?denomination__id ;
              rdfs:label ?coin__label .
    ?denomination__id rdfs:label ?denomination__prefLabel .
    
    bind(concat(?coin__label, ", ", ?denomination__prefLabel) as ?coin__prefLabel)
    
    bind(concat("/coins/page/", STRAFTER(str(?coin__id), "coin/")) as ?coin__dataProviderUrl)
    
    bind(concat("/denominations/page/", STRAFTER(str(?denomination__id), "denomination/")) as ?denomination__dataProviderUrl)
    
    optional
    {
        ?coin__id nmo:hasMaterial ?material__id .
        ?material__id skos:prefLabel ?material__prefLabel .
        bind(concat("/materials/page/", STRAFTER(str(?material__id), "material/")) as ?material__dataProviderUrl)
    }
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