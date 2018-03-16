import logging
from .pipeline import NLGPipelineComponent
from .document_plan import DocumentPlan, Relation
from .message_generator import NoMessagesForSelectionException
from .template_selector import TemplateMessageChecker

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

    def run(self, registry, random, language, scored_messages):
        """
        Run this pipeline component.
        """

        log.debug("Creating body document plan")

        # Root contains a sequence of children
        dp = DocumentPlan(children=[], relation=Relation.SEQUENCE)

        nuclei = []
        all_messages = scored_messages

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

            nuclei.append(message)
            messages = [message]
            current_location = message.fact.where_2
            scored_messages = [m for m in scored_messages if m.fact is not message.fact]
            core_messages = [m for m in core_messages if m.fact is not message.fact]

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
                    scored_messages = [m for m in scored_messages if m.fact is not sat_fact]
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
        nuclei_who_2 = [nucleus.fact.who_2 for nucleus in nuclei]
        modified = [msg for msg in candidates if msg.fact.who_2 not in nuclei_who_2]
        return modified

    def _encourage_similarity(self, candidates, nucleus):
        # Drop the messages that we won't consider at all instead of dropping the score to zero. This is much faster,
        # especially in cases where there are a lot of messages only a few of which would be left with a non-zero score.
        modified = [msg for msg in candidates if (nucleus.fact.where_2 == msg.fact.where_2 and nucleus.fact.who_2 == msg.fact.who_2)]

        return modified

    def _add_satellite(self, satellite, messages):
        for idx, msg in enumerate(messages):
            if type(msg) is DocumentPlan:
                continue
            rel = self._check_relation(satellite, msg)
            if rel != Relation.SEQUENCE:
                children = [msg, satellite]
                messages[idx] = DocumentPlan(children, rel)
                break
            rel = self._check_relation(msg, satellite)
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

        # Comparison of the same what_type between different place, time or entity
        if (fact_1.where_2 != fact_2.where_2 or fact_1.who_2 != fact_2.who_2 or fact_1.when_2 != fact_2.when_2) and \
                (fact_1.what_2 == fact_2.what_2):
            return Relation.CONTRAST

        # msg_1 is an elaboration of msg_2
        elif self._is_elaboration(fact_1, fact_2):
            return Relation.ELABORATION
        elif self._is_exemplification(fact_1, fact_2):
            return Relation.EXEMPLIFICATION
        return Relation.SEQUENCE

    def _is_elaboration(self, fact1, fact2):
        """

        :param fact1:
        :param fact2:
        :return: True, if fact1 is an elaboration of fact2, False otherwise
        """
        elaboration = {"total_votes": ["percentage_votes", "total_votes_rank", "total_votes_rank_reverse"],
                       "total_votes_change": ["total_votes_change_rank", "total_votes_change_rank_reverse"],
                       "seats": ["seats_rank", "seats_rank_reverse"],
                       }
        same_context = [fact1.where_2, fact1.when_2, fact1.who_2] == [fact2.where_2, fact2.when_2, fact2.who_2]
        # rank and rank_reverse are elaborated by the base values
        if not same_context:
            return False
        if "rank" in fact2.what_type_2:
            if "reverse" in fact2.what_type_2:
                return fact1.what_type_2 == fact2.what_type_2[:-13]
            return fact1.what_type_2 == fact2.what_type_2[:-5]
        if fact1.what_type_2 == "total_votes" and fact2.what_type_2 == "percentage_votes":
            return True
        return False

    def _is_exemplification(self, fact1, fact2):
        """
        Should check, whether fact1 is an exemplification of fact 2. This type doesn't exist at the moment, so
        will always return False
        :param fact1:
        :param fact2:
        :return:
        """
        return False
