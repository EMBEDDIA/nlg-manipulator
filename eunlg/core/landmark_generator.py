import pandas as pd
import os, sys
from math import radians, cos, sin, asin, sqrt
import urllib.request
import urllib.parse
import urllib.error
import json
import time


class LandmarkGenerator:

    def __init__(self, prefetch=True):
        self.population_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '../../data/' + "population.csv"))
        self.municipalities = self.population_data['where'].unique()
        latest = self.population_data['when'].unique()[-1]
        self._REFERENCES = self.population_data.loc[self.population_data['when'] == latest, ['where', 'population']]
        self._REFERENCES.columns = ['name', 'population']
        self._REFERENCES = self._REFERENCES.loc[self._REFERENCES['name'] != "WHOLE COUNTRY"]
        self._CACHE = {}
        if prefetch:
            print("Prefetching coordinates")
        for m in self.municipalities:
            if m not in list(self._REFERENCES['name']):
                print('\nMunicipality {} not in the latest population statistics, ignoring'.format(m))
            elif prefetch:
                sys.stdout.write("\rPrefetching: {:30s}".format(m))
                sys.stdout.flush()
                self._get_coords(m)

    def generate(self, min_dist, max_dist=None, n_landmarks=None):
        print("\nGenerating landmarks")
        ref_sorted = self._REFERENCES.sort_values(by='population', ascending=False)
        # Drop Maarianhamina, since it shouldn't be chosen as a landmark in any case.
        ref_sorted = ref_sorted.loc[ref_sorted['name'] != "Maarianhamina - Mariehamn"]
        ref_sorted = ref_sorted.reset_index(drop=True)
        idx = 0
        while idx < len(ref_sorted):
            curr_name = ref_sorted.loc[idx, 'name']
            curr_lat, curr_lng = self._get_coords(curr_name)
            remove = []
            max_found = 0
            for i in range(idx + 1, len(ref_sorted)):
                if i%10 == 0:
                    sys.stdout.write("\rChecking for neighbors of {}: {}/{}".format(curr_name, i, len(ref_sorted)))
                    sys.stdout.flush()
                comp_lat, comp_lng = self._get_coords(ref_sorted.loc[i, 'name'])
                dist = self._distance(curr_lat, curr_lng, comp_lat, comp_lng)
                if dist < min_dist:
                    remove.append(i)
                if dist > max_found:
                    max_found = dist
            sys.stdout.write("\rChecking for neighbors of {}: {}/{}".format(curr_name, i + 1, len(ref_sorted)))
            sys.stdout.flush()
            ref_sorted = ref_sorted.drop(remove)
            ref_sorted = ref_sorted.reset_index(drop=True)
            if (n_landmarks and idx + 1 == n_landmarks) or (max_dist and max_found < max_dist):
                ref_sorted = ref_sorted.nlargest(idx + 1, 'population')
                break
            idx += 1
        print('\nLandmarks created')
        references = []
        for row in ref_sorted.iterrows():
            name = row[1]['name']
            lat, lng = self._get_coords(name)
            references.append({'latitude': lat, 'longitude': lng, 'name': name})
        return references

    def _distance(self, lat1, lng1, lat2, lng2):
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        return 12742 * asin(sqrt(sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lng2 - lng1) / 2) ** 2))

    def _get_coords(self, location):
        n_retries = 0
        while location not in self._CACHE and n_retries <= 10:
            try:
                if n_retries > 0:
                    print("Error getting coordinates, retrying: {}/10".format(n_retries))
                url = "https://api.digitransit.fi/geocoding/v1/search?text={}&layers=localAdmin&size=1".format(
                    urllib.parse.quote(location))
                time.sleep(.05)
                response = urllib.request.urlopen(url).read()
                data = json.loads(response.decode('utf-8'))
                self._CACHE[location] = data['features'][0]['geometry']['coordinates'][1], \
                                        data['features'][0]['geometry']['coordinates'][0]
            except urllib.error.HTTPError:
                n_retries += 1
                continue
        if location not in self._CACHE:
            raise TimeoutError("Unable to fetch municipality coordinates. Check internet connection.")
        return self._CACHE[location]


if __name__ == '__main__':

    test_gen = LandmarkGenerator()
    REFERENCES = test_gen.generate(100)

    REFERENCES_2 = test_gen.generate(100, max_dist=200)

    REFERENCES_3 = test_gen.generate(100, max_dist=400)

    REFERENCES_4 = test_gen.generate(100, n_landmarks=17)

    print("Test complete")

