import Vue from 'vue'
import Plotly from 'plotly.js-dist-min'

export default ({ app }, inject) => {
	inject('Plotly', Plotly)
}
