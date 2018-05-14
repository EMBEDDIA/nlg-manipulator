import pandas as pd
import os
from math import radians, cos, sin, asin, sqrt
import urllib.request
import urllib.parse
import urllib.error
import json
import time


class LandmarkGenerator():

    def __init__(self):
        self.population_data = pd.read_csv(os.path.join(os.path.dirname(__file__), '../../data/' + "population.csv"))
        self.municipalities = self.population_data['where'].unique()
        latest = self.population_data['when'].unique()[-1]
        self.REFERENCES = self.population_data.loc[self.population_data['when'] == latest, ['where', 'population']]
        self.REFERENCES.columns = ['name', 'population']
        for m in self.municipalities:
            if m not in list(self.REFERENCES['name']):
                print('Municipality {}, not in the latest population statistics, ignoring'.format(m))
        self.CACHE = {}

    def generate(self, min_dist, max_dist=None, n_landmarks=None):
        ref_sorted = self.REFERENCES.sort_values(by='population', ascending=False)
        # Drop Maarianhamina, since it shouldn't be chosen as a landmark in any case.
        ref_sorted = ref_sorted.loc[ref_sorted['name'] != "Maarianhamina - Mariehamn"]
        ref_sorted = ref_sorted.iloc[1:].reset_index(drop=True)
        idx = 0
        while idx < len(ref_sorted):
            print("Removing neighbors of {}".format(ref_sorted.loc[idx, 'name']))
            try:
                curr_lat, curr_lng = self._get_coords(ref_sorted.loc[idx, 'name'])
            except urllib.error.HTTPError:
                print("Error getting coordinates, retrying")
                continue
            remove = []
            max_found = 0
            for i in range(idx + 1, len(ref_sorted)):
                if i%10 == 0:
                    print(i)
                comp_lat = None
                n_retries = 0
                while comp_lat is None and n_retries <= 10:
                    if n_retries > 0:
                        print("Error getting coordinates, retrying: {}/10".format(n_retries))
                    try:
                        comp_lat, comp_lng = self._get_coords(ref_sorted.loc[i, 'name'])
                    except urllib.error.HTTPError:
                        n_retries += 1
                        continue
                if comp_lat is None:
                    raise TimeoutError("Unable to fetch municipality coordinates. Check internet connection.")
                dist = self._distance(curr_lat, curr_lng, comp_lat, comp_lng)
                if dist < min_dist:
                    remove.append(i)
                if dist > max_found:
                    max_found = dist
            ref_sorted = ref_sorted.drop(remove)
            ref_sorted = ref_sorted.reset_index(drop=True)
            if (n_landmarks and idx + 1 == n_landmarks) or (max_dist and max_found < max_dist):
                return ref_sorted.nlargest(idx + 1, 'population')
            idx += 1
        print('Landmarks created')
        return ref_sorted

    def _distance(self, lat1, lng1, lat2, lng2):
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        return 12742 * asin(sqrt(sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lng2 - lng1) / 2) ** 2))

    def _get_coords(self, location):
        if location not in self.CACHE:
            url = "https://api.digitransit.fi/geocoding/v1/search?text={}&layers=localAdmin&size=1".format(
                urllib.parse.quote(location))
            response = urllib.request.urlopen(url).read()
            time.sleep(.05)
            data = json.loads(response.decode('utf-8'))
            self.CACHE[location] = data['features'][0]['geometry']['coordinates'][1], \
                                   data['features'][0]['geometry']['coordinates'][0]
        return self.CACHE[location]


if __name__ == '__main__':

    test_gen = LandmarkGenerator()
    REFERENCES = test_gen.generate(100)

    REFERENCES_2 = test_gen.generate(100, max_dist=200)

    REFERENCES_3 = test_gen.generate(100, max_dist=400)

    REFERENCES_4 = test_gen.generate(100, n_landmarks=17)

    print("Test complete")

