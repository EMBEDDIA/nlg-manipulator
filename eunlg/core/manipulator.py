import logging
import random
from .pipeline import NLGPipelineComponent
from config import MANIPULATORS
from nltk.corpus import wordnet as wn
import numpy as np
import pickle
from uralicNLP import uralicApi
import editdistance as ed

log = logging.getLogger("root")

#uralicApi.download("fin")

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
            self._recurse(document_plan, language)
        return (document_plan, info_list)

    def _recurse(self, this, language):
        try:
            idx = 0
            while idx < len(this.children):
                slots_added = self._recurse(this.children[idx], language)
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
                info_list.append(Replace(this.value, language))
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
    def get_original(self):
        return "[empty]"


class Replace():
    def __init__(self, original, language):
        self.original = original
        self.best_analysis = None

        synonymSet = set()

        if language == "en":
            # synonymSet.add(self.original)
            
            wordNetSynset =  wn.synsets(original.replace(" ", "_").replace("-", "_"))
            for synSet in wordNetSynset:
                for synWords in synSet.lemma_names():
                    # if "_" not in synWords:
                    #     synonymSet.add(synWords)
                    synonymSet.add(synWords.replace("_", " "))

        elif language == "fi":
            analysed = uralicApi.analyze(self.original, "fin")
            lemmas = uralicApi.lemmatize(self.original, "fin")

            synonymSet.add(self.original)

            analyses = [a[0] for a in analysed]

            id2word_fi, word2id_fi, matrix_fi = self._load_emb("cc.fi.300.vec.fi-en-sup.emb")
            id2word_en, word2id_en, matrix_en = self._load_emb("cc.en.300.vec.fi-en-sup.emb")
            
            for lemma in lemmas:
                try:
                    word_id = word2id_fi[lemma]
                    word_vec = matrix_fi[word_id]
                    closest = self._closest_words(word_vec, matrix_en, id2word_en, 1)

                    temp = set()
                    for c in closest:
                        wordNetSynset =  wn.synsets(c.replace(" ", "_").replace("-", "_"))
                        for synSet in wordNetSynset:
                            for synWords in synSet.lemma_names():
                                temp.add(synWords.replace("_", " "))
                    for s in temp:
                        try:
                            word_id = word2id_en[s]
                            word_vec = matrix_en[word_id]
                            closest = self._closest_words(word_vec, matrix_fi, id2word_fi, 1)
                            # split = self.best_analysis.split("+")
                            for c in closest:
                                for a in analyses:
                                    split = a.split("+")
                                    try:
                                        split[0] = c
                                        changed = uralicApi.generate("+".join(split), "fin")[0][0]
                                        synonymSet.add(changed)
                                    except:
                                        pass         
                        except:
                            pass
                except:
                    pass
        self.synonyms = list(synonymSet)
    def get_type(self):
        return "replace"
    def get_original(self):
        return self.original
    def get_synonyms(self):
        return self.synonyms
    def get_best_analysis(self):
        return self.best_analysis


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
