import logging

from core import MessageGenerator, NoMessagesForSelectionException

log = logging.getLogger('root')

class CrimeMessageGenerator(MessageGenerator):
    """
    An NLGPipelineComponent that creates messages from StatFi crime statistics data.
    """
    def __init__(self, expand=True):
        super(CrimeMessageGenerator, self).__init__()

    def run(self, registry, random, language, where, where_type, when1=None, when2=None, when_type=None):
        """
        Run this pipeline component.
        """
        messages = []
        log.info("Generating messages from crime data")
        datastore = registry.get('cphi-data')
        ignored_cols = [c for c in datastore.all().columns.values if 'population' in c]
        messages.extend((super().run(registry, random, language, datastore, where, where_type, when1, when2, when_type, ignored_cols=ignored_cols))[0])

        if not messages:
            raise NoMessagesForSelectionException()

        return (messages, )
