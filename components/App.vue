<template>
  <div>
    <client-only>
      <div v-show="!this.reportIsVisible" class="place-selector">
        <div class="container">
          <section class="section">
            <div class="content controls" id="controls">
              <!-- ID is used as anchor target, don't remove -->
              <PlaceSelector></PlaceSelector>
            </div>
          </section>
        </div>
        <!-- Map can't be wrapped in container/section, if we want it full-screen. -->
        <Map></Map>
      </div>
      <div v-show="this.reportIsVisible" class="report-wrapper">
        <Report></Report>
      </div>
    </client-only>
  </div>
</template>
<style lang="scss" scoped>
.content.controls {
  max-width: 50rem;
  margin-left: auto;
  margin-right: auto;
  padding-top: 2rem;
  margin-top: -2rem;
}
</style>
<script>
import Map from '~/components/Map'
import Report from '~/components/Report'
import PlaceSelector from '~/components/PlaceSelector'

import { mapGetters } from 'vuex'

export default {
  name: 'App',
  components: {
    Map,
    Report,
  },
  computed: {
    ...mapGetters(['reportIsVisible']),
  },
}
</script>
