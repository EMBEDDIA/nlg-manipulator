import logging

from core import MessageGenerator, NoMessagesForSelectionException

log = logging.getLogger('root')

class CrimeMessageGenerator(MessageGenerator):
    """
    An NLGPipelineComponent that creates messages from StatFi crime statistics data.
    """
    def __init__(self, expand=True):
        super(CrimeMessageGenerator, self).__init__()

    def run(self, registry, random, language, where, where_type, when1=None, when2=None, when_type="year"):
        """
        Run this pipeline component.
        """
        log.info("Generating messages from crime data")
        datastore = registry.get('crime-data')
        messages = (super().run(registry, random, language, datastore, where, where_type, when1, when2, when_type))[0]

        if not messages:
            raise NoMessagesForSelectionException()

        return (messages, )
