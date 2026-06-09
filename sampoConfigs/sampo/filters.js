// Custom filter functions for NuMAD.
// Each export is available as filterType "customFilter" + customFilterName in perspective configs.
//
// Signature:
//   ({ backendSearchConfig, facetClass, facetID, filterTarget, values, inverse }) => string

export const localAdminUnitRadiusFilter = ({ filterTarget, values }) => {
  const { lat, lng, radiusKm } = values
  const radiusM = radiusKm * 1000
  return `
    ?${filterTarget} nmo:hasFindContext ?_findForRadius .
    ?_findForRadius nmd:hasLocalAdminUnit ?_lauForRadius .
    ?_lauForRadius schema:geo ?_lauGeoForRadius .
    ?_lauGeoForRadius geo:asWKT ?_lauWktForRadius .
    FILTER(geof:distance(?_lauWktForRadius, "POINT(${lng} ${lat})"^^geo:wktLiteral, uom:metre) <= ${radiusM})
  `
}

export const localAdminUnitRadiusFilterFinds = ({ filterTarget, values }) => {
  const { lat, lng, radiusKm } = values
  const radiusM = radiusKm * 1000
  return `
    ?${filterTarget} nmd:hasLocalAdminUnit ?_lauForRadius .
    ?_lauForRadius schema:geo ?_lauGeoForRadius .
    ?_lauGeoForRadius geo:asWKT ?_lauWktForRadius .
    FILTER(geof:distance(?_lauWktForRadius, "POINT(${lng} ${lat})"^^geo:wktLiteral, uom:metre) <= ${radiusM})
  `
}
