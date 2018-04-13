import logging
import urllib.request
import json
log = logging.getLogger('root')

class LocatorMapAdder():

	CACHE = {}

	def add(self, html, location):
		lat, lng = self._get_coords(location)
		return self._get_map(lat, lng) + html
		
	def _get_coords(self, location):
		if location not in self.CACHE:
			response = urllib.request.urlopen("https://api.digitransit.fi/geocoding/v1/search?text={}&size=1".format(location)).read()
			data = json.loads(response.decode('utf-8'))
			self.CACHE[location] = data['features'][0]['geometry']['coordinates']
		return self.CACHE[location]

	def _get_map(self, lat, lng):
		return """
			<link rel="stylesheet" href="https://unpkg.com/leaflet@1.3.1/dist/leaflet.css"
			integrity="sha512-Rksm5RenBEKSKFjgI3a41vrjkw4EVPlJ3+OiI65vTjIdo9brlAacEuKOiQ5OFh7cOI1bkDwLqdLw3Zg0cRJAAQ=="
			crossorigin=""/>
			<script src="https://unpkg.com/leaflet@1.3.1/dist/leaflet.js"
			integrity="sha512-/Nsx9X4HebavoBvEBuyp3I7od5tA0UzAxs+j83KgC8PU0kgB4XiK4Lfe4y4cgBtaRJQEIFCW+oC506aPT2L1zw=="
			crossorigin=""></script>
			<div style="float:right; width:300px; height:400px;margin:15px;" id="map"></div>
			<script>
				var map = L.map('map').setView([64.96, 27.33], 13);
				L.tileLayer('http://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
					attribution: 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
				}}).addTo(map);
				map.fitBounds([[71.801, 38.408], [57.040, 12.041]])
				L.marker([{}, {}]).addTo(map);
			</script>
		""".format(lng,lat)


