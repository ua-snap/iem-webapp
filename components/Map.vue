<template>
	<div id="map"></div>
</template>

<script>
import _ from 'lodash'

export default {
	name: 'Map',
	mounted() {
		this.map = L.map('map', this.getBaseMapAndLayers())
		new this.$L.Control.Zoom({ position: 'topright' }).addTo(this.map)

		this.layer = this.$L.tileLayer.wms(process.env.rasdamanUrl, {
			transparent: true,
			srs: 'EPSG:3338',
			format: 'image/png',
			version: '1.3.0',
			layers: ['iem_temp_precip_wms'],
			styles: 'iem_temp_ccsm4_rcp85_2070-2100',
			continuousWorld: true,
		})

		this.map.addLayer(this.layer)

		this.map.on('click', this.handleMapClick)
	},
	data() {
		return {
			// Currently selected lat/lon on the map.
			latlng: undefined,
		}
	},
	methods: {
		handleMapClick(event) {
			this.latlng = {
				lat: event.latlng.lat.toFixed(4),
				lng: event.latlng.lng.toFixed(4),
			}
			this.$router.push('/report/' + this.latlng.lat + '/' + this.latlng.lng)
		},
		getBaseMapAndLayers() {
			var baseLayer = new this.$L.tileLayer.wms(process.env.geoserverUrl, {
				transparent: true,
				srs: 'EPSG:3338',
				format: 'image/png',
				version: '1.3.0',
				layers: ['atlas_mapproxy:alaska_osm'],
			})

			// Projection definition.
			var proj = new this.$L.Proj.CRS(
				'EPSG:3338',
				'+proj=aea +lat_1=55 +lat_2=65 +lat_0=50 +lon_0=-154 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs',
				{
					resolutions: [4096, 2048, 1024, 512, 256, 128, 64],
				}
			)

			// Map base configuration
			var config = {
				zoom: 1,
				minZoom: 0,
				maxZoom: 6,
				center: [64.7, -155],
				scrollWheelZoom: false,
				crs: proj,
				continuousWorld: true,
				zoomControl: false,
				doubleClickZoom: false,
				attributionControl: false,
				layers: [baseLayer],
			}

			return config
		},
	},
}
</script>

<style>
#map {
	height: 100vh;
	width: 100vw;
}
</style>
