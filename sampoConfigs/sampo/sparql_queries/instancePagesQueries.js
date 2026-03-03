export const denominationsInstanceProperties = `
{
    ?id rdfs:label ?name__id .
    bind(?name__id as ?name__prefLabel)
    bind(?id as ?uri__id)
    bind(?id as ?uri__prefLabel)
}
union
{
    ?id owl:sameAs ?nomismaUri__id .
    bind(?nomismaUri__id as ?nomismaUri__prefLabel)
}
union
{
    ?coin__id nmo:hasDenomination ?id .
    {
        ?coin__id nmo:hasAuthority ?authority__id .
        ?authority__id rdfs:label ?authority__prefLabel .
        bind(concat("/authorities/page/", STRAFTER(str(?authority__id), "ruler/")) as ?authority__dataProviderUrl)
    }
    union
    {
        ?coin__id nmo:hasMaterial ?material__id .
        ?material__id skos:prefLabel ?material__prefLabel .
        bind(concat("/materials/page/", STRAFTER(str(?material__id), "material/")) as ?material__dataProviderUrl)
    }
}
union
{
    ?id owl:sameAs ?nomismaUri__id .
    bind(?nomismaUri__id as ?nomismaUri__prefLabel)
    bind(?nomismaUri__id as ?nomismaUri__dataProviderUrl)
}
`

export const identifiersInstanceProperties = `
{
    ?id rdfs:label ?name__id .
    bind(?name__id as ?name__prefLabel)
    bind(?id as ?uri__id)
    bind(?id as ?uri__prefLabel)
}
union
{
    ?coin__id nmd:hasIdentifier ?id ;
              nmo:hasDenomination ?denomination__id ;
              rdfs:label ?coin__label .
    ?denomination__id rdfs:label ?denomination__prefLabel .
    bind(concat(?coin__label, ", ", ?denomination__prefLabel) as ?coin__prefLabel)
    bind(concat("/coins/page/", STRAFTER(str(?coin__id), "coin/")) as ?coin__dataProviderUrl)
}
`

export const materialsInstanceProperties = `
{
    ?id rdfs:label ?label__id .
    bind(?label__id as ?label__prefLabel)
    ?id skos:prefLabel ?name__id .
    bind(?name__id as ?name__prefLabel)
    
    bind(?id as ?uri__id)
    bind(?id as ?uri__prefLabel)
}
union
{
    ?coin__id nmo:hasMaterial ?id .
    
    optional
    {
        ?coin__id nmo:hasAuthority ?authority__id .
        ?authority__id rdfs:label ?authority__prefLabel .
        bind(concat("/authorities/page/", STRAFTER(str(?authority__id), "ruler/")) as ?authority__dataProviderUrl)
    }
    
    optional
    {
        ?coin__id nmo:hasMint ?mint__id .
        ?mint__id rdfs:label ?mint__prefLabel .
        bind(concat("/mints/page/", STRAFTER(str(?mint__id), "mint/")) as ?mint__dataProviderUrl)
    }
}
union
{
    ?id owl:sameAs ?nomismaUri__id .
    bind(?nomismaUri__id as ?nomismaUri__prefLabel)
    bind(?nomismaUri__id as ?nomismaUri__dataProviderUrl)
}
`

export const localAdminUnitsInstanceProperties = `
{
    ?id rdfs:label ?name__id .
    bind(?name__id as ?name__prefLabel)
    bind(?id as ?uri__id)
    bind(?id as ?uri__prefLabel)
}
union
{
    ?coin__id nmd:hasLocalAdminUnit ?id .
    
    optional
    {
        ?coin__id nmo:hasAuthority ?authority__id .
        ?authority__id rdfs:label ?authority__prefLabel .
        bind(concat("/authorities/page/", STRAFTER(str(?authority__id), "ruler/")) as ?authority__dataProviderUrl)
    }
    
    optional
    {
        ?coin__id nmo:hasMaterial ?material__id .
        ?material__id skos:prefLabel ?material__prefLabel .
        bind(concat("/materials/page/", STRAFTER(str(?material__id), "material/")) as ?material__dataProviderUrl)
    }
}
`