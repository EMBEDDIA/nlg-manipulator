import logging
import random
from .pipeline import NLGPipelineComponent
from config import MANIPULATORS

log = logging.getLogger("root")

adverbs = ["suprisingly", "luckily", "sadly"]


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
            log.info("Runnin the WordIntroducer component with language {}".format(language))
            self._recurse(document_plan)
        return (document_plan,)

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
                log.info("THE SLOT TYPE IS {}".format(slot_type))
            except AttributeError:
                log.info("Got an AttributeError when checking slot_type in realize_slots. Probably not a slot.")
                slot_type = "n/a"
            if slot_type == "empty":
                new_value = random.choice(adverbs)
                this.value = lambda x: new_value
                return 0
            else:
                return 0
