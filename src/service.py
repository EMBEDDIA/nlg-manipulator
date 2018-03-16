import gzip
import logging
import os
import pickle
import urllib
from random import randint
from zipfile import ZipFile

from locations import LocationHierarchy

log = logging.getLogger('root')

from core import Registry, NLGPipeline, HdfStore
from moj_election_data_importer import Importer as MOJImporter
from municipal_election_message_generator import MunicipalElectionMessageGenerator, NoMessagesForSelectionException
from core import BodyDocumentPlanner, HeadlineDocumentPlanner
from templates.read_multiling import read_templates_file
from core import NumeralFormatter
from core import TemplateSelector
from core import Aggregator
from municipal_election_named_entity_resolver import MunicipalElectionEntityNameResolver
from core import BodyHTMLSurfaceRealizer, HeadlineHTMLSurfaceRealizer
from municipal_election_party_names import party_names
from municipal_election_importance_allocator import MunicipalElectionImportanceSelector
from language_constants import pronouns, vocabulary, errors


class ElectionNlgService(object):

    def __init__(self, random_seed=None, force_cache_refresh=False, nomorphi=False):
        """
        :param random_seed: seed for random number generation, for repeatability
        :param force_cache_refresh:
        :param nomorphi: don't load Omorphi for morphological generation. This removes the dependency on Omorphi,
            so allows easier setup, but means that no morphological inflection will be performed on the output,
            which is generally a very bad thing for the full pipeline
        """

        # New registry and result importer
        self.registry = Registry()
        self.moj_importer = MOJImporter(spec=2017)

        # Results data

        moj_data_cache = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/moj-data.cache'))
        computes = [None, None, None]
        if force_cache_refresh or not os.path.exists(moj_data_cache):
            computes = [
                self._load_results_metadata,
                self._load_results_parties,
                self._load_results_candidates
            ]
        
        self.registry.register('moj-metadata', HdfStore(
            moj_data_cache,
            'metadata', 
            compute=computes[0]
        ))
        self.registry.register('moj-results-party', HdfStore(
            moj_data_cache,
            'party_data', 
            compute=computes[1]
        ))
        self.registry.register('moj-results-candidate', HdfStore(
            moj_data_cache,
            'candidate_data', 
            compute=computes[2]
        ))

        # Templates
        self.registry.register('templates', 
            self._get_cached_or_compute(
                '../data/templates.cache', 
                self._load_templates,
                force_cache_refresh=force_cache_refresh
            )
        )

        # Language metadata
        self.registry.register('pronouns', pronouns)
        self.registry.register('vocabulary', vocabulary)
        
        # Location names (hierarchy, localized names)
        geodata, geodata_lookup, geodata_index = self._get_cached_or_compute(
                '../data/geodata.cache', 
                self._generate_geographic_information,
                force_cache_refresh=force_cache_refresh)
        self.registry.register('geodata', geodata)
        self.registry.register('geodata-lookup', geodata_lookup)
        self.registry.register('geodata-hierarchy', geodata_index)

        # Parties (localized names)
        self.registry.register('parties', party_names)

        # Candidates (localized names, location mapping)
        candidates, candidates_by_location = self._get_cached_or_compute(
            '../data/candidate-data.cache',
            self._generate_candidate_information,
            force_cache_refresh=force_cache_refresh)
        self.registry.register('candidates', candidates)
        self.registry.register('candidates-by-location', candidates_by_location)

        # PRNG seed
        self._set_seed(seed_val=random_seed)

        def _get_components(headline=False):
            # Put together the list of components
            # This varies depending on whether it's for headlines and whether we're using Omorphi
            yield MunicipalElectionMessageGenerator(expand=not headline)  # Don't expand facts for headlines!
            yield MunicipalElectionImportanceSelector()
            yield HeadlineDocumentPlanner() if headline else BodyDocumentPlanner()
            yield TemplateSelector()
            yield Aggregator()
            yield NumeralFormatter()
            yield MunicipalElectionEntityNameResolver()
            if not nomorphi:
                # Don't even try importing Omorphi if we're not using it
                from omorfi_generator import OmorfiGenerator
                yield OmorfiGenerator()
            yield HeadlineHTMLSurfaceRealizer() if headline else BodyHTMLSurfaceRealizer()

        log.info("Configuring Body NLG Pipeline")
        self.body_pipeline = NLGPipeline(self.registry, *_get_components())
        self.headline_pipeline = NLGPipeline(self.registry, *_get_components(headline=True))

    def _get_cached_or_compute(self, cache, compute, force_cache_refresh=False, relative_path=True):
        if relative_path:
            cache = os.path.abspath(os.path.join(os.path.dirname(__file__), cache))
        if force_cache_refresh:
            log.info("force_cache_refresh is True, deleting previous cache from {}".format(cache))
            if os.path.exists(cache):
                os.remove(cache)
        if not os.path.exists(cache):
            log.info("No cache at {}, computing".format(cache))
            result = compute()
            with gzip.open(cache, 'wb') as f:
                pickle.dump(result, f)
            return result
        else:
            log.info("Found cache at {}, decompressing and loading".format(cache))
            with gzip.open(cache, 'rb') as f:
                return pickle.load(f)             

    def _load_templates(self):
        log.info('Loading templates')
        return read_templates_file(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "multilingual", "valtteri_main.txt")))

    def _load_results_metadata(self):
        log.info("Computing and caching MOJ metadata")
        filename = self._download_and_unzip(
            "http://tulospalvelu.vaalit.fi/KV-2017/kv-2017_alu_maa.csv.zip", 
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "csv")), 
            "meta.csv"
        )
        return self.moj_importer.load_meta(filename)

    def _load_results_parties(self):
        log.info("Computing and caching MOJ party results")
        filename = self._download_and_unzip(
            "http://tulospalvelu.vaalit.fi/KV-2017/kv-2017_puo_maa.csv.zip", 
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "csv")), 
            "party.csv"
        )
        return self.moj_importer.load_party_results(filename)

    def _load_results_candidates(self):
        log.info("Computing and caching MOJ candidate data")
        filename = self._download_and_unzip(
            "http://tulospalvelu.vaalit.fi/KV-2017/kv-2017_ehd_maa.csv.zip",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "csv")),
            "candidate.csv"
        )
        return self.moj_importer.load_candidate_results(filename)

    def _download_and_unzip(self, url, dir_path, file_name):
        csv_path = os.path.abspath(os.path.join(dir_path, file_name))

        if os.path.exists(csv_path):
            log.info("Found CSV at {}".format(csv_path))
            return csv_path
        
        log.info("Missing CSV at {}, downloading ZIP from {} to a temporary location".format(csv_path, url))
        temp_file, _ = urllib.request.urlretrieve(url)
        with ZipFile(temp_file, "r") as z:
            log.info("Extracting zipped file")
            z.extractall(dir_path)
            extracted_name = z.namelist()[0]
        
        log.info("Removing temporary file")
        os.remove(temp_file)
        
        log.info("Renaming file to correct name")
        os.rename(os.path.join(dir_path, extracted_name), csv_path)
        return csv_path

    def _generate_geographic_information(self):
        geodata = {}
        geodata_lookup = {}
        geodata_index = {}
        for language, area_name, country_name in [
                ("fi", "area_name_fi", "Suomi"),
                ("sv", "area_name_sv", "Finland"),
                ("en","area_name_fi", "Finland")]:
            if language not in self.registry.get('templates').keys():
                continue
            log.info("Generating geographic information for language {}".format(language))
            this_geodata, this_geodata_lookup = self._generate_geographic_information_for_language(area_name, country_name)
            geodata[language] = this_geodata
            geodata_lookup[language] = this_geodata_lookup

            # Now we've got the geodata, pre-compute an index so we can easily look things up in the hierarchy
            geodata_index[language] = LocationHierarchy(this_geodata["fi"])

        return geodata, geodata_lookup, geodata_index

    def _generate_geographic_information_for_language(self, name_field, country_name):
        metadata_store = self.registry.get('moj-metadata')
        geodata = {}
        geodata_lookup = {
            'C': {},
            'D': {},
            'M': {},
            'P': {},
        }

        geodata["fi"] = {
            "name": country_name,
            "id": "fi",
            "type": "C",
            "children": {},
        }
        geodata_lookup["C"]["fi"] = country_name
        
        filtered_data = metadata_store.query('where_type == "D"')
        for _, row in filtered_data.iterrows():
            electoral_district_id = str(int(row["electoral_district_id"]))
            electoral_district_name = row[name_field]

            geodata["fi"]["children"][electoral_district_id] = {
                "name": electoral_district_name,
                "id": electoral_district_id,
                "type": "D",
                "children": {},
            }
            geodata_lookup["D"][electoral_district_id] = electoral_district_name

        filtered_data = metadata_store.query('where_type == "M"')
        for _, row in filtered_data.iterrows():
            electoral_district_id = str(int(row["electoral_district_id"]))
            electoral_district_name = geodata["fi"]["children"][electoral_district_id]["name"]

            municipality_id = str(int(row["municipality_id"]))
            municipality_name = row[name_field]

            geodata["fi"]["children"][electoral_district_id]["children"][municipality_id] = {
                "name": municipality_name,
                "id": municipality_id,
                "type": "M",
                "children": {},
            }
            geodata_lookup["M"][municipality_id] = municipality_name
        
        filtered_data = metadata_store.query('where_type == "P"')
        for _, row in filtered_data.iterrows():
            electoral_district_id = str(int(row["electoral_district_id"]))
            electoral_district_name = geodata["fi"]["children"][electoral_district_id]["name"]

            municipality_id = str(int(row["municipality_id"]))
            municipality_name = geodata["fi"]["children"][electoral_district_id]["children"][municipality_id]["name"]

            polling_station_id = row["where"]
            polling_station_name = row[name_field]

            geodata["fi"]["children"][electoral_district_id]["children"][municipality_id]["children"][polling_station_id] = {
                "name": polling_station_name,
                "id": polling_station_id,
                "type": "P",
                "children": {},
            }
            geodata_lookup["P"][polling_station_id] = polling_station_name

        return geodata, geodata_lookup

    def _generate_candidate_information(self):
        candidates_by_location = {}
        candidates = {}

        party_data = self.registry.get('parties')

        candidate_data_store = self.registry.get('moj-results-candidate')
        data = candidate_data_store.query('where_type == "M" & columns=["where", "where_type", "who", "name", "gender", "party"]')
        data = data.drop_duplicates(keep='first')

        for language in pronouns.keys():

            candidates_by_location[language] = {}
            candidates[language] = {}

            log.info("Generating candidate information for language {}".format(language))
            for _, row in data.iterrows():
                # Try getting party membership abbreviation in this order:
                # 1. The relevant party's abbreviation in the relevant language
                # 2. A geneneral abbreviation in the relevant language
                # 3. The relevant party's abbreviation in Finnish
                # 4. A general abbreviation in Finnish (guaranteed to be present)
                party_membership = party_data.get(language, {}).get(row['party'], {}).get("membership_abbreviation", None)
                if not party_membership:
                    party_membership = party_data.get(language, {}).get(None, {}).get("membership_abbreviation", None)
                if not party_membership:
                    party_membership = party_data["fi"].get(row['party'], {}).get("membership_abbreviation", None)
                if not party_membership:
                    party_membership = party_data["fi"].get(None, {}).get("membership_abbreviation", ["unknown-party"])
                party_membership = party_membership[0]

                this_candidate = {
                    "full": "{} ({})".format(row['name'], party_membership),
                    "short": row['name'],
                    "pronoun": self.registry.get('pronouns')[language][row['gender']]
                }

                location = "{}{}".format(row['where_type'], row['where'])
                if location not in candidates_by_location[language]:
                    candidates_by_location[language][location] = {}
                candidates_by_location[language][location][row['who']] = this_candidate
                candidates[language][row['who']] = this_candidate

        return candidates, candidates_by_location

    def run_pipeline(self, language, who, who_type, where, where_type):
        log.info("Running Body NLG pipeline: language={}, who={}, who_type={}, where={}, where_type={}".format(language, who, who_type, where, where_type))
        try:
            body = self.body_pipeline.run(
                (who, who_type, where, where_type),
                language,
                prng_seed=self.registry.get('seed'),
            )[0]
            log.info("Body pipeline complete")
        except NoMessagesForSelectionException:
            log.error("User selection returned no messages")
            body = errors.get(language, {}).get("no-messages-for-selection", "Something went wrong. Please try again later")
        except Exception as ex:
            log.error("%s", ex)
            body = errors.get(language, {}).get("general-error", "Something went wrong. Please try again later")

        log.info("Running headline NLG pipeline")
        try:
            if language != "sv":
                headline_lang = "{}-head".format(language)
            else:
                headline_lang = language
            headline = self.headline_pipeline.run(
                (who, who_type, where, where_type),
                headline_lang,
                prng_seed=self.registry.get('seed'),
            )[0]
            log.info("Body pipeline complete")
        except Exception as ex:            
            headline = self.geodata_lookup(language, where_type, where)
            log.error("%s", ex)
            if who_type:
                headline += ": " + self.entity_lookup(language, who, who_type)

        return headline, body

    def _set_seed(self, seed_val=None):
        log.info("Selecting seed for NLG pipeline")
        if not seed_val:
            seed_val = randint(1, 10000000)
            log.info("No preset seed, using random seed {}".format(seed_val))
        else:
            log.info("Using preset seed {}".format(seed_val))
        self.registry.register('seed', seed_val)

    def get_geodata(self, language):
        geodata = self.registry.get('geodata')
        return geodata.get(language, geodata["fi"])

    def geodata_lookup(self, language, where_type, where):
        geodata = self.registry.get('geodata-lookup')
        geodata = geodata.get(language, geodata["fi"])
        if where_type:
            return geodata[where_type].get(where, None)
        for where_type in geodata:
            if where in geodata[where_type]:
                return geodata[where_type][where]
        return None

    def get_city_code(self, city):
        geodata = self.registry.get('geodata-lookup')["fi"]['M'].items()
        for code, name in geodata:
            if name == city:
                return code
        return None

    def get_entities(self, language, location):
        parties = self.registry.get('parties')
        parties = parties.get(language, parties["fi"])
        if location is None:
            return {
                "candidates": {},
                "parties": parties,
            }

        candidates = self.registry.get('candidates-by-location')
        candidates = candidates.get(language, candidates["fi"])

        if location[0] == "P":
            location = location[1: location.index(":")]

        return {
            "candidates": candidates.get(location, {}),
            "parties": parties,
        }

    def entity_lookup(self, language, who, who_type):
        if who_type == 'candidate':
            data = self.registry.get('candidates')
        elif who_type == 'party':
            data = self.registry.get('parties')
        data = data.get(language, data["fi"])
        data = data.get(who, {}).get('full', None)
        if isinstance(data, str):
            return data
        return data[0]

    def get_languages(self):
        return list(self.registry.get('templates').keys())
