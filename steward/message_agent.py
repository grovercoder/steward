from functools import wraps
from steward.event import StewardEvent
from steward.logger import get_logger



class MessageAgent:

    def __init__(self, logger=None):
        self.logger = logger
        self.handlers = {}
        self.event_log = get_logger(name="event", level="DEBUG", console=False, file="logs/event.log")

    def add_handler(self, event_name, handler_func):
        self.logger.warn(f"Adding handler for {event_name} : {handler_func}")
        if event_name in self.handlers:
            self.handlers[event_name].append(handler_func)
        else:
            self.handlers[event_name] = [handler_func]

    def find_event_handlers(self, target):
        for attr_name in dir(target):
            attr = getattr(target, attr_name)
            if callable(attr) and hasattr(attr, 'handles_event'):
                event = attr.handles_event
                if event:
                    self.add_handler(event, attr)

    def message_processor(self, client, userdata, message):
        if self.logger:
            self.logger.warn(f"MSG: [{message.topic} {str(message.payload)}")
        
        event = StewardEvent.fromJSON(message.payload.decode())
        if event.name in self.handlers:
            for handler in list(self.handlers[event.name]):
                handler(event, message)

