export const mapPieChartFloat = sparqlBindings => {
  return sparqlBindings.map(b => ({
    category: b.category.value,
    prefLabel: b.prefLabel.value,
    instanceCount: Math.round(parseFloat(b.instanceCount.value))
  }))
}
