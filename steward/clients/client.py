import json
import os
import paho.mqtt.client as mqtt
import signal
import threading

from typing import List
from nanoid import generate
from dotenv import load_dotenv
from steward.event import StewardEvent, EventType
from steward.logger import get_logger
from steward.message_agent import MessageAgent
from steward.decorators import is_event_handler

load_dotenv()

class StewardClient:
    def __init__(self, level="INFO"):
        self.id = generate(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",size=12)
        self.logger = get_logger(name=self.id, level=level, console=True, file="logs/client.log")
        self.msgagent = MessageAgent(logger=self.logger)

        self._active_connections = List[mqtt.Client]
        self.client_type = "general"
        self.client_topic = f"steward/{self.id}"

        self.client = mqtt.Client(client_id=self.id)
        self.mqtt_host = os.getenv('STEWARD_MQTT_HOST', 'localhost') 
        self.mqtt_port = int(os.getenv('STEWARD_MQTT_PORT', 1883))
        self.mqtt_ws_port = int(os.getenv('STEWARD_MQTT_WS_PORT', 51234))

        self.msgagent.find_event_handlers(self)
        signal.signal(signal.SIGINT, self.handle_disconnect)
        signal.signal(signal.SIGTERM, self.handle_disconnect)

    def connect(self):
        self.logger.debug(f"Connecting to MQTT broker: {self.mqtt_host}:{self.mqtt_port}")
        
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.msgagent.message_processor

        self.client.enable_logger()
        self.client.connect(self.mqtt_host, self.mqtt_port, 60)        

        try:
            self.client.loop_forever()

        except Exception as e:
            self.logger.error(f"Error: {e}")
                         
    def disconnect(self):
        self.logger.info("Shutting down")
        stop_event = StewardEvent(EventType.NOTICE, "CLIENT_STOP", payload={"id": self.id})
        self.client.publish(self.client_topic, stop_event.toJSON())
        self.client.disconnect()
        self.client.loop_stop()


    def handle_disconnect(self, SIGNAL, FRAME):    
        self.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        self.logger.debug("Connected with result code "+str(rc))
        client.subscribe("steward/#")

        self.client_register(None, self.client_topic)
        
        threading.Timer(2, self.run_test).start()
        
    def on_close(self, client, userdata, rc):
        event = StewardEvent(EventType.NOTICE, "CLIENT_DISCONNECT", payload={"id": self.id})
        self.client.publish(self.client_topic, event.toJSON())
        self.logger.debug(f"Client disconnected with result code {rc}")

    def request_clients(self):
        start_event = StewardEvent(EventType.COMMAND, "LIST_CLIENTS") 
        self.client.publish(self.client_topic, start_event.toJSON())

    def request_time(self):
        event = StewardEvent(EventType.COMMAND, "GET_TIME")
        self.client.publish(self.client_topic, event.toJSON())

    def run_test(self):
        
        event = StewardEvent(EventType.COMMAND, "INSPIRATIONAL_QUOTE")
        self.client.publish(self.client_topic, event.toJSON())
        
    @is_event_handler("FILE_READ_CONTENTS")
    def read_file(self, event, message=None):
        if event.is_response:
            self.logger.debug(f"File contents: {event.payload}")

    @is_event_handler("URL_GET_CONTENTS")
    def get_url_contents(self, event, message=None):
        if event.is_response:
            self.logger.debug(f"URL contents: {event.payload}")

    @is_event_handler("SERVER_START")
    def client_register(self, event, message):
        data = {
            "id": self.id,
            "type": self.client_type
        }

        start_event = StewardEvent(EventType.NOTICE, "CLIENT_REGISTER", payload=data)
        self.client.publish("steward/broadcast", start_event.toJSON())
    
    @is_event_handler("SERVER_STOP")
    def server_stop_response(self, event, message):
        self.disconnect()

    @is_event_handler("LIST_CLIENTS")
    def show_clients(self, event, message):
        if event.is_response:
            data = {item[0]: item[1] for item in event.payload}

            self.logger.debug(f"Current Clients")
            for client_id,client in data.items():
                self.logger.debug(f"  [{client['type']}] {client['id']}")
    

    @is_event_handler("TIME")
    def show_time(self, event, message):
        if event.is_response:
            self.logger.debug(f"Current Time: {event.payload}") 

    @is_event_handler("URL_GET_JSON")
    def get_url_json(self, event, message=None):
        if event.is_response:
            for item in event.payload:
                print(item['q'])
                print(f"  - {item['a']}")
            # self.logger.debug(f"JSON contents: {event.payload}")

    @is_event_handler("INSPIRATIONAL_QUOTE")
    def get_quote(self, event, message=None):
        if event.is_response:
            self.logger.info(f"Quote: {event.payload['q']}")
            self.logger.info(f"    - {event.payload['a']}")
            
        return event.payload