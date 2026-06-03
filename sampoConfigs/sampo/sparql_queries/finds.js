export const findProperties = `
{
    ?id rdf:type nmo:Find ;
        rdfs:label ?findId__prefLabel .
    bind(?id as ?uri__id)
    bind(?id as ?uri__prefLabel)
    bind(?id as ?findId__id)
    bind(concat("/finds/page/", str(?findId__prefLabel)) as ?uri__dataProviderUrl)
    bind(?uri__dataProviderUrl as ?findId__dataProviderUrl)
}
union
{
    ?id nmd:hasLocalAdminUnit ?localAdminUnit__id .
    ?localAdminUnit__id rdfs:label ?localAdminUnit__prefLabel .
    bind(concat("/localadminunits/page/", STRAFTER(str(?localAdminUnit__id), "localadminunit/")) as ?localAdminUnit__dataProviderUrl)
}
union
{
    ?id nmo:hasFindSpot ?findSpot__id .
    ?findSpot__id nmd:hasFindSpotToponym ?findSpotToponym__id .
    bind(?findSpotToponym__id as ?findSpotToponym__prefLabel)
}
union
{
    ?id nmo:hasFindSpot ?findSpot__id .
    ?findSpot__id nmd:hasSiteClassification ?siteClassification__id .
    bind(?siteClassification__id as ?siteClassification__prefLabel)
}
union
{
    ?id nmo:hasFindSpot ?findSpot__id .
    ?findSpot__id nmd:hasArchaeologicalStructure ?archaeologicalStructure__id .
    bind(?archaeologicalStructure__id as ?archaeologicalStructure__prefLabel)
}
union
{
    ?id nmd:hasDiscoveryType ?discoveryType__id .
    bind(?discoveryType__id as ?discoveryType__prefLabel)
}
union
{
    ?id nmd:hasDepositionType ?depositionType__id .
    bind(?depositionType__id as ?depositionType__prefLabel)
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


export const facetValuesQueryOntop = `
  SELECT DISTINCT ?id ?prefLabel ?selected ?parent ?instanceCount {
    {
      {
        SELECT DISTINCT (count(DISTINCT ?instance) as ?instanceCount) ?id ?parent ?selected {
          # facet values that return results
          {
            <FILTER>
            ?instance <PREDICATE> ?id .
            <PARENTS>
            VALUES ?facetClass { <FACET_CLASS> }
            ?instance <FACET_CLASS_PREDICATE> ?facetClass .
            <SELECTED_VALUES>
          }
          <SELECTED_VALUES_NO_HITS>
          BIND(COALESCE(?selected_, false) as ?selected)
        }
        GROUP BY ?id ?parent ?selected
      }
      FILTER(BOUND(?id))
      <FACET_VALUE_FILTER>
      <LABELS>
    }
    UNION
    {
      # 'Unknown' facet value for results with no predicate path
      {
        SELECT DISTINCT (count(DISTINCT ?instance) as ?instanceCount) {
          <FILTER>
          VALUES ?facetClass { <FACET_CLASS> }
          ?instance <FACET_CLASS_PREDICATE> ?facetClass .
          OPTIONAL {
            ?instance <MISSING_PREDICATE> ?not_exists .
          }
          FILTER(!BOUND(?not_exists))
        }
      }
      FILTER(?instanceCount > 0)
      BIND(IRI("http://ldf.fi/MISSING_VALUE") AS ?id)
      # prefLabel for <http://ldf.fi/MISSING_VALUE> is given in client/translations
      BIND('0' as ?parent)
      BIND(<UNKNOWN_SELECTED> as ?selected)
    }
  }
  <ORDER_BY>
`
