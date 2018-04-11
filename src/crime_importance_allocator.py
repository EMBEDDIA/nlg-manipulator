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
        category = fact.what_type.split('_')[0]
        what_type_score = pfg.category_scores.get(category, 1)
        if '_rank_reverse' in fact.what_type:
            what_type_score *= pfg.rank_reverse_weight
        elif '_rank' in fact.what_type:
            what_type_score *= pfg.rank_weight

        # importance of value
        what_score = what_type_score * outlier_score

        # importance of time
        if fact.when_type == "year":
            when_score = min(1, (1 / (2019 - int(fact.when_2))**2))
        elif fact.when_type == "month":
            year, month = fact.when.split('M')
            when_score = min(1, (1 / (2019 - int(year))**2))
            when_score *= min(1, (1 / (13 - int(month))))

        # total importance score
        message_score = where_type_score * what_score * when_score
        # message_score = "{:.5f}".format(message_score)

        if "_rank" in fact.what_type:
            message_score *= math.pow(0.7, fact.what - 1)

        if "_reverse" in fact.what_type:
            if "_change" in fact.what_type:
                message_score *= 0.7
            else:
                message_score *= 0.25

        # During fact selection, some facts were marked as inherently less important (for the current article)
        # Scale the importance if this was specified
        if message.importance_coefficient is not None:
            message_score *= message.importance_coefficient

        return message_score
