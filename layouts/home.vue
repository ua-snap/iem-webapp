<template>
  <div>
    <HeaderBanner />

    <div class="splash-title columns">
      <div class="splash-title-text column is-half">
        <div>
          <h1>Climate<br />Impact<br />Reports</h1>
          <h2>for Changing<br />Northern Ecosystems</h2>
        </div>
      </div>
      <div class="splash-title-image column is-half"></div>
    </div>

    <nuxt />

    <Footer />
  </div>
</template>

<style lang="scss" scoped>
.splash-title {
  height: 75vh;
  margin-top: 0;
  font-family: 'Paytone One';
  color: #000;

  .splash-title-text {
    display: flex;
    align-items: center;
    text-align: center;
    & div {
      width: 100%;

      h1 {
      font-size: 5.5rem;
      line-height: 1;
      }
      h2 {
        margin-top: 1.25rem;
        text-transform: uppercase;
        font-size: 1.6rem;
        letter-spacing: 0.35rem;
        line-height: 1.8;
      }
    }
  }
  .splash-title-image {
    background-image: url('~/assets/images/river-mts-bw.png');
    background-size: cover;
  }
}
</style>

<script>
import HeaderBanner from '~/components/HeaderBanner'
import Footer from '~/components/Footer'
export default {
  components: { Footer, HeaderBanner },
}
</script>
