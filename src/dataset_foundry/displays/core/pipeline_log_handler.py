import logging
from logging import Formatter, Filter, Handler, LogRecord

from ...core.pipeline_service import pipeline_service
from ...core.execution_context import current_item_id
from .console_service import console_service


class PipelineLogHandler(Handler):
    """
    Logging handler that routes records with an item ID to the PipelineService, and those without
    to the ConsoleService so they can be rendered in a display.
    """

    def emit(self, record: LogRecord):
        try:
            item_id = getattr(record, "item_id", None)
            message = self.format(record)
            emitted = False

            if item_id:
                try:
                    pipeline_service.append_to_item_property(item_id, "logs", message)
                    emitted = True
                except Exception:
                    # If there's an error appending to the item logs, just log to the console
                    pass

            if not emitted:
                console_service.append(message)

        except Exception:
            self.handleError(record)


class ItemContextFilter(Filter):
    """
    Logging filter that injects `item_id` into records from a contextvar when
    the record doesn't already have an `item_id` attribute.
    """

    def filter(self, record: LogRecord) -> bool:
        if not hasattr(record, "item_id"):
            try:
                record.item_id = current_item_id.get()
            except LookupError:
                # No current item; leave attribute unset
                pass
        return True


def install_pipeline_log_handler(log_level: str):
    handler = PipelineLogHandler()
    handler.setFormatter(Formatter('%(levelname)s: %(message)s'))
    # Ensure item_id is injected at the handler level so all records passing
    # through this handler get the correct item context, regardless of logger config
    handler.addFilter(ItemContextFilter())

    root = logging.getLogger()
    root.handlers = [handler]
    # Don't add a root filter that could interfere with other handlers
    root.setLevel(log_level)
