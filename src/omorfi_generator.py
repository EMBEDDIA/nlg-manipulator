from omorfi.omorfi import Omorfi

from finnish_municipality_morphology import INESSIVE_ADESSIVE_MAP

from finnish_morphology_special_cases import special_cases as cache_fi
from swedish_morphology_special_cases import special_cases as cache_sv
from english_morphology_special_cases import special_cases as cache_en

import re

import logging
log = logging.getLogger('root')

CASE_REGEX = re.compile("\[CASE=([^\]]*)\]")

CASE_MAP = {
    "nominative": "[CASE=NOM]",
    "essive": "[CASE=ESS]",
    "genitive": "[CASE=GEN]",
    "illative": "[CASE=ILL",
    "inessive": "[CASE=INE]",
    "elative": "[CASE=ELA]",
    "allative": "[CASE=ALL]",
    "adessive": "[CASE=ADE]",
    "ablative": "[CASE=ABL]",
    "partitive": "[CASE=PAR]",
    "accusative": "[CASE=ACC]",
    "translative": "[CASE=TRA]",
}

FINNISH_FALLBACKS = {
    "ä": {
        "essive": "na",
        "genitive": "n",
        "inessive": "ssä",
        "elative": "stä",
        "allative": "lle",
        "adessive": "llä",
        "ablative": "ltä",
        "partitive": "a"
    },
    "a": {
        "essive": "nä",
        "genitive": "n",
        "inessive": "ssa",
        "elative": "sta",
        "allative": "lle",
        "adessive": "lla",
        "ablative": "lta",
        "partitive": "a"
    }
}

VOWELS = ["a", "e", "i", "o", "u", "å", "y", "ä", "ö", ]

class OmorfiGenerator(object):

    def __init__(self):
        
        self._omorfi = Omorfi()
        self._omorfi.load_from_dir()
        if not "omorfi-omor" in self._omorfi.generators:
            raise Exception("Omorfi did not find omorfi-omor.generator using default heuristic, unable to proceed")
        self._generator = self._omorfi.generators["omorfi-omor"]
        self._analyse = self._omorfi.analyse

    def run(self, registry, random, language, document_plan):
        if language.startswith("fi"):
            log.debug("Language is Finnish, using Omorfi for morphology")
            self._recurse_fi(document_plan)
        elif language.startswith("sv"):
            log.debug("Language is Swedish, using custom rules")
            self._recurse_sv(document_plan)
        elif language.startswith("en"):
            log.debug("Language is English, using custom rules")
            self._recurse_en(document_plan)
        return (document_plan, )

    def _recurse_en(self, this):
        try:
            # Try to use the current root as a non-leaf.
            children = this.children
            log.debug("Visiting non-leaf '{}'".format(this))
            for child in children:
                self._recurse_en(child)
        except AttributeError as ex:
            # Had no children, must be a leaf node
            log.debug("Visiting leaf {}".format(this))
           
            try:
                attributes = this.attributes
            except AttributeError:
                log.debug("Does not have attributes, ignoring")
                return

            if not "case" in attributes:
                log.debug("Does not have a case attribute, ignoring")
                return

            case = this.attributes["case"]
            cached = cache_en.get(this.value, {}).get(case, None)
            if cached:
                this.value = lambda x: cached
            else:
                modified_part = this.value

                if case == "possessive" or case == "genitive":
                    maybe_s = "s" if modified_part[-1] != "s" else ""
                    modified_part = "{}'{}".format(modified_part, maybe_s)

                result = modified_part

                this.value = lambda x: result

    def _recurse_sv(self, this):
        try:
            # Try to use the current root as a non-leaf.
            children = this.children
            log.debug("Visiting non-leaf '{}'".format(this))
            for child in children:
                self._recurse_sv(child)
        except AttributeError as ex:
            # Had no children, must be a leaf node
            log.debug("Visiting leaf {}".format(this))
           
            try:
                attributes = this.attributes
            except AttributeError:
                log.debug("Does not have attributes, ignoring")
                return

            if not "case" in attributes:
                log.debug("Does not have a case attribute, ignoring")
                return

            case = this.attributes["case"]
            cached = cache_sv.get(this.value, {}).get(case, None)
            if cached:
                this.value = lambda x: cached
            else:
                modified_part = this.value

                if case == "possessive" or case == "genitive":
                    maybe_s = "" if modified_part[-1] in ["s", "x", "z"] else "s"
                    modified_part = "{}'{}".format(modified_part, maybe_s)

                result = modified_part

                this.value = lambda x: result

    def _recurse_fi(self, this):
        try:
            # Try to use the current root as a non-leaf.
            children = this.children
            log.debug("Visiting non-leaf '{}'".format(this))
            for child in children:
                self._recurse_fi(child)
        except AttributeError as ex:
            # Had no children, must be a leaf node
            log.debug("Visiting leaf {}".format(this))
           
            try:
                attributes = this.attributes
            except AttributeError:
                log.debug("Does not have attributes, ignoring")
                return

            if not "case" in attributes:
                log.debug("Does not have a case attribute, ignoring")
                return

            log.debug("Found a slot with a 'case' attribute: {}".format(this))

            if attributes.get("entity_type", None) == "D":
                self._modify(this, multi_word_idx=1)

            elif attributes.get("entity_type", None) == "P":
                modified = "äänestysalue {}".format(this.value)
                this.value = lambda x: modified
                self._modify(this, multi_word_idx=0)

            else:
                # The slot is probably a common noun
                self._modify(this, prefer_proper_nouns=False)
            return

    def _modify(self, slot, multi_word_idx=None, prefer_proper_nouns=True):
        original_case = slot.attributes["case"]

        cached_value = cache_fi.get(slot.value, {}).get(original_case, None)
        if cached_value:
            slot.value = lambda x: cached_value
            return

        if multi_word_idx is not None:
            parts = slot.value.split(" ")
            analysis_part = parts[multi_word_idx]
        else:
            analysis_part = slot.value

        if original_case == "inessive" or original_case == "adessive":
            case = INESSIVE_ADESSIVE_MAP.get(analysis_part, original_case)
        else:
            case = original_case

        analysis = self.analyse(analysis_part, prefer_proper_nouns)

        if analysis == "UNKNOWN" or "GUESS=UNKNOWN" in analysis:
            log.error("No Omorfi analysis for case {} (originally {}) of word {} (part of {})".format(case, original_case, analysis_part, slot.value))
            result = None 

        else:
            log.info("Omorfi analysis: {} -> {}".format(analysis_part, analysis))

            analysis_parts = analysis.split("[BOUNDARY=COMPOUND]")
            last_part = analysis_parts[-1].replace("[CASE=NOM]", CASE_MAP[case])
            modified_analysis = analysis_parts
            modified_analysis[-1] = last_part
            modified_analysis = "[BOUNDARY=COMPOUND]".join(modified_analysis)

            log.info("Omorfi modification: {} + {} -> {}".format(analysis, case, modified_analysis))

            result = self.generate(modified_analysis)[0]
            log.info("Omorfi {} -> {}".format(modified_analysis, result))  
        
            if result == "U":
                log.error("No Omorfi generation for {}".format(modified_analysis))
                result = None

        if result is None:
            maybe_separator = ":" if analysis_part[-1] not in VOWELS else ""
            if "a" in analysis_part or "o" in analysis_part or "u" in analysis_part:
                suffix = FINNISH_FALLBACKS["a"].get(case, "")
            else:
                suffix = FINNISH_FALLBACKS["ä"].get(case, "")
            if suffix != "": 
                result = analysis_part + maybe_separator + suffix
            else:
                result = analysis_part

        if analysis_part[0].isupper():
            result = result[0].upper() + result[1:]

        if multi_word_idx is not None:
            parts[multi_word_idx] = result
            result = " ".join(parts)


        if slot.value not in cache_fi:
            cache_fi[slot.value] = {}
        cache_fi[slot.value][original_case] = result

        slot.value = lambda x: result
        return 
        

    def generate(self, token):
        return [res[0] for res in self._generator.lookup(token) or ["UNKNOWN"]]

    def analyse(self, token, prefer_proper_nouns=True):
        analyses = []
        for analysis in self._omorfi.analyse(token):
            analyses.append(analysis[0])
        nominative_analyses = [a for a in analyses if "[CASE=NOM]" in a]
        if nominative_analyses:
            analyses = nominative_analyses
        non_possessive_analyses = [a for a in analyses if "[POSS=" not in a]
        if non_possessive_analyses:
            analyses = non_possessive_analyses
        if prefer_proper_nouns:
            return next((analysis for analysis in analyses if "[UPOS=PROPN]" in analysis), analyses[0])
        else:
            return analyses[0]

if __name__ == "__main__":
    g = OmorfiGenerator()
    print(g.analyse("Pyhärannan"))
    print(g.generate("[WORD_ID=äänestys][UPOS=NOUN][NUM=SG][CASE=NOM][BOUNDARY=COMPOUND][WORD_ID=alue][UPOS=NOUN][NUM=SG][CASE=ADE]"))
