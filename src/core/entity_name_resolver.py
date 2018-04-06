from .pipeline import NLGPipelineComponent
from collections import defaultdict

import logging
log = logging.getLogger('root')


class EntityNameResolver(NLGPipelineComponent):
    """
    A NLGPipelineComponent that transforms abstracted entity identifers to names.

    Entity name variants are supplied as the 'ner_table' component in the registry.

    When an entity is first encountered, "full_name" is used. On subsequent uses,
    either "short_name" or "pronoun" is used depending on whether the previously
    encountered entity is the same entity as the one being processed.
    """

    # We want certain entity_types to be "possible confusable" for each other. For example
    # it is possible for a reader to get confused with a pronoun like "they" if the previous
    # sentence discusses both a party and a candidate. At the same time, there are cases where
    # such confusion is not in pratice possible, for example when we refer to "they" in a sentence
    # that has only discussed a single party and some location.
    #
    # Thus, we define a data structure where
    # these "confusion-groups" each map to a key. This allows us to in turn key the previous_entities
    # my by confusion-group, rather than by entity_type.
    #
    # This solution is likely going to turn out to be language-specific. If so, some abstraction is
    # needed or the confusion-groups must be keyed by language as well.
    #
    # In this implementation, it is enough to define the multi-entity_type confusion groups, as we
    # can simply use the default parameter in dict.get() to return the key for other cases-

    # ToDo: These can probably be removed, but left them here for now.
    confusion_groups = {
        'party': 'party-candidate',
        'candidate': 'party-candidate',
    }

    def run(self, registry, random, language, document_plan):
        """
        Run this pipeline component.
        """
        log.info("Running NER")

        if language.endswith("-head"):
            language = language[:-5]
            log.debug("Language had suffix '-head', removing. Result: {}".format(language))

        previous_entities = defaultdict(lambda: None)
        self._recurse(registry, random, language, document_plan, previous_entities, set())

        if log.isEnabledFor(logging.DEBUG):
            document_plan.print_tree()

        return (document_plan, )

    def _recurse(self, registry, random, language, this, previous_entities, encountered):
        """
        Traverses the DocumentPlan tree recursively in-order and modifies named
        entity to_value functions to return the chosen form of that NE's name.
        """

        try:
            # Try to use the current root as a non-leaf.
            children = this.children
            log.debug("Visiting non-leaf '{}'".format(this))
            for child in children:
                encountered, previous_entities = self._recurse(registry, random, language, child, previous_entities, encountered)
        except AttributeError as ex:
            # Had no children, must be a leaf node

            entity = this.value
            
            if not self.is_entity(entity):
                log.debug("Visited leaf non-NE leaf node {}".format(entity))
                return encountered, previous_entities

            log.debug("Visiting NE leaf {}".format(entity))
            entity_type = self.resolve_entity_type(entity)

            confusion_group = self.confusion_groups.get(entity_type, entity_type)
            if previous_entities[confusion_group] == entity:
                log.debug("Same as previous entity")
                name_type = "pronoun"

            elif entity in encountered:
                log.debug("Different entity than previous, but has been previously encountered")
                name_type = "short"

            else:
                log.debug("First time encountering this entity")
                name_type = "full"
                encountered.add(entity)
                log.debug("Added entity to encountered, all encountered: {}".format(encountered))

            surface_form = self.resolve_surface_form(registry, random, language, entity, name_type)
            log.debug("Resolved entity name to {}".format(surface_form))

            this.value = lambda x: surface_form
            this.attributes["entity_type"] = entity_type
            this.attributes["name_type"] = name_type
            # If the entity shouldn't be realized, remove the case marking to prevent Omorfi from getting confused
            if not surface_form:
                this.attributes.pop('case')

            previous_entities[confusion_group] = entity

        return encountered, previous_entities

    def is_entity(self, maybe_entity):
        raise NotImplementedError("Not implemented")

    def resolve(self, registry, random, language, code, name_type):
        raise NotImplementedError("Not implemented")
