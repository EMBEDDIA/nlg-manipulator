from .pipeline import NLGPipelineComponent
from .template import Template, Literal, Slot
from templates.substitutions import FactFieldSource
from .message import Message
from .document_plan import Relation

import logging
log = logging.getLogger('root')


class Aggregator(NLGPipelineComponent):

    def run(self, registry, random, language, document_plan):
        if log.isEnabledFor(logging.DEBUG):
            document_plan.print_tree()

        # Consider a sliding window of three Sentences: s_0, s_1, s_2 + knowledge of if the previous window resulted in a combination (P)
        # if (s_0 == s_1) and ((not P) or (not s_1 == s_2))
        log.debug("Aggregating")
        self._aggregate(registry, language, document_plan)

        if log.isEnabledFor(logging.DEBUG):
            document_plan.print_tree()

        return (document_plan, )

    def _aggregate_sequence(self, registry, language, this):
        log.debug("Visiting {}".format(this))

        previous_was_combined = True
        num_children = len(this.children)
        new_children = []
        for idx in range(0, num_children):
            if idx > 0:
                t0 = new_children[-1]
            else:
                t0 = None
            t1 = self._aggregate(registry, language, this.children[idx])

            log.debug("t0={}, t1={}".format(t0, t1))

            if self._same_prefix(t0, t1) and not previous_was_combined:
                previous_was_combined = True
                log.debug("Combining")
                new_children[-1] = self._combine(registry, language, new_children[-1], t1)
                log.debug("Combined, New Children: {}".format(new_children))

            else:
                previous_was_combined = False
                new_children.append(t1)
                log.debug("Did not combine. New Children: {}".format(new_children))

        this.children.clear()
        this.children.extend(new_children)
        return this

    def _aggregate_elaboration(self, registry, language, this):
        log.debug("Visiting {}".format(this))

        num_children = len(this.children)
        new_children = [this.children[0]]
        for idx in range(1, num_children):
            t0 = this.children[idx - 1]
            t1 = this.children[idx]

            log.debug("t0={}, t1={}".format(t0, t1))

            new_children[-1] = self._elaborate(registry, language, t0, t1)
            log.debug("Combined, New Children: {}".format(new_children))

        if len(new_children) == 1:
            return new_children[0]
        this.children.clear()
        this.children.extend(new_children)
        return this

    def _same_prefix(self, first, second):
        try:
            return first.components[0].value == second.components[0].value
        except AttributeError:
            return False

    def _combine(self, registry, language, first, second):
        log.debug("Combining {} and {}".format([c.value for c in first.components], [c.value for c in second.components]))
        combined = [c for c in first.components]
        for idx, other_component in enumerate(second.components):
            if idx >= len(combined):
                break
            this_component = combined[idx]
            if not self._are_same(this_component, other_component):
                break
        log.debug("idx = {}".format(idx))
        # ToDo! At the moment everything is considered either positive or negative, which is sometimes weird. Add neutral sentences.
        if (self._message_positive(first) != self._message_positive(second)):
            combined.append(Literal(registry.get('vocabulary').get(language, {}).get('inverse_combiner', "MISSING-COMBINER")))
        else:
            combined.append(Literal(registry.get('vocabulary').get(language, {}).get('default_combiner', "MISSING-COMBINER")))
        combined.extend(second.components[idx:])
        log.debug("Combined thing is {}".format([c.value for c in combined]))
        new_message = Message(facts=first.facts + [fact for fact in second.facts if fact not in first.facts], importance_coefficient=first.importance_coefficient)
        new_message.template = Template(combined)
        return new_message

    def _elaborate(self, registry, language, first, second):
        log.debug("Elaborating {} with {}".format([c.value for c in first.components], [c.value for c in second.components]))
        result = [c for c in first.components]
        try:
            first_type = first.facts[0].what_type
            second_type = second.facts[0].what_type
            if first_type + "_change" == second_type:
                result.append(Literal(
                    registry.get('vocabulary').get(language, {}).get('subord_clause_start', "MISSING-COMBINER")))
                result.append(Slot(FactFieldSource('what'), fact=second.facts[0]))
                result.append(Slot(FactFieldSource('what_type'), fact=second.facts[0]))
                result[-1].attributes['form'] = 'full'
                result.append(Literal(registry.get('vocabulary').get(language, {}).get('comparator', "MISSING-COMBINER")))
                result.append(Slot(FactFieldSource('when_1'), fact=second.facts[0]))
            else:
                result.append(Literal("("))
                result.append(Slot(FactFieldSource('what'), fact=second.facts[0]))
                result.append(Slot(FactFieldSource("what_type"), fact=second.facts[0]))
                attributes = {"form": "short", "case": "accusative"}
                result[-1].attributes = attributes
                result.append(Literal(")"))
        except KeyError:
            return self._combine(registry, language, first, second)
        new_message = Message(facts=first.facts + [fact for fact in second.facts if fact not in first.facts], importance_coefficient=first.importance_coefficient)
        new_message.template = Template(result)
        return new_message

    def _are_same(self, c1, c2):
        if c1.value != c2.value:
            # Are completely different, are not same
            return False

        try:
            if getattr(c1.fact, c1.slot_type + "_type") != getattr(c2.fact, c2.slot_type + "_type"):
                return False
        except AttributeError:
            pass

        # They are apparently same, check cases
        c1_case = "no-case"
        c2_case = "no-case"
        try:
            c1_case = c1.attributes.get("case", "")
        except AttributeError:
            pass
        try:
            c2_case = c2.attributes.get("case", "")
        except AttributeError:
            pass

        # False if different cases or one had attributes and other didn't
        return c1_case == c2_case

    def _aggregate(self, registry, language, this):
        log.debug("Visiting {}".format(this))

        # Check the relation attribute and call the appropriate aggregator.
        try:
            relation = this.relation
        # If the node doesn't have a relation attribute, it is a message and should be simply returned
        except AttributeError:
            return this

        if relation == Relation.ELABORATION:
            return self._aggregate_elaboration(registry, language, this)

        return self._aggregate_sequence(registry, language, this)

    def _message_positive(self, message):
        fact = message.template.slots[0].fact
        try:
            return ("_rank_reverse" not in fact.what_type) and fact.what >= 0
        # This will happen, if the fact is non-numeric
        except TypeError:
            return True
