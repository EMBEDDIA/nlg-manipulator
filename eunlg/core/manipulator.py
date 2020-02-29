import logging
import random
from .pipeline import NLGPipelineComponent
from config import MANIPULATORS
from nltk.corpus import wordnet as wn

log = logging.getLogger("root")

words = {
    "RB": ["suprisingly", "luckily", "sadly"],
    "JJ": ["awesome", "round", "soft"],
    "VB": ["run", "increase"],
}

synonyms = {
    "group": ["category", "class"],
}

info_list = []

class Manipulator(NLGPipelineComponent):
    def __init__(self):
        return

    def run(self, registry, random, language, document_plan):
        """
        Run this pipeline component.
        """

        if language.endswith("-head"):
            language = language[:-5]
            log.debug("Language had suffix '-head', removing. Result: {}".format(language))

        if language in MANIPULATORS:
            log.info("Runnin the Manipulator component with language {}".format(language))
            self._recurse(document_plan)
        return (document_plan, info_list)

    def _recurse(self, this):
        try:
            idx = 0
            while idx < len(this.children):
                slots_added = self._recurse(this.children[idx])
                if slots_added:
                    idx += slots_added
                idx += 1
        except AttributeError as ex:
            try:
                slot_type = this.slot_type
                slot_attributes = this.attributes
                log.info("THE SLOT TYPE IS {}".format(slot_type))
            except AttributeError:
                log.info("Got an AttributeError when checking slot_type in realize_slots. Probably not a slot.")
                slot_type = "n/a"
                return 0
            if slot_type == "empty":
                pos = slot_attributes['pos']
                #new_value = random.choice(words[pos])
                info_list.append(Empty(pos))
                this.value = lambda x: "[MASK]"
                return 0
            elif "replace" in slot_attributes.keys():
                #new_value = random.choice(synonyms[this.value])
                info_list.append(Replace(this.value))
                this.value = lambda x: "[MASK]"
                return 0
            else:
                return 0


class Empty():
    def __init__(self, pos):
        self.pos = pos
    def get_type(self):
        return "empty"
    def get_pos(self):
        return self.pos


class Replace():
    def __init__(self, original):
        self.original = original
        synonymList = set()
        wordNetSynset =  wn.synsets(original)
        for synSet in wordNetSynset:
            for synWords in synSet.lemma_names():
                synWords = synWords.replace("_", " ")
                synonymList.add(synWords)
        self.synonyms = synonymList
    def get_type(self):
        return "replace"
    def get_original(self):
        return self.original
    def get_synonyms(self):
        return self.synonyms