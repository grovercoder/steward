from steward.decorators import is_event_handler
from steward.event import StewardEvent, EventType
import os

class BasePlugin:
    def __init__(self):
        self.name = None
        self.logger = None
        self.mqtt_client = None

    def set_logger(self, logger):
        self.logger = logger
    
    def set_mqtt_client(self, client):
        self.mqtt_client = client  
    
    def send_response_event(self, message, event):
        self.mqtt_client.publish(message.topic, event.toJSON())