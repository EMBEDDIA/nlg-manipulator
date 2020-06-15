import logging
import re
import random
import nltk
from operator import itemgetter 
import pandas as pd
from uralicNLP import uralicApi
import numpy as np
import pickle

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
        bert = Bert(language)

        for message in sequence.children:
            template = message.template
            # TODO: I used a quick fix for getting rid of unwanted integers
            sent = [str(component.value) for component in template.components if component.value != ""]
            original_sent = sent.copy()
            # TODO: This can now only handle one masked slot per sentence.
            if "[MASK]" in sent:
                info = info_list.pop(0)
                options = []
                all_options = []

                if info.get_type() == "empty":
                    how = info.get_type()
                    word_type = info.get_pos()
                    sentence_str = " ".join(sent)
                    proposed_words, all_options = bert.get_words(sentence_str, language, info.get_pos())

                    for i, s in enumerate(sent):
                        if s == "[MASK]":
                            # # POS tag proposed words
                            # tagged = nltk.pos_tag(proposed_words)
                            # # Get subset with desired POS tag
                            #proposed_words = [pair[0] for pair in proposed_words]

                            original_sent[i] = "____"
                            options = proposed_words
                            try:    
                                new = random.choice(proposed_words)
                                options.remove(new)
                            except:
                                new = "[EMPTY]"
                            sent[i] = new

                elif info.get_type() == "replace":
                    how = info.get_type()
                    for i, s in enumerate(sent):
                        if s == "[MASK]":

                            candidates = info.get_synonyms()
                            original = info.get_original()
                            sentence_str = " ".join(sent)
                            options, all_options = bert.choose_word(sentence_str, candidates, original)
                            print(options)
                            try:
                                new = random.choice(options).replace("_", " ")
                                options.remove(new)
                            except:
                                new = original
                            sent[i] = new
                            word_type = nltk.pos_tag(original)[0][1]
                            original_sent[i] = "_{}_".format(original)   
                            

                if type(sent) == list:
                    sent = " ".join(sent)
            
                if type(original_sent) == list:
                    original_sent = " ".join(original_sent)

                # Temp fix: remove extra spaces occurring with braces and sometimes before commas.
                sent = re.sub(r"\(\s", r"\(", sent)
                sent = re.sub(r"\s\)", r"\)", sent)
                sent = re.sub(r"\s,", r",", sent)
                try:
                    options = options[:6]
                    all_options = all_options[:6]
                except:
                    pass
                if len(options) == 0 or len(all_options) == 0:
                    pass
                elif "[EMPTY]" in sent:
                    pass
                else:
                    original_sent = re.sub(r"\(\s", r"\(", original_sent)
                    original_sent = re.sub(r"\s\)", r"\)", original_sent)
                    original_sent = re.sub(r"\s,", r",", original_sent)
                    new_row = pd.DataFrame({
                        "How":[how], 
                        "Word type": [word_type],
                        "Original sentence":["{}{}.".format(original_sent[0].capitalize(), original_sent[1:])], 
                        "Modified sentence":["{}{}.".format(sent[0].capitalize(), sent[1:])], 
                        "Original word":[info.get_original()], 
                        "Approved":[", ".join(options)], 
                        "Disapprove": [", ".join(all_options)]
                    })
                    new_row.to_csv("{}_output.csv".format(language), sep=",", mode='a', header=False, index=False, encoding="utf-8")
            
            if type(sent) == list:
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

    def tag_finnish(self, words):
        tagged = list()
        id2word_fi, word2id_fi, matrix_fi = self._load_emb("cc.fi.300.vec.fi-en-sup.emb")
        id2word_en, word2id_en, matrix_en = self._load_emb("cc.en.300.vec.fi-en-sup.emb")

        for w in words:
            print(w)
            try:
                word_id = word2id_fi[w[1]]
            except:
                continue
            word_vec = matrix_fi[word_id]
            closest = self._closest_words(word_vec, matrix_en, id2word_en, 1)

            pos = nltk.pos_tag(closest)[0][1]   
            tagged.append(w + (pos,))
 
            
        return tagged
    
    def insert(self, idx: int, base: torch.tensor, insert: torch.tensor) -> torch.tensor:
        prefix = base[0][:idx]
        suffix = base[0][idx + 1:]
        combined = torch.cat([prefix, insert, suffix])
        combined = combined.reshape((1, combined.shape[0]))
        return combined

    def predict(
        self,
        sentence: str, 
        min_masked_tokens: int, 
        max_masked_tokens: int, 
        k: int
        ) -> list(tuple()):
        base = torch.tensor([self.tokenizer.encode(sentence, add_special_tokens=True)])
        mask_idx_in_base = torch.where(base == self.tokenizer.mask_token_id)[1][0].item()

        #assert min_masked_tokens < max_masked_tokens
        #assert min_masked_tokens >= 1
        #preds: Dict[str, Dict[str, float]] = {}
        pairs = list()
        for i in range(min_masked_tokens, max_masked_tokens + 1):
            masked_insert = torch.tensor([self.tokenizer.mask_token_id]*i)

            template = self.insert(mask_idx_in_base, base, masked_insert)
            masked_indices = torch.where(template == self.tokenizer.mask_token_id)[1].tolist()

            logits = self.model(template)[0][:, masked_indices]
            probabilities, predictions = torch.softmax(logits, dim=2).topk(k)
            probabilities = probabilities.reshape((k, len(masked_indices)))
            predictions = predictions.reshape((k, len(masked_indices)))

            for probs, predicted_indices in zip(probabilities, predictions):
                filled_template = template.clone()
                filled_template[:, masked_indices] = predicted_indices

                sentence = self.tokenizer.decode(filled_template[0,:])
                word = self.tokenizer.decode(predicted_indices)

                pairs.append((probs.mean().item(), word))

        return pairs

    def get_words(self, sentence_str, language, pos):
        # encode sentence with a masked token in the middle
        K = 200
        MIN_MASKED_TOKENS = 1
        MAX_MASKED_TOKENS = 1
        predictions = self.predict(sentence_str, MIN_MASKED_TOKENS, MAX_MASKED_TOKENS, K)
        predictions = [p for p in predictions if "[UNK]" not in p[1]]
        predictions = [p for p in predictions if "#" not in p[1]]

        import re
        new_predictions = list()
        for p in predictions:
            match = re.search('^[a-zA-Z]+$', p[1])
            if match and len(match.group(0)) > 1:
                new_predictions.append((p[0], match.group(0)))

        new_predictions = sorted(new_predictions, key=lambda x: x[0], reverse=True)

        if language == "en":
            new_predictions = [p + (nltk.pos_tag([p[1]])[0][1],) for p in new_predictions]
            approved = [pair[1] for pair in new_predictions if pair[0] >= 0.0005 and pair[2] == pos]
            disapproved = [pair[1] for pair in new_predictions if pair[0] < 0.0005 and pair[2] == pos]
        elif language == "fi":
            
            # Do not consider POS
            # approved = [pair[1] for pair in new_predictions if pair[0] >= 0.001]
            # disapproved = [pair[1] for pair in new_predictions if pair[0] < 0.001]

            # Consider POS
            new_predictions = self.tag_finnish(new_predictions)
            approved = [pair[1] for pair in new_predictions if pair[0] >= 0.0005 and pair[2] == pos]
            disapproved = [pair[1] for pair in new_predictions if pair[0] < 0.0005 and pair[2] == pos]

        print(approved)
        return approved, disapproved


    def choose_word(self, sentence_str, candidates, original):
        encoded_sentence = torch.tensor(self.tokenizer.encode(sentence_str, add_special_tokens=True))
        masked_index = torch.where(encoded_sentence == self.tokenizer.mask_token_id)[0].item()
        sentence_prefix = encoded_sentence[:masked_index]
        sentence_suffix = encoded_sentence[masked_index+1:]

        probabilities_and_candidates = list()

        for candidate in candidates:
            encoded_candidate = torch.tensor(self.tokenizer.encode(candidate, add_special_tokens=False))
            masked_candidate = torch.tensor([self.tokenizer.mask_token_id for item in encoded_candidate])
            
            new_sentence_encoding = torch.cat([sentence_prefix, masked_candidate, sentence_suffix])
            new_sentence_encoding = new_sentence_encoding.reshape((1, len(new_sentence_encoding)))

            masked_indices = torch.where(new_sentence_encoding == self.tokenizer.mask_token_id)[1].tolist()

            predictions = self.model(new_sentence_encoding)[0][:, masked_indices]

            probs = torch.nn.functional.softmax(predictions, dim=-1)

            probs = probs[0].tolist()
            
            candidate_part_probabilities = list()
            for i, candi in enumerate(encoded_candidate):
                candidate_part_probabilities.append(probs[i][candi])

            from statistics import mean
            candi_prob_mean = mean(candidate_part_probabilities)

            probabilities_and_candidates.append((candi_prob_mean, candidate))
        
        probabilities_and_candidates = sorted(probabilities_and_candidates, key=lambda x: x[0], reverse=True)
        probabilities_and_candidates = [p for p in probabilities_and_candidates if "[UNK]" not in p[1]]
        print(probabilities_and_candidates)
        approved = [pair[1] for pair in probabilities_and_candidates if pair[0] >= 0.0005]
        disapproved = [pair[1] for pair in probabilities_and_candidates if pair[0] < 0.0005]

        try:
            approved.remove(original)
        except:
            pass
        try:
            disapproved.remove(original)
        except:
            pass
        # if approved == []:
        #     return [original], disapproved

        return approved, disapproved

    def _load_emb(self, embfile):
        """Loads the embeddings and saves them as pickle for quicker loading next time."""
        import os

        dir_path = os.path.dirname(os.path.realpath(__file__))
        embfile = os.path.join(dir_path, embfile)

        try:
            with open(embfile.split('/')[-1]+'.pickle', 'rb') as f:
                word_to_id, id_to_word, embmatrix = pickle.load(f)
        except:
            word_to_id = {}
            id_to_word = []
            embmatrix = []
            idcount = 0
            with open(embfile, 'r') as reader:
                reader.readline()
                for line in reader:
                    line = line.split()
                    word = line[0]
                    id_to_word.append(word)
                    word_to_id[word] = idcount
                    try:
                        vector = np.asarray([float(v) for v in line[1:]])
                        vector = vector/np.sqrt(vector.dot(vector))
                    except:
                        continue
                    if len(vector) != 300:
                        continue
                    else:
                        embmatrix.append(vector)
                        idcount += 1
            with open(embfile.split('/')[-1]+'.pickle', 'wb') as f:
                pickle.dump([word_to_id, id_to_word, embmatrix], f, pickle.HIGHEST_PROTOCOL)
        return id_to_word, word_to_id, np.asarray(embmatrix)
        
    def _closest_words(self, vector, embmatrix, id_to_word, n):
        """Returns n closest words to vector 'vector' among words in embeddings embmatrix."""
        # embmatrix = np.array([a,b,c,d,e,f,g...]), where a,b,c,d... are word vectors
        dotproduct = embmatrix.dot(vector)
        maxn_indices = dotproduct.argsort()[-n:][::-1]
        words = [id_to_word[int(id)] for id in maxn_indices]
        return words

