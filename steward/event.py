import pickle
import time
from nanoid import generate

class StewardEvent:
    def __init__(self, name=None, payload=None, trigger_event=None):
        self.id = f"E{generate(size=10)}"
        self.name = name
        self.timestamp = int(time.time() * 1000)
        # ID of event that triggered this event (is this a response event)
        self.triggering_event = None
        self.payload = None

    def serialize(self):
        return pickle.dumps(self)
