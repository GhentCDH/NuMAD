import React from 'react'
import PropTypes from 'prop-types'
import { withStyles } from 'tss-react/mui'
import { MapboxOverlay as DeckOverlay } from '@deck.gl/mapbox'
import { ScatterplotLayer, TextLayer } from '@deck.gl/layers'

import { Map, useControl, FullscreenControl, NavigationControl } from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'

import maplibregl from 'maplibre-gl'
import { Protocol } from 'pmtiles'
import { layers, namedFlavor } from '@protomaps/basemaps'
import { Link } from 'react-router-dom'

import CircularProgress from '@mui/material/CircularProgress'
import { useConfigsStore } from '@sampo-ui/configsStore'

const styles = (theme, props) => ({
    root: {
        height: 400,
        fontFamily: theme.typography.fontFamily,
        [theme.breakpoints.up(props.layoutConfig.hundredPercentHeightBreakPoint)]: {
            height: `calc(100% - ${props.layoutConfig.tabHeight}px)`
        }
    },
    spinner: {
        height: 40,
        width: 40,
        position: 'absolute',
        left: '50%',
        top: '50%',
        transform: 'translate(-50%,-50%)'
    },
    popup: {
        position: 'absolute',
        zIndex: 9,
        background: '#fff',
        border: '1px solid #ccc',
        borderRadius: 4,
        boxShadow: '0 2px 8px rgba(0,0,0,0.25)',
        padding: '10px 14px',
        minWidth: 160,
        maxWidth: 260,
        fontSize: 14,
        lineHeight: 1.5,
        '& h3': {
            margin: '0 0 4px 0',
            fontSize: 15,
            fontWeight: 600
        },
        '& a': {
            color: '#1565c0',
            textDecoration: 'underline',
            cursor: 'pointer'
        },
        '& .close-btn': {
            position: 'absolute',
            top: 4,
            right: 8,
            cursor: 'pointer',
            fontSize: 16,
            color: '#666',
            background: 'none',
            border: 'none',
            lineHeight: 1
        }
    }
})

const circleColor = n => {
    if (n >= 100) return [202, 0, 32, 220]
    if (n >= 10)  return [252, 141, 89, 220]
    return [26, 150, 65, 220]
}

/**
 * Renders deck.gl layers as an overlay on top of the maplibre map. Keeping deck.gl
 * as a MapboxOverlay child of <Map> (instead of wrapping <Map> in <DeckGL>) leaves
 * the maplibre controls in the map's own DOM so they stay clickable.
 */
function DeckGLOverlay (props) {
    const overlay = useControl(() => new DeckOverlay(props))
    overlay.setProps(props)
    return null
}

class MintsCoinCountMap extends React.Component {
    mapConfig = this.props.perspectiveConfig.maps[this.props.resultClass]
    state = {
        viewport: {
            longitude: this.mapConfig.center[1],
            latitude: this.mapConfig.center[0],
            zoom: this.mapConfig.zoom,
            pitch: 0,
            bearing: 0,
            width: 100,
            height: 100
        },
        hoverInfo: null,
        clickInfo: null,
        defaultFacetFetchingRequired: false
    }

    mapContainer = React.createRef()

    componentDidMount = () => {
        if (this.props.resultClassConfig.customTilesLayer?.type === 'pmtiles') {
            const protocol = new Protocol()
            maplibregl.addProtocol('pmtiles', protocol.tile)
        }
        this.props.fetchResults({
            resultClass: this.props.resultClass,
            facetClass: this.props.facetClass,
            sortBy: null
        })
        this.setState({ mounted: true })
    }

    componentWillUnmount = () => {
        if (this.props.resultClassConfig.customTilesLayer?.type === 'pmtiles') {
            maplibregl.removeProtocol('pmtiles')
        }
    }

    componentDidUpdate = prevProps => {
        if (this.state.defaultFacetFetchingRequired && this.props.facetUpdateID > 0) {
            const defaultFacets = this.props.perspectiveConfig.defaultActiveFacets
            for (const facet of defaultFacets) {
                if (this.props.perspectiveConfig.facets[facet].filterType !== 'textFilter') {
                    this.props.fetchFacet({
                        facetClass: this.props.facetClass,
                        facetID: facet
                    })
                }
            }
            this.setState({ defaultFacetFetchingRequired: false })
        }

        if (prevProps.facetUpdateID !== this.props.facetUpdateID) {
            this.props.fetchResults({
                resultClass: this.props.resultClass,
                facetClass: this.props.facetClass,
                sortBy: null
            })
        }
    }

    handleOnViewportChange = viewport => {
        if (this.state.mounted) {
            this.setState({ viewport })
        }
    }

    createScatterLayer = data => {
        const MIN_RADIUS = 14
        const MAX_RADIUS = 50
        const maxCount = Math.max(...data.map(d => +d.instanceCount), 1)

        return new ScatterplotLayer({
            id: 'scatter-layer',
            data,
            pickable: true,
            stroked: true,
            filled: true,
            radiusUnits: 'pixels',
            getPosition: d => [+d.long, +d.lat],
            getRadius: d => MIN_RADIUS + ((+d.instanceCount / maxCount) * (MAX_RADIUS - MIN_RADIUS)),
            getFillColor: d => circleColor(+d.instanceCount),
            getLineColor: [255, 255, 255, 200],
            lineWidthMinPixels: 2,
            onClick: info => { info.object && this.setState({ clickInfo: info }) },
            onHover: info => this.setState({ hoverInfo: info }),
            autoHighlight: true
        })
    }

    createTextLayer = data =>
        new TextLayer({
            id: 'text-layer',
            data,
            getPosition: d => [+d.long, +d.lat],
            getText: d => String(d.instanceCount),
            getSize: 13,
            getColor: [255, 255, 255, 255],
            fontWeight: 'bold',
            getTextAnchor: 'middle',
            getAlignmentBaseline: 'center'
        })

    getMapStyle = () => {
        const { customTilesLayer } = this.props.resultClassConfig

        if (customTilesLayer?.type === 'pmtiles') {
            const url = customTilesLayer.inConfig
                ? useConfigsStore.getState().getStaticFileUrl(customTilesLayer.url)
                : customTilesLayer.url

            return {
                version: 8,
                glyphs: 'https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf',
                sprite: 'https://protomaps.github.io/basemaps-assets/sprites/v4/light',
                sources: {
                    'pmtiles-source': { type: 'vector', url: `pmtiles://${url}` }
                },
                layers: layers('pmtiles-source', namedFlavor('light'), { lang: 'en' })
            }
        }

        return {
            version: 8,
            sources: {},
            layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#e0e0e0' } }]
        }
    }

    renderPopup = () => {
        const { clickInfo } = this.state
        if (!clickInfo || !clickInfo.object) return null
        const { x, y, object } = clickInfo
        const localId = object.id ? object.id.split('/mint/')[1] : null
        return (
            <div
                className={this.props.classes.popup}
                style={{ left: x + 12, top: y - 10 }}
            >
                <button
                    className='close-btn'
                    onClick={e => { e.stopPropagation(); this.setState({ clickInfo: null }) }}
                >×</button>
                <h3>
                    {localId
                        ? <Link to={`${this.props.rootUrl}/mints/page/${localId}`}>{object.prefLabel}</Link>
                        : object.prefLabel}
                </h3>
                {object.instanceCount} coins
            </div>
        )
    }

    renderSpinner = () => {
        if (this.props.fetching) {
            return (
                <div className={this.props.classes.spinner}>
                    <CircularProgress />
                </div>
            )
        }
        return null
    }

    render () {
        const { classes, fetching, results } = this.props
        const { viewport } = this.state

        const hasData = !fetching && results && results.length > 0 && results[0].lat && results[0].long

        const layerList = hasData
            ? [this.createScatterLayer(results), this.createTextLayer(results)]
            : []

        return (
            <div
                className={classes.root}
                ref={this.mapContainer}
                style={{ position: 'relative' }}
                onContextMenu={e => e.preventDefault()}
            >
                <Map
                    reuseMaps
                    mapStyle={this.getMapStyle()}
                    initialViewState={viewport}
                    onMove={evt => this.handleOnViewportChange(evt.viewState)}
                    attributionControl={false}
                    style={{ width: '100%', height: '100%', zIndex: 0 }}
                >
                    <DeckGLOverlay
                        layers={layerList}
                        onClick={info => { if (!info.object) this.setState({ clickInfo: null }) }}
                    />
                    <NavigationControl position='top-left' />
                    <FullscreenControl position='top-left' />
                    {this.renderSpinner()}
                </Map>
                {this.renderPopup()}
            </div>
        )
    }
}

MintsCoinCountMap.propTypes = {
    data: PropTypes.object.isRequired,
    results: PropTypes.array,
    fetching: PropTypes.bool,
    resultClass: PropTypes.string.isRequired,
    facetClass: PropTypes.string.isRequired,
    rootUrl: PropTypes.string.isRequired,
    portalConfig: PropTypes.object,
    layoutConfig: PropTypes.object,
    perspectiveConfig: PropTypes.object,
    resultClassConfig: PropTypes.object,
    facetState: PropTypes.object,
    facetUpdateID: PropTypes.number.isRequired,
    screenSize: PropTypes.string,
    location: PropTypes.object,
    currentLocale: PropTypes.string,
    fetchPaginatedResults: PropTypes.func.isRequired,
    fetchResults: PropTypes.func,
    fetchByURI: PropTypes.func,
    fetchFacet: PropTypes.func,
    updatePage: PropTypes.func.isRequired,
    updateRowsPerPage: PropTypes.func,
    updateFacetOption: PropTypes.func,
    sortResults: PropTypes.func.isRequired,
    showError: PropTypes.func
}

export default withStyles(MintsCoinCountMap, styles)
