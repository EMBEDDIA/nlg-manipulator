from core import NLGPipelineComponent
import math
import logging
import paramconfig as pfg
log = logging.getLogger('root')


class MunicipalElectionImportanceSelector(NLGPipelineComponent):
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
        what = fact.what_2
        what_type = fact.what_type_2
        who = fact.who_2
        who_type = fact.who_type_2
        where = fact.where_2
        where_type = fact.where_type_2
        when = fact.when_2
        outlier_score = fact.outlierness or 1

        # importance of names - who_score
        if who_type == "party":
            who_score = pfg.party_score
        if who_type == "candidate":
            who_score = pfg.candidate_score

        # importance of location types - where_type_score
        if where_type == "M":
            where_type_score = pfg.municipality_score
        if where_type == "C":
            where_type_score = pfg.country_score
        if where_type == "D":
            where_type_score = pfg.voting_district_score
        if where_type == "P":
            where_type_score = pfg.polling_station_score

        # importance of location size
        # logarithmic function

        # importance of locations
        # where_score = where_type_score * where_size_score

        # importance of fact
        what_type_score = 1

        if what_type == "seats":
            what_type_score = pfg.base_seats * pfg.comparison_empty * pfg.stats_empty

        if what_type == "seats_rank" or what_type == "seats_rank_reverse":
            what_type_score = pfg.base_seats * pfg.comparison_empty * pfg.stats_rank

        if what_type == "seats_change":
            what_type_score = pfg.base_seats * pfg.comparison_change * pfg.stats_empty

        if what_type == "seats_change_rank" or what_type == "seats_change_rank_reverse":
            what_type_score = pfg.base_seats * pfg.comparison_change * pfg.stats_rank

        if what_type == "seats_previous_election":
            what_type_score = pfg.base_seats * pfg.comparison_prev_election * pfg.stats_empty

        if what_type == "seats_previous_election_rank" or what_type == "seats_previous_election_rank_reverse":
            what_type_score = pfg.base_seats * pfg.comparison_prev_election * pfg.stats_rank

        if what_type == "total_votes":
            what_type_score = pfg.base_total_votes * pfg.comparison_empty * pfg.stats_empty

        if what_type == "total_votes_rank" or what_type == "total_votes_rank_reverse":
            what_type_score = pfg.base_total_votes * pfg.comparison_empty * pfg.stats_rank

        if what_type == "total_votes_change":
            what_type_score = pfg.base_total_votes * pfg.comparison_change * pfg.stats_empty

        if what_type == "total_votes_change_rank" or what_type == "total_votes_change_rank_reverse":
            what_type_score = pfg.base_total_votes * pfg.comparison_change * pfg.stats_rank

        if what_type == "percentage_votes":
            what_type_score = pfg.base_perc_votes * pfg.comparison_empty * pfg.stats_empty

        if what_type == "percentage_votes_change":
            what_type_score = pfg.base_perc_votes * pfg.comparison_change * pfg.stats_empty

        if what_type == "total_votes_previous_election":
            what_type_score = pfg.base_total_votes * pfg.comparison_prev_election * pfg.stats_empty

        if what_type == "total_votes_previous_election_rank" or what_type == "total_votes_previous_election_rank_reverse":
            what_type_score = pfg.base_total_votes * pfg.comparison_prev_election * pfg.stats_rank

        if what_type == "percentage_votes_previous_election":
            what_type_score = pfg.base_perc_votes * pfg.comparison_prev_election * pfg.stats_empty

        if what_type == "percentage_votes_previous_election_rank" or what_type == "percentage_votes_previous_election_rank_reverse":
            what_type_score = pfg.base_perc_votes * pfg.comparison_prev_election * pfg.stats_rank

        if what_type == "election_result":
            what_type_score = pfg.base_election_result * pfg.comparison_empty * pfg.stats_empty

        # importance of value
        what_score = what_type_score * outlier_score

        # importance of time
        if when == 2012:
            what_score = what_score / 4

        # total importance score
        message_score = who_score * where_type_score * what_score
        # message_score = "{:.5f}".format(message_score)

        if "_rank" in what_type:
            message_score *= math.pow(0.7, what - 1)

        if "_reverse" in what_type:
            if "_change" in what_type:
                message_score *= 0.7
            else:
                message_score *= 0.25

        # During fact selection, some facts were marked as inherently less important (for the current article)
        # Scale the importance if this was specified
        if message.importance_coefficient is not None:
            message_score *= message.importance_coefficient

        not_accepted = {"percentage_votes_rank", "percentage_votes_rank_reverse", "percentage_votes_change_rank", "percentage_votes_change_rank_reverse"}
        if what_type in not_accepted:
            message_score = pfg.low_importance

        return message_score
