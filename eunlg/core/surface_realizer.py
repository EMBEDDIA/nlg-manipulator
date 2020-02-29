import logging
import re
import random
import nltk

from core.pipeline import NLGPipelineComponent

log = logging.getLogger("root")


class SurfaceRealizer(NLGPipelineComponent):
    """
    Realizes a DocumentPlan as surface text.

    Assumes that the DocumentPlan corresponds to a structure wherein the root has
    some number of paragraphs as children and each paragraph in turn has some number
    of sentences as children.
    """

    def run(self, registry, random, language, document_plan, info_list):
        """
        Run this pipeline component.
        """
        log.info("Realizing to text")
        if language.endswith("-head"):
            language = language[:-5]
            log.debug("Language had suffix '-head', removing. Result: {}".format(language))
        sequences = [c for c in document_plan.children]
        paragraphs = [self.realize(s, language, info_list) for s in sequences]
        output = ""
        for p in paragraphs:
            output += self.paragraph_start + p + self.paragraph_end
        return (output,)

    def realize(self, sequence, language, info_list):
        """Realizes a single paragraph."""
        output = ""
        for message in sequence.children:
            template = message.template
            # TODO: I used a quick fix for getting rid of unwanted integers
            sent = " ".join(
                [str(component.value) for component in template.components if component.value != ""]
            ).rstrip()

            # TODO: This can now only handle one masked slot per sentence.
            bert = Bert(language)
            if "[MASK]" in sent:

                proposed_words = bert.get_words(sent)
                info = info_list.pop()

                sent = sent.split(" ")

                if info.get_type() == "empty":
                    for i, s in enumerate(sent):
                        if s == "[MASK]":
                            # POS tag proposed words
                            tagged = nltk.pos_tag(proposed_words)
                            log.info(tagged)

                            # Get subset with desired POS tag
                            proposed_words = [pair[0] for pair in tagged if pair[1] == info.get_pos()]

                            log.info(proposed_words)

                            new = random.choice(proposed_words)
                            sent[i] = new

                elif info.get_type() == "replace":
                    for i, s in enumerate(sent):
                        if s == "[MASK]":

                            # Find intersection of synonym set of original word and BERT proposed words
                            synonyms = self.intersection(proposed_words, info.get_synonyms())
                            try:
                                new = random.choice(synonyms)
                                sent[i] = new
                            except:
                                # If intersection is empty set, use original word
                                sent[i] = info.get_original()

                sent = " ".join(sent)


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


    def intersection(self, lst1, lst2): 
        temp = set(lst2) 
        lst3 = [value for value in lst1 if value in temp] 
        return lst3 


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


from transformers import *
import torch

from config import BERTS

class Bert():
    def __init__(self, language):
        self.tokenizer = BertTokenizer.from_pretrained(BERTS[language])
        self.model = BertForMaskedLM.from_pretrained(BERTS[language])

    def get_words(self, sentence_str):
        # encode sentence with a masked token in the middle
        print(sentence_str)
        sentence = torch.tensor([self.tokenizer.encode(sentence_str, add_special_tokens=True)])

        # Identify the masked token position
        masked_index = torch.where(sentence == self.tokenizer.mask_token_id)[1].tolist()[0]

        # Get the top-n answers
        predictions = self.model(sentence)[0][:, masked_index].topk(200).indices

        return self.tokenizer.decode(predictions.tolist()[0]).split(" ")
