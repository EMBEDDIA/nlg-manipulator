import logging
from .pipeline import NLGPipelineComponent
from .document_plan import DocumentPlan, Relation
from .message_generator import NoMessagesForSelectionException
from .template_selector import TemplateMessageChecker
import re

log = logging.getLogger('root')

# For now, these parameters are hard-coded
MIN_PARAGRAPHS_PER_DOC = 3  # Try really hard to get at least this many
MAX_PARAGRAPHS_PER_DOC = 5
SENTENCES_PER_PARAGRAPH = 6
# How many messages are we allowed to take from the expanded set
MAX_EXPANDED_NUCLEI = 2

END_STORY_RELATIVE_TRESHOLD = 0.2
END_STORY_ABSOLUTE_TRESHOLD = 2.0


class HeadlineDocumentPlanner(NLGPipelineComponent):

    def run(self, registry, random, language, scored_messages):
        """
        Run this pipeline component.
        """
        
        log.debug("Creating headline document plan")

        # Root contains a sequence of children
        dp = DocumentPlan(children=[], relation=Relation.SEQUENCE)

        headline_message = scored_messages[0]
        all_messages = scored_messages

        dp.children.append(
            DocumentPlan(children=[headline_message], relation=Relation.SEQUENCE)
        )

        return (dp, all_messages)


class BodyDocumentPlanner(NLGPipelineComponent):
    """
    NLGPipeline that creates a DocumentPlan from the given nuclei and satellites.
    """

    # The capture groups are: (unit)(normalized)(percentage)(change)(grouped_by)(rank)
    value_type_re = re.compile(
        r'^([0-9_a-z]+?)(_normalized)?(_percentage)?(_change)?(?:(?:_grouped_by)(_time_place|_crime_time))?(_rank(?:_reverse)?)?$')

    def run(self, registry, random, language, scored_messages):
        """
        Run this pipeline component.
        """

        log.debug("Creating body document plan")

        # Root contains a sequence of children
        dp = DocumentPlan(children=[], relation=Relation.SEQUENCE)

        nuclei = []
        all_messages = scored_messages

        # Drop messages with rank or rank_reverse values of more than 4 and messages with comparisons between
        # municipalities using the reported values instead of normalized or percentage values
        scored_messages = [msg for msg in scored_messages
                           # drop the message if it is about a rank or rank_reverse of more than 4 ...
                           if not ((self.value_type_re.match(msg.fact.what_type_2).group(6) and msg.fact.what_2 > 4)
                                   # ... or if the message is not normalized ...
                                   or (not (self.value_type_re.match(msg.fact.what_type_2).group(2)
                                            # ... or percentage ...
                                            or self.value_type_re.match(msg.fact.what_type_2).group(3))
                                       # ... and is comparing different municipalities
                                       and self.value_type_re.match(msg.fact.what_type_2).group(5) == '_crime_time'))]

        # In the first paragraph, don't ever use a message that's been added during expansion
        # These are recognisable by having a <1 importance coefficient
        core_messages = [sm for sm in scored_messages if sm.importance_coefficient >= 1.]
        if not core_messages:
            raise NoMessagesForSelectionException

        # Prepare a template checker
        template_checker = TemplateMessageChecker(registry.get("templates")[language], all_messages)

        # The children of the root are sequences of messages, with the nuclei
        # as first elements.
        max_score = 0.0
        expanded_nuclei = 0
        # Keep track of what location is currently being talked about
        current_location = None
        for par_num in range(MAX_PARAGRAPHS_PER_DOC):
            if (par_num == 0 and len(core_messages)) or expanded_nuclei >= MAX_EXPANDED_NUCLEI:
                penalized_candidates = self._penalize_similarity(core_messages, nuclei)
            else:
                penalized_candidates = self._penalize_similarity(scored_messages, nuclei)

            if len(penalized_candidates) == 0:
                break

            for message in penalized_candidates:
                require_location = current_location is None or message.fact.where_2 != current_location
                # Check whether this nucleus is even expressable, given our templates and contextual requirements
                # (Currently no contextual requirements, but location expression will soon be constrained)
                # If the message can't be expressed, choose another one
                if template_checker.exists_template_for_message(message, location_required=require_location):
                    break
            else:
                # Couldn't express ANY of the messages! V. unlikely to happen
                # Use the first one and let later stages deal with the problems

                message = penalized_candidates[0]

            if message.score == 0:
                break

            # Once we've got the min pars per doc, we can apply stricter tests for whether it's worth continuing
            if par_num >= MIN_PARAGRAPHS_PER_DOC:
                if message.score < max_score * END_STORY_RELATIVE_TRESHOLD:
                    # We've dropped to vastly below the importance of the most important nucleus: time to stop nattering
                    log.info("Nucleus score dropped below 20% of max score so far, stopping adding paragraphs")
                    break
                if message.score < END_STORY_ABSOLUTE_TRESHOLD:
                    # This absolute score is simply very low, so we're probably scraping the bottom of the barrel
                    log.info("Nucleus score dropped to a low absolute value, stopping adding paragraphs")
                    break

            # Check whether the added nucleus was from the expanded set
            if message.importance_coefficient < 1.:
                expanded_nuclei += 1

            message.prevent_aggregation = True
            nuclei.append(message)
            messages = [message]
            current_location = message.fact.where_2
            # Drop the chosen message from the lists of remaining messages
            scored_messages = [m for m in scored_messages if m is not message]
            core_messages = [m for m in core_messages if m is not message]

            # Select satellites
            par_length = 1
            satellite_candidates = self._encourage_similarity(scored_messages, message)
            for satellite in satellite_candidates:
                score = satellite.score
                sat_fact = satellite.fact
                if score == 0:
                    break
                require_location = current_location is None or sat_fact.where_2 != current_location
                # Only use the fact if we have a template to express it
                # Otherwise skip to the next most relevant
                if template_checker.exists_template_for_message(satellite, location_required=require_location):

                    self._add_satellite(satellite, messages)
                    # Drop the chosen message from the lists of remaining messages
                    scored_messages = [m for m in scored_messages if m is not satellite]
                    core_messages = [m for m in core_messages if m is not satellite]
                    par_length += 1
                    if par_length >= SENTENCES_PER_PARAGRAPH:
                        # Reached max length of par, stop generating
                        break

            dp.children.append(
                DocumentPlan(children=messages, relation=Relation.SEQUENCE)
            )

            max_score = max(message.score, max_score)

        return (dp, all_messages)

    def _penalize_similarity(self, candidates, nuclei):
        if not nuclei:
            return candidates
        # Pick only messages about crimes that belong to DIFFERENT generic crime type but share a location
        for nucleus in nuclei:
            candidates = [msg for msg in candidates
                    if (nucleus.fact.where_2 == msg.fact.where_2
                        and nucleus.fact.what_type_2.split("_")[0] != msg.fact.what_type_2.split("_")[0])]
        return candidates

    def _encourage_similarity(self, candidates, nucleus):
        # Pick only messages about crimes that belong to the same generic crime type (in other words, that have a crime
        # type starting with the same prefix as the nucleus
        modified = [msg for msg in candidates
                    if (nucleus.fact.where_2 == msg.fact.where_2
                        and nucleus.fact.what_type_2.split("_")[0] == msg.fact.what_type_2.split("_")[0])]
        return modified

    def _add_satellite(self, satellite, messages):
        # ToDo: Decide how to deal with the nuclei. Can they be elaborated by something else? Can they be used to
        # elaborate less important message? At the moment they cannot be either part of an elaborate relation.
        for idx, msg in enumerate(messages):
            if type(msg) is DocumentPlan or msg.prevent_aggregation:
                continue
            rel = self._check_relation(msg, satellite)
            if rel != Relation.SEQUENCE:
                children = [msg, satellite]
                messages[idx] = DocumentPlan(children, rel)
                break
            rel = self._check_relation(satellite, msg)
            if rel != Relation.SEQUENCE:
                children = [satellite, msg]
                messages[idx] = DocumentPlan(children, rel)
                break
        else:
            messages.append(satellite)

    def _check_relation(self, msg_1, msg_2):
        """
        Returns the Relation type between msg_1 and msg_2
        :param msg_1:
        :param msg_2:
        :return:
        """
        fact_1 = msg_1.fact
        fact_2 = msg_2.fact

        # Comparison of the same what_type between different place or time
        if (fact_1.where_2 != fact_2.where_2 or fact_1.when_2 != fact_2.when_2) and \
                (fact_1.what_type_2 == fact_2.what_type_2):
            return Relation.CONTRAST

        # msg_2 is an elaboration of msg_1
        elif self._is_elaboration(fact_1, fact_2):
            return Relation.ELABORATION
        elif self._is_exemplification(fact_1, fact_2):
            return Relation.EXEMPLIFICATION
        return Relation.SEQUENCE

    def _is_elaboration(self, fact1, fact2):
        return False


        # TODO: FIX THIS
        """

        :param fact1:
        :param fact2:
        :return: True, if fact2 is an elaboration of fact1, False otherwise
        """
        same_context = (fact1.where_2, fact1.when_2) == (fact2.where_2, fact2.when_2)
        if not same_context:
            return False
        # An elaboration can't have the same fact type in both facts.
        if fact1.what_type_2 == fact2.what_type_2:
            return False
        value_type_re = re.compile(r'(percentage_|total_)?([a-z]+)(_change)?(_rank(_reverse)?)?')
        match_1 = value_type_re.match(fact1.what_type_2)
        match_2 = value_type_re.match(fact2.what_type_2)
        # If the facts have different base unit, they can't have an elaboration relation
        if match_1.group(2) != match_2.group(2):
            return False
        # rank and rank_reverse are elaborated by the base values
        if match_1.group(4) is not None:
            return match_1.group(1,3) == match_2.group(1,3)
        # Rank and rank_reverse cannot be elaborations
        if match_2.group(4) is not None:
            return False
        # Change is an elaboration of the result value
        if match_2.group(3) is not None and match_1.group(1) == match_2.group(1):
            return True
        # total value is an elaboration of a percentage value
        if match_1.group(3) == match_2.group(3) == None and match_1.group(1) == "percentage_":
            return True
        return False

    def _is_exemplification(self, fact1, fact2):
        """
        Should check, whether fact2 is an exemplification of fact1. This type doesn't exist at the moment, so
        will always return False
        :param fact1:
        :param fact2:
        :return:
        """
        return False
