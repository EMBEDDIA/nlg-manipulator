import gzip
import logging
import os
import pickle
import urllib
from random import randint
import pandas as pd

log = logging.getLogger('root')

from core import Registry, NLGPipeline, DataFrameStore
from crime_message_generator import CrimeMessageGenerator, NoMessagesForSelectionException
from core import BodyDocumentPlanner, HeadlineDocumentPlanner
from templates.read_multiling import read_templates_file
from core import NumeralFormatter
from core import TemplateSelector
from core import Aggregator
from crime_named_entity_resolver import CrimeEntityNameResolver
from core import BodyHTMLSurfaceRealizer, HeadlineHTMLSurfaceRealizer
from crime_importance_allocator import CrimeImportanceSelector
from language_constants import pronouns, vocabulary, errors


class CrimeNlgService(object):

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

        # Load crime stats
        crime_cache_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/crime_data.cache'))
        compute = None
        if force_cache_refresh or not os.path.exists(crime_cache_path):
            csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/pyn_crime_y12_comparison_ranks_outliers.csv'))
            if not os.path.exists(csv_path):
                log.info('No pre-computed CSV at "{}", generating'.format(csv_path))
                from fetch_crime_data import run as fetch_data
                fetch_data()
            compute = lambda: pd.DataFrame.from_csv(csv_path)
        
        self.registry.register('crime-data', DataFrameStore(
            crime_cache_path,
            compute=compute
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

        # PRNG seed
        self._set_seed(seed_val=random_seed)

        def _get_components(headline=False):
            # Put together the list of components
            # This varies depending on whether it's for headlines and whether we're using Omorphi
            yield CrimeMessageGenerator(expand=not headline)  # Don't expand facts for headlines!
            yield CrimeImportanceSelector()
            yield HeadlineDocumentPlanner() if headline else BodyDocumentPlanner()
            yield TemplateSelector()
            yield Aggregator()
            yield NumeralFormatter()
            yield CrimeEntityNameResolver()
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
        return read_templates_file(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "main.txt")))

    def run_pipeline(self, language, where, where_type):
        log.info("Running Body NLG pipeline: language={}, where={}, where_type={}".format(language, where, where_type))
        try:
            body = self.body_pipeline.run(
                (where, where_type),
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
            headline_lang = "{}-head".format(language)
            headline = self.headline_pipeline.run(
                (where, where_type),
                headline_lang,
                prng_seed=self.registry.get('seed'),
            )[0]
            log.info("Headline pipeline complete")
        except Exception as ex:            
            headline = where
            log.error("%s", ex)

        return headline, body

    def _set_seed(self, seed_val=None):
        log.info("Selecting seed for NLG pipeline")
        if not seed_val:
            seed_val = randint(1, 10000000)
            log.info("No preset seed, using random seed {}".format(seed_val))
        else:
            log.info("Using preset seed {}".format(seed_val))
        self.registry.register('seed', seed_val)

    def get_languages(self):
        return list(self.registry.get('templates').keys())

if __name__ == "__main__":
    # Logging
    import logging
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log = logging.getLogger('root')
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)

    # Run
    CrimeNlgService().run_pipeline('fi', 'Akaa', 'M')