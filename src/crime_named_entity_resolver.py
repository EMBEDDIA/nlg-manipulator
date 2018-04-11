import re
from core import EntityNameResolver


class CrimeEntityNameResolver(EntityNameResolver):

    def __init__(self):
        # [ENTITY:<group1>:<group2>] where group1 and group2 can contain anything but square brackets or double colon
        self._matcher = re.compile("\[(PLACE|TIME):([^\]:]*):([^\]]*)\]")

    def is_entity(self, maybe_entity):
        # Match and convert the result to boolean
        try:
            return self._matcher.fullmatch(maybe_entity) is not None
        except TypeError:
            print("EntityNameResolver got a number: {} instead of a string".format(maybe_entity))

    def _parse_code(self, code):
        match = self._matcher.fullmatch(code)
        if not match:
            raise ValueError("Who value {} does not match entity regex".format(code))
        if not len(match.groups()) == 3:
            raise Exception("Invalid number of matched groups?!")
        return match.groups()

    def resolve_entity_type(self, code):
        return self._parse_code(code)[1]

    def resolve_surface_form(self, registry, random, language, code, name_type):
        _, entity_type, entity = self._parse_code(code)
        if entity_type == 'C' and entity == 'fi':
            return {
                'en':'Finland',
                'fi':'Suomi',
                'sv':'Finland'
            }[language]
        if entity_type in ["C", "D", "M", "P"]:
            if name_type == 'full':
                return entity
            else:
                return ""

        raise ValueError("Unknown entity: {}".format(code))
