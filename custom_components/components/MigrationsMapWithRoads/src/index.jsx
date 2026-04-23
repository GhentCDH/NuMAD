import React from 'react'
import PropTypes from 'prop-types'
import { withStyles } from 'tss-react/mui'
import DeckGL from '@deck.gl/react'
import { ArcLayer } from '@deck.gl/layers'
import intl from 'react-intl-universal'

import ReactMapGL, { FullscreenControl, NavigationControl } from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'

import maplibregl from 'maplibre-gl'
import { Protocol } from 'pmtiles'
import { layers, namedFlavor } from '@protomaps/basemaps'

import {DeckArcLayerLegend, DeckArcLayerDialog, DeckArcLayerTooltip } from '@sampo-ui/components'
import CircularProgress from '@mui/material/CircularProgress'
import { useConfigsStore } from '@sampo-ui/configsStore'


const styles = (theme, props) => ({
    root: {
        height: 400,
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
    navigationContainer: {
        position: 'absolute',
        top: 0,
        left: 0,
        padding: theme.spacing(1),
        zIndex: 2
    },
    fullscreenButton: {
        position: 'absolute',
        top: 105
    },
    mapWrapper: {
        '& .maplibregl-ctrl-top-left': {
            pointerEvents: 'all',
            zIndex: 3
        },
        '& .maplibregl-ctrl-top-right': {
            pointerEvents: 'all',
            zIndex: 3
        }
    }
})

/**
 * A component for WebGL maps using deck.gl and ReactMapGL.
 */
class MigrationsMapWithRoads extends React.Component {
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
        dialog: {
            open: false,
            data: null,
            from: null,
            to: null
        },
        hoverInfo: null,
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
        // check if facets are still fetching
        let someFacetIsFetching = false

        // refetch default facets (excl. text facets) when facets have been updated
        if (this.state.defaultFacetFetchingRequired && this.props.facetUpdateID > 0 && !someFacetIsFetching) {
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

        // check if filters have changed
        if (prevProps.facetUpdateID !== this.props.facetUpdateID) {
            this.props.fetchResults({
                resultClass: this.props.resultClass,
                facetClass: this.props.facetClass,
                sortBy: null
            })
        }
    }

    setDialog = info => {
        this.setState({
            dialog: {
                open: true,
                from: info.object.from,
                to: info.object.to
            }
        })
        this.props.fetchInstanceAnalysis({
            resultClass: `${this.props.resultClass}Dialog`,
            facetClass: this.props.facetClass,
            fromID: info.object.from.id,
            toID: info.object.to.id
        })
    }

    closeDialog = () =>
        this.setState({
            dialog: {
                open: false,
                data: null
            }
        })

    handleOnViewportChange = viewport => {
        if (this.state.mounted) {
            this.setState({ viewport })
        }
    }

    renderSpinner () {
        if (this.props.fetching || this.props.data.fetchingInstanceAnalysisData) {
            return (
                <div className={this.props.classes.spinner}>
                    <CircularProgress />
                </div>
            )
        }
        return null
    }

    parseCoordinates = data => [+data.long, +data.lat]

    createArcLayer = data =>
        new ArcLayer({
            id: 'arc-layer',
            data,
            pickable: true,
            getWidth: 3,
            getSourceColor: [0, 0, 255, 255],
            getTargetColor: [255, 0, 0, 255],
            getSourcePosition: d => this.parseCoordinates(d.from),
            getTargetPosition: d => this.parseCoordinates(d.to),
            onClick: info => this.setDialog(info),
            onHover: info => this.setState({ hoverInfo: info }),
            autoHighlight: true
        })

    getMapStyle = () => {
        const { customTilesLayer, roadsGeoJson } = this.props.resultClassConfig

        if (customTilesLayer?.type === 'pmtiles') {
            const url = customTilesLayer.inConfig
                ? useConfigsStore.getState().getStaticFileUrl(customTilesLayer.url)
                : customTilesLayer.url

            const style = {
                version: 8,
                glyphs: 'https://protomaps.github.io/basemaps-assets/fonts/{fontstack}/{range}.pbf',
                sprite: 'https://protomaps.github.io/basemaps-assets/sprites/v4/light',
                sources: {
                    'pmtiles-source': { type: 'vector', url: `pmtiles://${url}` }
                },
                layers: layers('pmtiles-source', namedFlavor('light'), { lang: 'en' })
            }

            if (roadsGeoJson) {
                const roadsUrl = roadsGeoJson.inConfig
                    ? useConfigsStore.getState().getStaticFileUrl(roadsGeoJson.url)
                    : roadsGeoJson.url

                style.sources['roads-source'] = {
                    type: 'geojson',
                    data: roadsUrl
                }

                style.layers.push({
                    id: 'roads-layer',
                    type: 'line',
                    source: 'roads-source',
                    layout: {
                        'line-join': 'round',
                        'line-cap': 'round'
                    },
                    paint: {
                        'line-color': '#d32f2f',
                        'line-width': 1.5,
                        'line-opacity': 0.7
                    }
                })
            }

            return style
        }

        // fallback gray base
        return {
            version: 8,
            sources: {},
            layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#e0e0e0' } }]
        }
    }

    renderMap = (layer, showTooltip, hoverInfo) => {
        const { resultClass } = this.props
        const title = intl.get(`deckGlMap.${resultClass}.legendTitle`)
        const fromText = intl.get(`deckGlMap.${resultClass}.legendFrom`)
        const toText = intl.get(`deckGlMap.${resultClass}.legendTo`)
        const countText = intl.get(`deckGlMap.${resultClass}.count`)
        const listHeadingSingleInstance = intl.get(`deckGlMap.${resultClass}.listHeadingSingleInstance`)
        const listHeadingMultipleInstances = intl.get(`deckGlMap.${resultClass}.listHeadingMultipleInstances`)
        const showMoreText = intl.get('deckGlMap.showMoreInformation')

        return (
            <DeckGL
                viewState={this.state.viewport}
                controller
                layers={[layer]}
                onViewStateChange={({ viewState }) => this.handleOnViewportChange(viewState)}
                style={{ width: '100%', height: '100%', position: 'relative' }}
                getCursor={({ isDragging, isHovering }) => {
                    if (isDragging) return 'grabbing'
                    if (isHovering) return 'pointer'
                    return 'grab'
                }}
            >
                {/* ReactMapGL as a child — DeckGL passes it the map context automatically */}
                <ReactMapGL
                    reuseMaps
                    mapStyle={this.getMapStyle()}
                    preventStyleDiffing
                    style={{ width: '100%', height: '100%' }}
                >
                    <NavigationControl position='top-left' />
                    <FullscreenControl position='top-left' containerId='map-root' />
                </ReactMapGL>

                <DeckArcLayerLegend
                    title={title}
                    fromText={fromText}
                    toText={toText}
                />

                {this.props.data.instanceAnalysisData && this.state.dialog.open &&
                    <DeckArcLayerDialog
                        onClose={this.closeDialog.bind(this)}
                        data={this.props.data.instanceAnalysisData}
                        from={this.state.dialog.from}
                        to={this.state.dialog.to}
                        fromText={fromText}
                        toText={toText}
                        countText={countText}
                        listHeadingSingleInstance={listHeadingSingleInstance}
                        listHeadingMultipleInstances={listHeadingMultipleInstances}
                        instanceVariable={[this.props.resultClassConfig.instanceVariable]}
                        resultClass={this.props.resultClass}
                        facetClass={this.props.facetClass}
                    />}

                {showTooltip &&
                    <DeckArcLayerTooltip
                        data={hoverInfo}
                        fromText={fromText}
                        toText={toText}
                        countText={countText}
                        showMoreText={showMoreText}
                    />}

                {this.renderSpinner()}
            </DeckGL>
        )
    }

    render () {
        const { classes, fetching, results } = this.props
        const { showTooltips } = this.props.resultClassConfig
        const { hoverInfo } = this.state
        const showTooltip = showTooltips && hoverInfo && hoverInfo.object
        const hasData = !fetching && results && results.length > 0 &&
            (
                (results[0].lat && results[0].long) ||
                (results[0].from && results[0].to) ||
                results[0].polygon
            )

        /* It's OK to create a new Layer instance on every render
           https://github.com/uber/deck.gl/blob/master/docs/developer-guide/using-layers.md#should-i-be-creating-new-layers-on-every-render
          */
        let layer = null
        if (hasData) {
            layer = this.createArcLayer(results)
        }
        return (
            <div
                className={classes.root} ref={this.mapContainer} style={{ position: 'relative' }}
                onContextMenu={e => e.preventDefault()}
            >
                {this.renderMap(layer, showTooltip, hoverInfo)}

            </div>
        )
    }
}

MigrationsMapWithRoads.propTypes = {
    data: PropTypes.object.isRequired,
    results: PropTypes.array,
    fetching: PropTypes.bool,
    // Identity
    resultClass: PropTypes.string.isRequired,
    facetClass: PropTypes.string.isRequired,
    rootUrl: PropTypes.string.isRequired,
    // Config
    portalConfig: PropTypes.object,
    layoutConfig: PropTypes.object,
    perspectiveConfig: PropTypes.object,
    resultClassConfig: PropTypes.object,
    // Facet state
    facetState: PropTypes.object,
    facetUpdateID: PropTypes.number.isRequired,
    // UI
    screenSize: PropTypes.string,
    location: PropTypes.object,
    currentLocale: PropTypes.string,
    // Actions
    fetchPaginatedResults: PropTypes.func.isRequired,
    fetchResults: PropTypes.func,
    fetchByURI: PropTypes.func,
    fetchFacet: PropTypes.func,
    fetchInstanceAnalysis: PropTypes.func,
    updatePage: PropTypes.func.isRequired,
    updateRowsPerPage: PropTypes.func,
    updateFacetOption: PropTypes.func,
    sortResults: PropTypes.func.isRequired,
    showError: PropTypes.func
}

export default withStyles(MigrationsMapWithRoads, styles)
