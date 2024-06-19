from datetime import datetime
from steward.plugins._base_plugin import BasePlugin
from steward.decorators import STEWARD_DIR, is_event_handler
from steward.event import StewardEvent, EventType

class PluginTime(BasePlugin):
    def __init__(self, logger=None, client=None):
        super().__init__()
        self.name = "Time"   
        self.logger = logger
        self.mqtt_client = client
        self.datadir = f"{STEWARD_DIR}/{self.name.lower()}"


    @is_event_handler(event="GET_TIME")
    def getTime(self, event, message=None):
        if event and event.is_command and message:
            now = datetime.now()
            locale_aware_time = now.strftime('%c')

            resp = StewardEvent(event_type=EventType.RESPONSE, name=event.name, payload=locale_aware_time)
            self.send_response_event(message, resp)
            
    @is_event_handler(event="GET_TIMESTAMP")
    def getTimestamp(self, event, message=None):
        if event and event.is_command and message:
            timestamp = int(datetime.today().timestamp() * 1000)

            resp = StewardEvent(event_type=EventType.RESPONSE, name=event.name, payload=timestamp)
            self.send_response_event(message, resp)