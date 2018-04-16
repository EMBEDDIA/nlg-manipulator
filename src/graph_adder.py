import logging
import urllib.request
import urllib.parse
import json
import numpy as np
from math import cos, sqrt
log = logging.getLogger('root')

class GraphAdder():

	def add(self, registry, html, location):
		if location in ['Suomi', 'Finland']:
			return html

		labels, datasets = self._get_data(location, registry)
		return html + self._get_graph(labels, datasets)

	def _get_data(self, location, registry):
		datastore = registry.get('crime-bc-data')
		cols = [c for c in datastore.all() if c in ['where', 'when', 'all_total_normalized']]

		# get data
		location_df = datastore.query('where=={!r} and when_type=="month" and where_type=="M"'.format(location))[cols]
		elsewhere_df = datastore.query('where!={!r} and when_type=="month" and where_type=="M"'.format(location))[cols]

		location_df = location_df[location_df['when'].str.contains("(2015|2016|2017|2018)")]
		elsewhere_df = elsewhere_df[elsewhere_df['when'].str.contains("(2015|2016|2017|2018)")]

		# Drop infs & nans, group by 'when', get means
		location_df = location_df.replace([np.inf, -np.inf], np.nan) \
			.dropna(how="any") \
			.groupby(['when'], as_index=False) \
			.mean()

		elsewhere_df = elsewhere_df.replace([np.inf, -np.inf], np.nan) \
			.dropna(how="any") \
			.groupby(['when'], as_index=False) \
			.mean()

		# Should be same columns in both dataframes
		labels = list(location_df['when'])
		datasets = [
			{
				'label': location,
				'data': list(location_df['all_total_normalized']),
				'backgroundColor': 'rgba(205, 170, 152, 0.2)',
				'borderColor': 'rgba(205, 170, 152, 1)',
			},
			{
				'label': 'Muiden kuntien keskiarvo',
				'data': list(elsewhere_df['all_total_normalized']),
				'backgroundColor': 'rgba(151, 187, 205, 0.2)',
				'borderColor': 'rgba(151, 187, 205, 1)',
			}
		]

		return json.dumps(labels), json.dumps(datasets)

	def _get_graph(self, labels, datasets):
		return """
			<div style="max-width: 500px; max-height: 500px; float:left; clear:right;">
				<canvas id="chart" width="500" height="500"></canvas>
				<script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.22.1/moment.min.js"></script>
				<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.2/Chart.min.js"></script>
				<script>
					var chart = new Chart(
						document.getElementById('chart'), 
						{{
							type: 'line',
							data: {{
								labels: {labels},
								datasets: {datasets}
							}},
							options: {{
								title: {{
									display: true,
									text: 'Rikoksia tuhatta asukasta kohden'
								}}
							}}
						}}
					)
				</script>
			</div>
		""".format(labels=labels, datasets=datasets)
