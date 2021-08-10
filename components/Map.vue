<template>
	<div>
		<section class="section">
			
			<h2 class="title is-4">
				{{ variables[variable] }}, {{ models[model] }},
				{{ scenarios[scenario] }}, {{ periods[period] }},
				{{ seasons[season].title }}
			</h2>

			<div class="columns">
				<div class="column is-one-third">
					<b-field label="Variable">
						<b-radio-button
							v-model="variable"
							:native-value="0"
							name="variable"
							type="is-primary is-light is-outlined"
						>
							<span>Temperature</span>
						</b-radio-button>

						<b-radio-button
							v-model="variable"
							:native-value="1"
							name="variable"
							type="is-primary is-light is-outlined"
						>
							<span>Precipitation</span>
						</b-radio-button>
					</b-field>

					<b-field label="Model">
						<b-radio-button
							v-model="model"
							name="model"
							:native-value="0"
							type="is-primary is-light is-outlined"
						>
							<span>NCAR-CCSM4</span>
						</b-radio-button>

						<b-radio-button
							v-model="model"
							:native-value="1"
							name="model"
							type="is-primary is-light is-outlined"
						>
							<span>MRI-CGCM3</span>
						</b-radio-button>
					</b-field>

					<b-field label="Scenario">
						<b-radio-button
							v-model="scenario"
							:native-value="0"
							type="is-primary is-light is-outlined"
						>
							<span>RCP 4.5</span>
						</b-radio-button>

						<b-radio-button
							v-model="scenario"
							:native-value="2"
							type="is-primary is-light is-outlined"
						>
							<span>RCP 8.5</span>
						</b-radio-button>
					</b-field>

					<b-field label="Time Period">
						<b-radio-button
							v-model="period"
							:native-value="0"
							type="is-primary is-light is-outlined"
						>
							<span>2040&ndash;2070</span>
						</b-radio-button>

						<b-radio-button
							v-model="period"
							:native-value="1"
							type="is-primary is-light is-outlined"
						>
							<span>2070&ndash;2100</span>
						</b-radio-button>
					</b-field>

					<b-field label="Season">
						<b-select v-model="season" placeholder="Select a season">
							<option
								v-for="option in seasons"
								:value="option.id"
								:key="option.id"
							>
								{{ option.title }}
							</option>
						</b-select>
					</b-field>
				</div>
				<div class="column is-two-thirds">
					<div id="map"></div>
				</div>
			</div>
		</section>
	</div>
</template>

<script>
import _ from 'lodash'

export default {
	name: 'Map',
	mounted() {
		this.map = L.map('map', this.getBaseMapAndLayers())
		new this.$L.Control.Zoom({ position: 'topright' }).addTo(this.map)
		this.updateLayer()
		this.map.on('click', this.handleMapClick)
	},
	data() {
		return {
			// Currently selected lat/lon on the map.
			latlng: undefined,
			// Current Leaflet layer object
			layer: undefined,

			// Variables for picking map layers
			seasons: [
				{ id: 0, title: 'Winter (December, January, February)' },
				{ id: 1, title: 'Spring (March, April, May)' },
				{ id: 2, title: 'Summer (June, July, August)' },
				{ id: 3, title: 'Fall (September, October, November)' },
			],
			variables: {
				0: 'Temperature',
				1: 'Precipitation',
			},
			variableStyles: { // For picking the right Rasdaman style in WMS query
				0: 'temperature',
				1: 'precipitation'
			},
			models: {
				0: 'NCAR-CCSM4',
				1: 'MRI-CGCM3',
			},
			scenarios: {
				0: 'RCP 4.5',
				2: 'RCP 8.5',
			},
			periods: {
				0: '2040-2070',
				1: '2070-2100',
			},
			season: 0,
			variable: 0, // temperature
			model: 0,
			scenario: 0,
			period: 0,
		}
	},
	computed: {
		wmsLayerConfig() {
			return {
				transparent: true,
				srs: 'EPSG:3338',
				format: 'image/png',
				version: '1.3.0',
				layers: ['iem_temp_precip_wms'],
				styles: this.variableStyles[this.variable],
				dim_scenario: this.scenario,
				dim_model: this.model,
				dim_period: this.period,
				dim_season: this.season,
			}
		},
	},
	watch: {
		wmsLayerConfig: function () {
			this.updateLayer()
		},
	},
	methods: {
		updateLayer() {
			if (this.layer === undefined) {
				this.layer = this.$L.tileLayer.wms(
					process.env.rasdamanUrl,
					this.wmsLayerConfig
				)
				this.map.addLayer(this.layer)
			} else {
				this.layer.setParams(this.wmsLayerConfig, false)
			}
		},
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
				center: [64, -148],
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
