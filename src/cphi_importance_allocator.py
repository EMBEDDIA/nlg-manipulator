# FYI: needed to change the year to 2020

from core import NLGPipelineComponent
import math
import logging
import paramconfig as pfg
log = logging.getLogger('root')


class CPHIImportanceSelector(NLGPipelineComponent):
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

        # # Early stop
        # if not '2017' in str(fact.when_2):
        #     return 0

        # # Certain crimes haunt the data
        # if 'life_killing_total' in fact.what_type or 'life_infanticide_total' in fact.what_type:
        #     return 0

        # importance of fact
        category = fact.what_type.split('_')[0]
        what_type_score = pfg.category_scores.get(category, 1)
        if '_rank_reverse' in fact.what_type:
            what_type_score *= pfg.rank_reverse_weight
        elif '_rank' in fact.what_type:
            what_type_score *= pfg.rank_weight
        elif not '_change' in fact.what_type and fact.what == 0:
            return 0

        if '_trend' in fact.what_type:
            what_type_score *= 500

        # importance of value
        what_score = what_type_score * outlier_score

        when_score = 20
        # importance of time
        if fact.when_type == "year":
            # For each year, the importance is simply 1 / diff,
            # where diff is the difference between the next year (now 2020)
            # and the year the fact discusses. That is, facts regarding
            # the current year get a multiplier of 1, the year before that
            # gets a multiplied of 0.5, the year before that 0.11... etc.
            when_score *= min(1, (1 / (2020 - int(fact.when_2))**2))
            when_score *= 2
        elif fact.when_type == "month":
            # For months, the penalty is scaled linearly between the multiplers
            # of the year it belongs to and the previous year. The notable
            # complication here is that we consider the year to consists of 13
            # months, so that (for example) the year 2020 is considered to be
            # more newsworthy than the month 2020M12 by the same amount that
            # 2020M12 is more newsworthy than 2020M11.
            year, month = fact.when_2.split('M')
            this_year = min(1, (1 / (2020 - int(year)))**2)
            prev_year = min(1, (1 / (2020 - (int(year)-1)))**2)
            month_effect = (this_year - prev_year) / (int(month)+1)
            when_score *= this_year - month_effect

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
