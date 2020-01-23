import gzip
import logging
import os
import pickle
from collections import OrderedDict
from random import randint

import pandas as pd

from core.aggregator import Aggregator
from core.datastore import DataFrameStore
from core.document_planner import BodyDocumentPlanner, HeadlineDocumentPlanner
from core.morphology_resolver import MorphologyResolver
from core.pipeline import NLGPipeline
from core.realize_slots import SlotRealizer
from core.registry import Registry
from core.surface_realizer import BodyHTMLSurfaceRealizer, HeadlineHTMLSurfaceRealizer
from core.template_reader import read_templates_file
from core.template_selector import TemplateSelector
from eu_importance_allocator import EUImportanceSelector
from eu_message_generator import EUMessageGenerator, NoMessagesForSelectionException
from eu_named_entity_resolver import EUEntityNameResolver
from language.language_constants import errors, vocabulary
from locations import LocationHierarchy

log = logging.getLogger("root")


class EUNlgService:
    def __init__(self, random_seed=None, force_cache_refresh=False, nomorphi=True):
        """
        :param random_seed: seed for random number generation, for repeatability
        :param force_cache_refresh:
        :param nomorphi: don't load Omorphi for morphological generation. This removes the dependency on Omorphi,
            so allows easier setup, but means that no morphological inflection will be performed on the output,
            which is generally a very bad thing for the full pipeline
        """

        # New registry and result importer
        self.registry = Registry()

        dataname = "eu_data"

        data = [
            ("../data/" + dataname + ".csv", "../data/" + dataname + ".cache", "eu-data"),
        ]

        for csv_path, cache_path, registry_name in data:
            csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), csv_path))
            cache_path = os.path.abspath(os.path.join(os.path.dirname(__file__), cache_path))
            compute = None
            if force_cache_refresh or not os.path.exists(cache_path):
                if not os.path.exists(csv_path):
                    log.info('No pre-computed CSV at "{}", generating'.format(csv_path))
                    from fetch_eu_data import run as fetch_data

                    fetch_data()

                def compute():
                    return pd.read_csv(csv_path, index_col=False)

            self.registry.register(registry_name, DataFrameStore(cache_path, compute=compute))

        # Templates
        self.registry.register(
            "templates",
            self._get_cached_or_compute(
                "../data/templates.cache", self._load_templates, force_cache_refresh=force_cache_refresh,
            ),
        )

        # Language metadata
        self.registry.register("vocabulary", vocabulary)

        # Geodata
        # Location names (hierarchy, localized names)
        geodata, geodata_lookup, geodata_index = self._get_cached_or_compute(
            "../data/geodata.cache", self._generate_geographic_information, force_cache_refresh=force_cache_refresh,
        )
        self.registry.register("geodata", geodata)
        self.registry.register("geodata-lookup", geodata_lookup)
        self.registry.register("geodata-hierarchy", geodata_index)

        # PRNG seed
        self._set_seed(seed_val=random_seed)

        def _get_components(headline=False):
            # Put together the list of components
            # This varies depending on whether it's for headlines and whether we're using Omorphi
            yield EUMessageGenerator(expand=not headline)  # Don't expand facts for headlines!
            yield EUImportanceSelector()
            yield HeadlineDocumentPlanner() if headline else BodyDocumentPlanner()
            yield TemplateSelector()
            yield Aggregator()
            yield SlotRealizer()
            yield EUEntityNameResolver()
            yield MorphologyResolver()
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
            with gzip.open(cache, "wb") as f:
                pickle.dump(result, f)
            return result
        else:
            log.info("Found cache at {}, decompressing and loading".format(cache))
            with gzip.open(cache, "rb") as f:
                return pickle.load(f)

    def _load_templates(self):
        log.info("Loading templates")
        return read_templates_file(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "main.txt"))
        )

    def _load_geodata(self):
        return list(self.registry.get("cphi-data").all()["where"].unique())

    def run_pipeline(self, language, where, where_type, data):
        log.info("Running Body NLG pipeline: language={}, where={}, where_type={}".format(language, where, where_type))
        try:
            body = self.body_pipeline.run((where, where_type, data), language, prng_seed=self.registry.get("seed"))[0]
            log.info("Body pipeline complete")
        except NoMessagesForSelectionException:
            log.error("User selection returned no messages")
            body = errors.get(language, {}).get(
                "no-messages-for-selection", "Something went wrong. Please try again later",
            )
        except Exception as ex:
            log.error("%s", ex)
            body = errors.get(language, {}).get("general-error", "Something went wrong. Please try again later")

        log.info("Running headline NLG pipeline")
        try:
            headline_lang = "{}-head".format(language)
            headline = self.headline_pipeline.run(
                (where, where_type, data), headline_lang, prng_seed=self.registry.get("seed"),
            )[0]
            log.info("Headline pipeline complete")
        except Exception as ex:
            headline = where
            log.error("%s", ex)

        # locator_map_data = self.locator_map_data_generator.generate(where) if where_type == 'M' else ''

        return headline, body

    def _set_seed(self, seed_val=None):
        log.info("Selecting seed for NLG pipeline")
        if not seed_val:
            seed_val = randint(1, 10000000)
            log.info("No preset seed, using random seed {}".format(seed_val))
        else:
            log.info("Using preset seed {}".format(seed_val))
        self.registry.register("seed", seed_val)

    def get_languages(self):
        return list(self.registry.get("templates").keys())

    def _generate_geographic_information(self):
        geodata = {}
        geodata_lookup = {}
        geodata_index = {}
        for language, area_name, country_name in [
            ("fi", "area_name_fi", "Suomi"),
            ("sv", "area_name_sv", "Finland"),
            ("en", "area_name_fi", "Finland"),
        ]:
            if language not in self.registry.get("templates").keys():
                continue
            log.info("Generating geographic information for language {}".format(language))
            (this_geodata, this_geodata_lookup) = self._generate_geographic_information_for_language(
                area_name, country_name
            )
            geodata[language] = this_geodata
            geodata_lookup[language] = this_geodata_lookup

            # Now we've got the geodata, pre-compute an index so we can easily look things up in the hierarchy
            geodata_index[language] = LocationHierarchy(this_geodata["fi"])

            return geodata, geodata_lookup, geodata_index

    def _generate_geographic_information_for_language(self, name_field, country_name):
        geodata = {}
        geodata_lookup = {
            "C": {},
            "M": {},
        }

        geodata["fi"] = {
            "name": country_name,
            "id": "fi",
            "type": "C",
            "children": {},
        }
        geodata_lookup["C"]["fi"] = country_name

        municipalities = self.registry.get("cphi-data").query('where_type == "C"')["where"].unique()
        geodata["fi"]["children"] = {m: {"name": m, "id": m, "type": "M", "children": {}} for m in municipalities}
        geodata_lookup["M"] = {m: m for m in municipalities}

        # Sort geodata
        geodata["fi"]["children"] = OrderedDict(sorted(geodata["fi"]["children"].items(), key=lambda i: i[1]["name"]))

        return geodata, geodata_lookup

    def get_geodata(self, language):
        geodata = self.registry.get("geodata")
        return geodata.get(language, geodata["fi"])
