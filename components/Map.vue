<template>
	<div>
		<div class="content-wrapper map-intro">
			<p><strong>Click the map</strong> to pick a location.</p>
		</div>
		<div id="map"></div>
	</div>
</template>

<style lang="scss" scoped>
.map-intro {
	margin-bottom: 1.25rem;
}
#map {
	height: 100vh;
	width: 100vw;
}
</style>

<script>
import _ from 'lodash'

export default {
	name: 'Map',
	mounted() {
		this.map = L.map('map', this.getBaseMapAndLayers())
		new this.$L.Control.Zoom({ position: 'topright' }).addTo(this.map)

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
			this.$router.push({
				path: '/report/' + this.latlng.lat + '/' + this.latlng.lng,
				hash: '#results',
			})
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
