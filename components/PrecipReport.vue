<template>
	<div>
		<h4 class="subtitle is-4">
			Precipitation
			<span class="units">
				<span v-if="units == 'imperial'">(inches)</span>
				<span v-if="units == 'metric'">(mm)</span>
			</span>
		</h4>
		<div class="content-placeholder">
			What text might go here, introducing Precipitation?
		</div>
		<table class="table" v-if="reportData">
			<thead>
				<tr>
					<th scope="col" colspan="2"></th>
					<th scope="col" colspan="4">2040&ndash;2070</th>
					<th scope="col" colspan="4">2070&ndash;2100</th>
				</tr>
				<tr>
					<th scope="col" colspan="2"></th>
					<th scope="col" colspan="2">RCP4.5</th>
					<th scope="col" colspan="2">RCP8.5</th>
					<th scope="col" colspan="2">RCP4.5</th>
					<th scope="col" colspan="2">RCP8.5</th>
				</tr>
				<tr>
					<th scope="col">Season</th>
					<th scope="col">Historical Average</th>
					<th scope="col">MRI-CGCM3</th>
					<th scope="col">NCAR-CCSM4</th>
					<th scope="col">MRI-CGCM3</th>
					<th scope="col">NCAR-CCSM4</th>
					<th scope="col">MRI-CGCM3</th>
					<th scope="col">NCAR-CCSM4</th>
					<th scope="col">MRI-CGCM3</th>
					<th scope="col">NCAR-CCSM4</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<th scope="row">DJF</th>
					<td>1</td>
					<td>
						{{ reportData['2040_2070']['DJF']['MRI-CGCM3']['rcp45']['pr'] }}
					</td>
					<td>{{ reportData['2040_2070']['DJF']['CCSM4']['rcp45']['pr'] }}</td>
					<td>
						{{ reportData['2040_2070']['DJF']['MRI-CGCM3']['rcp85']['pr'] }}
					</td>
					<td>{{ reportData['2040_2070']['DJF']['CCSM4']['rcp85']['pr'] }}</td>
					<td>
						{{ reportData['2070_2100']['DJF']['MRI-CGCM3']['rcp45']['pr'] }}
					</td>
					<td>{{ reportData['2070_2100']['DJF']['CCSM4']['rcp45']['pr'] }}</td>
					<td>
						{{ reportData['2070_2100']['DJF']['MRI-CGCM3']['rcp85']['pr'] }}
					</td>
					<td>{{ reportData['2070_2100']['DJF']['CCSM4']['rcp85']['pr'] }}</td>
				</tr>
				<tr>
					<th scope="row">MAM</th>
					<td>1</td>
					<td>
						{{ reportData['2040_2070']['MAM']['MRI-CGCM3']['rcp45']['pr'] }}
					</td>
					<td>{{ reportData['2040_2070']['MAM']['CCSM4']['rcp45']['pr'] }}</td>
					<td>
						{{ reportData['2040_2070']['MAM']['MRI-CGCM3']['rcp85']['pr'] }}
					</td>
					<td>{{ reportData['2040_2070']['MAM']['CCSM4']['rcp85']['pr'] }}</td>
					<td>
						{{ reportData['2070_2100']['MAM']['MRI-CGCM3']['rcp45']['pr'] }}
					</td>
					<td>{{ reportData['2070_2100']['MAM']['CCSM4']['rcp45']['pr'] }}</td>
					<td>
						{{ reportData['2070_2100']['MAM']['MRI-CGCM3']['rcp85']['pr'] }}
					</td>
					<td>{{ reportData['2070_2100']['MAM']['CCSM4']['rcp85']['pr'] }}</td>
				</tr>
				<tr>
					<th scope="row">JJA</th>
					<td>1</td>
					<td>
						{{ reportData['2040_2070']['JJA']['MRI-CGCM3']['rcp45']['pr'] }}
					</td>
					<td>{{ reportData['2040_2070']['JJA']['CCSM4']['rcp45']['pr'] }}</td>
					<td>
						{{ reportData['2040_2070']['JJA']['MRI-CGCM3']['rcp85']['pr'] }}
					</td>
					<td>{{ reportData['2040_2070']['JJA']['CCSM4']['rcp85']['pr'] }}</td>
					<td>
						{{ reportData['2070_2100']['JJA']['MRI-CGCM3']['rcp45']['pr'] }}
					</td>
					<td>{{ reportData['2070_2100']['JJA']['CCSM4']['rcp45']['pr'] }}</td>
					<td>
						{{ reportData['2070_2100']['JJA']['MRI-CGCM3']['rcp85']['pr'] }}
					</td>
					<td>{{ reportData['2070_2100']['JJA']['CCSM4']['rcp85']['pr'] }}</td>
				</tr>
				<tr>
					<th scope="row">SON</th>
					<td>1</td>
					<td>
						{{ reportData['2040_2070']['SON']['MRI-CGCM3']['rcp45']['pr'] }}
					</td>
					<td>{{ reportData['2040_2070']['SON']['CCSM4']['rcp45']['pr'] }}</td>
					<td>
						{{ reportData['2040_2070']['SON']['MRI-CGCM3']['rcp85']['pr'] }}
					</td>
					<td>{{ reportData['2040_2070']['SON']['CCSM4']['rcp85']['pr'] }}</td>
					<td>
						{{ reportData['2070_2100']['SON']['MRI-CGCM3']['rcp45']['pr'] }}
					</td>
					<td>{{ reportData['2070_2100']['SON']['CCSM4']['rcp45']['pr'] }}</td>
					<td>
						{{ reportData['2070_2100']['SON']['MRI-CGCM3']['rcp85']['pr'] }}
					</td>
					<td>{{ reportData['2070_2100']['SON']['CCSM4']['rcp85']['pr'] }}</td>
				</tr>
			</tbody>
		</table>
	</div>
</template>
<style></style>
<script>
export default {
	name: 'PrecipReport',
	props: ['reportData', 'units'],
}
</script>
