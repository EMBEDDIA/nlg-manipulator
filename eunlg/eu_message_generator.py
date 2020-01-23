import logging

from core.message_generator import MessageGenerator, NoMessagesForSelectionException

log = logging.getLogger("root")


class EUMessageGenerator(MessageGenerator):
    """
    An NLGPipelineComponent that creates messages from StatFi crime statistics data.
    """

    def __init__(self, expand=True):
        super(EUMessageGenerator, self).__init__()

    def run(
        self, registry, random, language, where, where_type, data, when1=None, when2=None, when_type=None,
    ):
        """
        Run this pipeline component.
        """
        messages = []
        log.info("Generating messages from EU data")
        datastore = registry.get("eu-data")
        ignored_cols = []
        messages.extend(
            (
                super().run(
                    registry,
                    random,
                    language,
                    datastore,
                    where,
                    where_type,
                    data,
                    when1,
                    when2,
                    when_type,
                    ignored_cols=ignored_cols,
                )
            )[0]
        )

        if not messages:
            raise NoMessagesForSelectionException()

        # for message in messages:
        #     log.info(message.fact)

        return (messages,)
