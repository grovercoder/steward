import os
import random
import requests

from steward.plugins._base_plugin import BasePlugin
from steward.decorators import STEWARD_DIR, is_event_handler
from steward.event import StewardEvent, EventType
from steward.plugins.inspirational_quotes.db import DB

QUOTE_URL = "https://zenquotes.io/api/quotes"

class PluginQuotes(BasePlugin):
    def __init__(self, logger=None, client=None):
        super().__init__()
        self.name = "InspirationalQuotes"   
        self.logger = logger
        self.mqtt_client = client
        self.datadir = f"{STEWARD_DIR}/{self.name}"
        self.dbfile = f"{self.datadir}/quotes.db"
        
        os.makedirs(self.datadir, exist_ok=True)

        self.db = DB(self.dbfile)
      
    
        
    def get_quote(self):
        chosen = {"q": "No quotes today", "a": "system"}
        quotes = self.db.get_todays_quotes()
        
        if quotes:
            choice = random.choice(quotes)
            chosen = {
                "q": choice.quote,
                "a": choice.author
            }
        else:
            quote_json = requests.get(QUOTE_URL).json()
            for item in quote_json:
                self.db.add_quote(item["q"], item["a"])
                quotes = self.db.get_todays_quotes()
                if quotes:
                    choice = random.choice(quotes)
                    chosen = {
                        "q": choice.quote,
                        "a": choice.author
                    }

        return chosen

    @is_event_handler(event="INSPIRATIONAL_QUOTE")
    def on_get_quote(self, event, message=None):
        """
        Get a random quote from the database

        Params:
            event (StewardEvent): The event that triggered this function
            message: The message that triggered this function

        Returns:
            A StewardEvent Response object is returned containing the quote and author
        """
        if event and event.is_command:
            quote = self.get_quote()
            response = StewardEvent(EventType.RESPONSE, event.name, payload=quote)
            self.mqtt_client.publish(message.topic, response.toJSON())

    
