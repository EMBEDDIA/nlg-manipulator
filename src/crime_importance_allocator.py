from core import NLGPipelineComponent
import math
import logging
import paramconfig as pfg
log = logging.getLogger('root')


class CrimeImportanceSelector(NLGPipelineComponent):
    def run(self, registry, random, language, messages):
        """
        Runs this pipeline component.
        """
        facts = messages
        scored_messages = self.score_importance(facts, registry)
        sorted_scored_messages = sorted(scored_messages, key=lambda x: float(x.score), reverse=True)
        return (sorted_scored_messages, )

    def score_importance(self, messages, registry):
        for msg in messages:
            msg.score = self.score_importance_single(msg, registry)
        return messages

    def score_importance_single(self, message, registry):
        fact = message.fact
        outlier_score = fact.outlierness or 1

        # importance of location types - where_type_score
        pass

        # importance of location size
        pass

        # importance of locations
        where_type_score = 1

        # importance of fact
        def get_interestingness(wht_tpe):
            wht_tpe = wht_tpe

            # Assign the parameters
            parm_dict = pfg.crime_parameters

            # Get the interestingness value
            var = wht_tpe.split("_")[0]
            wht_tpe_score = parm_dict[var]

            return wht_tpe_score

        what_type_score = get_interestingness(fact.what_type_2)
        # what_type_score = 1

        # importance of value
        what_score = what_type_score * outlier_score

        # importance of time
        when_score = min(1, (1 / (2019 - fact.when_2)**2))

        # total importance score
        message_score = where_type_score * what_score
        # message_score = "{:.5f}".format(message_score)

        if "_rank" in fact.what_type_2:
            message_score *= math.pow(0.7, fact.what_1 - 1)

        if "_reverse" in fact.what_type_2:
            if "_change" in fact.what_type_2:
                message_score *= 0.7
            else:
                message_score *= 0.25

        # During fact selection, some facts were marked as inherently less important (for the current article)
        # Scale the importance if this was specified
        if message.importance_coefficient is not None:
            message_score *= message.importance_coefficient

        return message_score
