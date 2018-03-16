import re
from core import EntityNameResolver

class MunicipalElectionEntityNameResolver(EntityNameResolver):

    def __init__(self):
        # [ENTITY:<group1>:<group2>] where group1 and group2 can contain anything but square brackets or double colon
        self._matcher = re.compile("\[ENTITY:([^\]:]*):([^\]]*)\]")

    def is_entity(self, maybe_entity):
        # Match and convert the result to boolean
        try:
            return self._matcher.fullmatch(maybe_entity) is not None
        except TypeError:
            print("EntityNameResolver got a number: {:n} instead of a string".format(maybe_entity))

    def _parse_code(self, code):
        match = self._matcher.fullmatch(code)
        if not match:
            raise ValueError("Who value {} does not match entity regex".format(code))
        if not len(match.groups()) == 2:
            raise Exception("Invalid number of matched groups?!")
        return match.groups()

    def resolve_entity_type(self, code):
        return self._parse_code(code)[0]

    def resolve_surface_form(self, registry, random, language, code, name_type):
        entity_type, entity = self._parse_code(code)
        if entity_type == "party":
            return self.resolve_party(registry, random, language, entity, name_type)
        elif entity_type == "candidate":
            return self.resolve_candidate(registry, random, language, entity, name_type)
        elif entity_type in ["C", "D", "M", "P"]:
            return self.resolve_location(registry, random, language, entity, entity_type, name_type)

        raise ValueError("Unknown entity: {}".format(code))

    def resolve_party(self, registry, random, language, entity, name_type):
        # Try getting surface form in this order:
        # 1. The relevant entity's surface form in the relevant language
        # 2. A geneneral surface form in the relevant language
        # 3. The relevant entity's surface form in Finnish
        # 4. A general surface form in Finnish (guaranteed to be present)
        party_data = registry.get('parties')
        options = party_data.get(language, {}).get(entity, {}).get(name_type, None)
        if not options:
            options = party_data.get(language, {}).get(None, {}).get(name_type, None)
        if not options:
            options = party_data["fi"].get(entity, {}).get(name_type, None)
        if not options:
            options = party_data["fi"].get(None, {}).get(name_type, "NOT-A-CLUE")
        # Randomly pick one from the list and return that
        return random.choice(options)

    def resolve_candidate(self, registry, random, language, entity, name_type):
        # Try getting surface form in this order:
        # 1. The relevant entity's surface form in the relevant language
        # 2. A geneneral surface form in the relevant language
        # 3. The relevant entity's surface form in Finnish
        # 4. A general surface form in Finnish (guaranteed to be present)
        candidate_data = registry.get('candidates')
        surface_form = candidate_data.get(language, {}).get(entity, {}).get(name_type, None)
        if not surface_form:
            surface_form = candidate_data.get(language, {}).get(None, {}).get(name_type, None)
        if not surface_form:
            surface_form = candidate_data["fi"].get(entity, {}).get(name_type, None)
        if not surface_form:
            surface_form = candidate_data["fi"].get(None, {}).get(name_type, "NOT-A-CLUE")
        return surface_form

    def resolve_location(self, registry, random, language, entity, entity_type, name_type):
        geodata = registry.get('geodata-lookup')
        
        #if name_type == "pronoun":
        #    return ""

        surface_form = geodata.get(language, {}).get(entity_type, {}).get(entity, None)
        if not surface_form:
            surface_form = geodata.get(language, {}).get(entity_type, {}).get(None, None)
        if not surface_form:
            surface_form = geodata["fi"].get(entity_type, {}).get(entity, None)
        if not surface_form:
            surface_form = geodata["fi"].get(entity_type, {}).get(None, "NOT-A-CLUE")
        return surface_form