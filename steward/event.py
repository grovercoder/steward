import time
import json
from nanoid import generate
from enum import Enum, auto


class EventType(Enum):
    UNKNOWN = auto()
    NOTICE = auto()
    COMMAND = auto()
    QUERY = auto()
    RESPONSE = auto()
    ERROR = auto()

class StewardEvent:
    def __init__(self, event_type, name=None, trigger_event=None, payload=None):
        self.id = f"E:{generate(size=10)}"
        self.event_type = event_type
        self.name = name
        self.timestamp = int(time.time() * 1000)
        # ID of event that triggered this event (is this a response event)
        self.triggering_event = trigger_event
        self.payload = payload

    def toJSON(self):
        if self.payload:
            try:
                payload_json = json.dumps(self.payload)
            except Exception as e:
                payload_json = str(e)
        else:
            payload_json = None


        json_obj = json.dumps({
            "id": self.id,
            "event_type": self.event_type.name,
            "name": self.name,
            "timestamp": self.timestamp,
            "triggering_event": self.triggering_event.toJSON() if self.triggering_event else None,
            "payload": payload_json
        })
        
        return json_obj
    
    @property
    def is_notice(self):
        return self.event_type == EventType.NOTICE

    @property
    def is_command(self):
        return self.event_type == EventType.COMMAND
    
    @property
    def is_query(self):
        return self.event_type == EventType.QUERY
    
    @property
    def is_response(self):
        return self.event_type == EventType.RESPONSE

    @property
    def is_error(self):
        return self.event_type == EventType.ERROR  
    
    @staticmethod
    def fromJSON(json_str):
        data = json.loads(json_str)
        event_type = EventType[data["event_type"]]
        trigger_event = StewardEvent.fromJSON(data["triggering_event"]) if data["triggering_event"] else None
        payload = None
        if data["payload"]:
            try:
                payload = json.loads(data["payload"])
            except Exception as e:
                payload = data["payload"]

        return StewardEvent(
            event_type=event_type,
            name=data.get("name"),
            trigger_event=trigger_event,
            payload=payload
        )
