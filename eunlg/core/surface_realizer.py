import logging
import re

from core.pipeline import NLGPipelineComponent

log = logging.getLogger("root")


class SurfaceRealizer(NLGPipelineComponent):
    """
    Realizes a DocumentPlan as surface text.

    Assumes that the DocumentPlan corresponds to a structure wherein the root has
    some number of paragraphs as children and each paragraph in turn has some number
    of sentences as children.
    """

    def run(self, registry, random, language, document_plan):
        """
        Run this pipeline component.
        """
        log.info("Realizing to text")
        sequences = [c for c in document_plan.children]
        paragraphs = [self.realize(s, language) for s in sequences]
        output = ""
        for p in paragraphs:
            output += self.paragraph_start + p + self.paragraph_end
        return (output,)

    def realize(self, sequence, language):
        """Realizes a single paragraph."""
        output = ""
        for message in sequence.children:
            template = message.template
            # TODO: I used a quick fix for getting rid of unwanted integers
            sent = " ".join(
                [str(component.value) for component in template.components if component.value != ""]
            ).rstrip()
            # Temp fix: remove extra spaces occurring with braces and sometimes before commas.
            sent = re.sub(r"\(\s", r"(", sent)
            sent = re.sub(r"\s\)", r")", sent)
            sent = re.sub(r"\s,", r",", sent)

            if not sent:
                if self.fail_on_empty:
                    raise Exception("Empty sentence in surface realization")
                else:
                    continue
            sent = sent[0].upper() + sent[1:]
            output += self.sentence_start + sent + self.sentence_end
        return output


class HeadlineHTMLSurfaceRealizer(SurfaceRealizer):
    def __init__(self):
        self.paragraph_start = ""
        self.paragraph_end = ""
        self.sentence_end = ""
        self.sentence_start = ""
        self.fail_on_empty = True


class BodyHTMLSurfaceRealizer(SurfaceRealizer):
    def __init__(self):
        self.paragraph_start = "<p>"
        self.paragraph_end = "</p>"
        self.sentence_end = ". "
        self.sentence_start = ""
        self.fail_on_empty = False