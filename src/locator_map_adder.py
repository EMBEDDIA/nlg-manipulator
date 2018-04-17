import logging
import urllib.request
import urllib.parse
import json
from math import cos, sqrt
log = logging.getLogger('root')

class LocatorMapAdder():
	REFERENCES =[
		{"latitude":60.170, "longitude":24.940, "name":"Helsinki"},
		{"latitude":60.210, "longitude":24.660, "name":"Espoo"},
		{"latitude":61.520, "longitude":23.760, "name":"Tampere"},
		{"latitude":60.450, "longitude":22.250, "name":"Turku"},
		{"latitude":65.020, "longitude":25.470, "name":"Oulu"},
		{"latitude":60.990, "longitude":25.660, "name":"Lahti"},
		{"latitude":62.900, "longitude":27.700, "name":"Kuopio"},
		{"latitude":62.260, "longitude":25.750, "name":"Jyväskylä"},
		{"latitude":61.490, "longitude":21.770, "name":"Pori"},
		{"latitude":61.060, "longitude":28.180, "name":"Lappeenranta"},
		{"latitude":63.100, "longitude":21.610, "name":"Vaasa"},
		{"latitude":60.470, "longitude":26.930, "name":"Kotka"},
		{"latitude":62.610, "longitude":29.780, "name":"Joensuu"},
		{"latitude":61.000, "longitude":24.450, "name":"Hämeenlinna"},
		{"latitude":60.390, "longitude":25.660, "name":"Porvoo"},
		{"latitude":61.700, "longitude":27.260, "name":"Mikkeli"},
		{"latitude":60.640, "longitude":24.870, "name":"Hyvinkää"},
		{"latitude":61.130, "longitude":21.520, "name":"Rauma"},
		{"latitude":66.490, "longitude":25.700, "name":"Rovaniemi"},
		{"latitude":60.250, "longitude":24.080, "name":"Lohja"},
		{"latitude":63.840, "longitude":23.120, "name":"Kokkola"},
		{"latitude":64.230, "longitude":27.730, "name":"Kajaani"},
		{"latitude":60.880, "longitude":26.700, "name":"Kouvola"},
		{"latitude":61.180, "longitude":28.760, "name":"Imatra"},
		{"latitude":60.470, "longitude":24.790, "name":"Nurmijärvi"},
		{"latitude":62.790, "longitude":22.840, "name":"Seinäjoki"},
		{"latitude":61.870, "longitude":28.910, "name":"Savonlinna"},
		{"latitude":61.490, "longitude":23.480, "name":"Nokia"},
		{"latitude":60.740, "longitude":24.790, "name":"Riihimäki"},
		{"latitude":60.420, "longitude":24.330, "name":"Vihti"},
		{"latitude":60.390, "longitude":23.130, "name":"Salo"},
		{"latitude":63.570, "longitude":27.180, "name":"Iisalmi"},
		{"latitude":62.320, "longitude":27.910, "name":"Varkaus"},
		{"latitude":65.760, "longitude":24.550, "name":"Kemi"},
		{"latitude":65.860, "longitude":24.170, "name":"Tornio"},
		{"latitude":65.960, "longitude":29.180, "name":"Kuusamo"},
		{"latitude":63.320, "longitude":30.040, "name":"Lieksa"},
		{"latitude":60.470, "longitude":22.020, "name":"Naantali"},
		{"latitude":60.570, "longitude":27.210, "name":"Hamina"},
	]
	CACHE = {}

	def add(self, html, location):
		# For reference points themselves, show map of whole country
		for reference in self.REFERENCES:
			if location == reference['name']:
				return self._get_map_country(reference['latitude'], reference['longitude']) + html

		# For other locations, show map zoomed to self and nearest reference
		location_lat, location_lng = self._get_coords(location)
		reference_lat, reference_lng = self._get_nearest_reference_coords(location_lat, location_lng)
		return self._get_map(location_lat, location_lng, reference_lat, reference_lng) + html

	def _distance(self, lat1, lng1, lat2, lng2):
		x = (lng1 - lng2) * cos((lat1 + lat2) / 2)
		y = (lat1 - lat2)
		return sqrt(x**2 + y**2) * 6371000

	def _get_nearest_reference_coords(self, lat, lng):
		closest_reference = self.REFERENCES[0]
		min_distance = self._distance(lat, lng, closest_reference['latitude'], closest_reference['longitude'])
		for reference in self.REFERENCES[1:]:
			distance = self._distance(lat, lng, reference['latitude'], reference['longitude'])
			if distance < min_distance:
				min_distance = distance
				closest_reference = reference
		return (closest_reference['latitude'], closest_reference['longitude'])
		
	def _get_coords(self, location):
		if location not in self.CACHE:
			url = "https://api.digitransit.fi/geocoding/v1/search?text={}&layers=localAdmin&size=1".format(urllib.parse.quote(location))
			response = urllib.request.urlopen(url).read()
			data = json.loads(response.decode('utf-8'))
			self.CACHE[location] = data['features'][0]['geometry']['coordinates'][1], data['features'][0]['geometry']['coordinates'][0]
		return self.CACHE[location]

	def _get_map_country(self, location_lat, location_lng):
		return """
			<div style="float:right; width:300px; height:400px; margin:15px;" id="map"></div>
			<script>
			function createMap() {{
				// Create map
				var mapOptions= {{
					center: new google.maps.LatLng({location_lat}, {location_lng}),
					zoom:6,
				}};
				var map = new google.maps.Map(document.getElementById('map'), mapOptions);

				// Add markers
				var location_marker = new google.maps.Marker({{
					position: mapOptions.center
				}});
				location_marker.setMap(map);

				// Set zoom
				var bounds = new google.maps.LatLngBounds()
				bounds.extend(location_marker.position)
				bounds.extend(new google.maps.LatLng(70.4703, 19.0707))
				bounds.extend(new google.maps.LatLng(59.4066, 33.3968))
				map.fitBounds(bounds);
			}}
			</script>
			<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyD7A_wqRiWrVXFAxqyzUY09oDNTxMJl9ZA&callback=createMap"></script>
		""".format(location_lat=location_lat, location_lng=location_lng)

	def _get_map(self, location_lat, location_lng, reference_lat, reference_lng):
		return """
			<div style="float:right; width:300px; height:400px; margin:15px;" id="map"></div>
			<script>
			function createMap() {{
				// Create map
				var mapOptions= {{
					center: new google.maps.LatLng({location_lat}, {location_lng}),
					zoom:9,
				}};
				var map = new google.maps.Map(document.getElementById('map'), mapOptions);

				// Add markers
				var location_marker = new google.maps.Marker({{
					position: mapOptions.center
				}});
				location_marker.setMap(map);

				// Set zoom
				var bounds = new google.maps.LatLngBounds()
				bounds.extend(location_marker.position)
				bounds.extend(new google.maps.LatLng({reference_lat}, {reference_lng}))
				map.fitBounds(bounds);
			}}
			</script>
			<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyD7A_wqRiWrVXFAxqyzUY09oDNTxMJl9ZA&callback=createMap"></script>
		""".format(location_lat=location_lat, location_lng=location_lng, reference_lat=reference_lat, reference_lng=reference_lng)


