import React, { useState, useCallback, useEffect, useRef } from 'react'
import Map, { Source, Layer, Marker, NavigationControl } from 'react-map-gl/maplibre'
import maplibregl from 'maplibre-gl'
import { Protocol } from 'pmtiles'
import { layers, namedFlavor } from '@protomaps/basemaps'
import { useConfigsStore } from '@sampo-ui/configsStore'
import 'maplibre-gl/dist/maplibre-gl.css'

// Approximate a circle as a closed GeoJSON polygon
const circleGeoJSON = (center, radiusKm) => {
  const n = 64
  const coords = Array.from({ length: n }, (_, i) => {
    const a = (i / n) * 2 * Math.PI
    return [
      center[0] + (radiusKm / (111.32 * Math.cos(center[1] * Math.PI / 180))) * Math.cos(a),
      center[1] + (radiusKm / 110.574) * Math.sin(a)
    ]
  })
  coords.push(coords[0])
  return { type: 'Feature', geometry: { type: 'Polygon', coordinates: [coords] } }
}

// PMTiles protocol is global — register only once across remounts
let pmtilesRegistered = false

const RadiusMapFacet = ({
  facetID,
  facetClass,
  facetState,
  facet,
  updateFacetOption,
  clearFacet
}) => {
  const {
    initialLng = 10,
    initialLat = 50,
    initialZoom = 3,
    sliderMin = 1,
    sliderMax = 500,
    defaultRadiusKm = 100
  } = facet?.componentConfig ?? {}

  const saved = facetState?.facets?.[facetID]?.customFilter ?? null
  const [center, setCenter] = useState(saved ? [saved.lng, saved.lat] : null)
  const [radiusKm, setRadiusKm] = useState(saved?.radiusKm ?? defaultRadiusKm)
  const [dirty, setDirty] = useState(false)
  const [autoApply, setAutoApply] = useState(false)
  const autoApplyTimer = useRef(null)

  useEffect(() => {
    if (!pmtilesRegistered) {
      maplibregl.addProtocol('pmtiles', new Protocol().tile)
      pmtilesRegistered = true
    }
  }, [])

  useEffect(() => {
    if (saved === null) {
      setCenter(null)
      setDirty(false)
    }
  }, [saved])

  const tilesUrl = useConfigsStore.getState().getStaticFileUrl('maps/world.pmtiles')
  const mapStyle = {
    version: 8,
    glyphs: 'https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf',
    sprite: 'https://protomaps.github.io/basemaps-assets/sprites/v4/light',
    sources: { protomaps: { type: 'vector', url: `pmtiles://${tilesUrl}` } },
    layers: layers('protomaps', namedFlavor('light'), { lang: 'en' })
  }

  const dispatchFilter = useCallback((c, r) => {
    updateFacetOption({
      facetClass,
      facetID,
      option: 'customFilter',
      value: { lat: c[1], lng: c[0], radiusKm: r }
    })
  }, [facetClass, facetID, updateFacetOption])

  const scheduleAutoApply = useCallback((c, r) => {
    clearTimeout(autoApplyTimer.current)
    autoApplyTimer.current = setTimeout(() => {
      dispatchFilter(c, r)
      setDirty(false)
    }, 500)
  }, [dispatchFilter])

  const handleClick = useCallback((e) => {
    const c = [e.lngLat.lng, e.lngLat.lat]
    setCenter(c)
    setDirty(true)
    if (autoApply) scheduleAutoApply(c, radiusKm)
  }, [autoApply, radiusKm, scheduleAutoApply])

  const handleRadiusChange = useCallback((e) => {
    const r = Number(e.target.value)
    setRadiusKm(r)
    if (center) {
      setDirty(true)
      if (autoApply) scheduleAutoApply(center, r)
    }
  }, [center, autoApply, scheduleAutoApply])

  const handleSave = useCallback(() => {
    clearTimeout(autoApplyTimer.current)
    dispatchFilter(center, radiusKm)
    setDirty(false)
  }, [center, radiusKm, dispatchFilter])

  const handleClear = useCallback(() => {
    clearTimeout(autoApplyTimer.current)
    setCenter(null)
    setDirty(false)
    clearFacet({ facetClass, facetID })
  }, [facetClass, facetID, clearFacet])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, padding: '8px 4px', fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif' }}>
      <div style={{ height: 260, borderRadius: 4, overflow: 'hidden', cursor: 'crosshair' }}>
        <Map
          initialViewState={{ longitude: initialLng, latitude: initialLat, zoom: initialZoom }}
          mapStyle={mapStyle}
          onClick={handleClick}
          dragRotate={false}
          touchPitch={false}
          style={{ width: '100%', height: '100%' }}
        >
          <NavigationControl position="top-right" showCompass={false} />
          {center && (
            <Source type="geojson" data={circleGeoJSON(center, radiusKm)}>
              <Layer
                id="radius-fill"
                type="fill"
                paint={{ 'fill-color': '#1976d2', 'fill-opacity': 0.15 }}
              />
              <Layer
                id="radius-border"
                type="line"
                paint={{ 'line-color': '#1976d2', 'line-width': 2 }}
              />
            </Source>
          )}
          {center && <Marker longitude={center[0]} latitude={center[1]} />}
        </Map>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontSize: 12, whiteSpace: 'nowrap' }}>Radius:</span>
        <input
          type="range"
          min={sliderMin}
          max={sliderMax}
          value={radiusKm}
          onChange={handleRadiusChange}
          style={{ flex: 1 }}
        />
        <span style={{ fontSize: 12, minWidth: 55 }}>{radiusKm} km</span>
      </div>
      <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, cursor: 'pointer' }}>
        <input
          type="checkbox"
          checked={autoApply}
          onChange={e => setAutoApply(e.target.checked)}
        />
        Auto-apply
      </label>
      {center && dirty && (
        <button
          onClick={handleSave}
          style={{
            padding: '4px 8px',
            fontSize: 12,
            cursor: 'pointer',
            background: '#1976d2',
            color: '#fff',
            border: 'none',
            borderRadius: 4
          }}
        >
          Apply filter
        </button>
      )}
      {center && !dirty && (
        <button
          onClick={handleClear}
          style={{
            padding: '4px 8px',
            fontSize: 12,
            cursor: 'pointer',
            background: '#f5f5f5',
            border: '1px solid #ccc',
            borderRadius: 4
          }}
        >
          Clear filter
        </button>
      )}
      {!center && (
        <span style={{ fontSize: 11, color: '#888', textAlign: 'center' }}>
          Click the map to set a center point
        </span>
      )}
    </div>
  )
}

export default RadiusMapFacet
