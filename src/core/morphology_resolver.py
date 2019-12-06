import logging
from .pipeline import NLGPipelineComponent

to_be_moved = {
'Cipar': 'na Cipru',
'Luksemburg': 'u Luksemburgu',
'Malta': 'na Malti',
'Portugal': 'u Portugalu',
'Velika Britanija': 'u Velikoj Britaniji',
'Island': 'na Islandu',
'Sjeverna Makedonija': 'u sjevernoj Makedoniji',
'Sjedinjene Države': 'u Sjedinjenim Državama',
}

from config import MORPHOLOGIES 

log = logging.getLogger('root')

class MorphologyResolver(NLGPipelineComponent):

    def __init__(self):
        return

    def run(self, registry, random, language, document_plan):
        '''
        Run this pipeline component.
        '''
        if language.endswith('-head'):
            language = language[:-5]
            log.debug('Language had suffix \'-head\', removing. Result: {}'.format(language))
        
        if language in MORPHOLOGIES:
            self._recurse(document_plan)
        return (document_plan, )

    def _recurse(self, this):
        try:
            idx = 0
            while idx < len(this.children):
                slots_added = self._recurse(this.children[idx])
                if slots_added:
                    idx += slots_added
                idx += 1
        except AttributeError as ex:
            try:
                slot_type = this.slot_type
                case = this.attributes.get('case')
            except AttributeError:
                log.info('Got an AttributeError when checking slot_type in realize_slots. Probably not a slot.')
                slot_type = 'n/a'
            if slot_type == 'where':
                if case == 'ine':
                    new_value = self._hr_country_inessive(this.value)
                    this.value = lambda x: new_value
                return 0
            else:
                return 0

    def _hr_country_inessive(self, value):
        
        exceptions = {
            'Cipar': 'na Cipru',
            'Luksemburg': 'u Luksemburgu',
            'Malta': 'na Malti',
            'Portugal': 'u Portugalu',
            'Velika Britanija': 'u Velikoj Britaniji',
            'Island': 'na Islandu',
            'Sjeverna Makedonija': 'u sjevernoj Makedoniji',
            'Sjedinjene Države': 'u Sjedinjenim Državama',
        }

        if value in exceptions:
            return exceptions.get(value)

        if value.endswith('ka'):
            value = 'u {}oj'.format(value[:-1])
        elif value.endswith('a'):
            value = 'u {}i'.format(value[:-1])
        return value
