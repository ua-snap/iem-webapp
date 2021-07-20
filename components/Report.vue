<template>
	<div class="container">
		<section class="section">
			<b-button tag="nuxt-link" to="/">
				Go Back / Show Location Pickers</b-button
			>
			<h3 class="title is-4">
				Projected Future Conditions for <span v-html="place"></span>
			</h3>
			<div v-if="$fetchState.pending">
				<!-- Drama dots -->
				<h4 class="title is-5">Loading data&hellip;</h4>
			</div>
			<div v-else-if="$fetchState.error" class="error">
				<p>
					Oh no! Something&rsquo;s amiss and the report for this place
					couldn&rsquo;t be loaded.
				</p>
				<b-button tag="nuxt-link" to="/">
					Go back and try another place</b-button
				>
			</div>
			<div v-else>
				<TempReport></TempReport>
				<PrecipReport></PrecipReport>
			</div>
		</section>
	</div>
</template>
<style></style>
<script>
import TempReport from '~/components/TempReport'
import PrecipReport from '~/components/PrecipReport'
import { mapGetters } from 'vuex'

// For mocking/scaffolding only
function sleep(ms) {
	return new Promise((resolve) => setTimeout(resolve, ms))
}

export default {
	name: 'Report',
	components: { TempReport, PrecipReport },
	data() {
		return {
			results: undefined,
		}
	},
	computed: {
		...mapGetters({
			place: 'getPlaceName',
		}),
	},
	async fetch() {
		// Example doing real fetch: this.results = await this.$http.$get('https://api.nuxtjs.dev/mountains')
		await sleep(5000)
	},
}
</script>
