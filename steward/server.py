import paho.mqtt.client as mqtt
import os
import signal
from typing import List
from nanoid import generate
from dotenv import load_dotenv
import importlib.util
import inspect

from steward.event import StewardEvent, EventType
from steward.logger import get_logger
from steward.message_agent import MessageAgent
from steward.decorators import is_event_handler
from steward.steward_plugins import StewardPlugins

load_dotenv()

class StewardServer:
    def __init__(self, level="INFO"):
        self.id = f'STEWARD-{generate(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",size=12)}'
        self.logger = get_logger(name="steward", level=level, console=True, file="logs/steward.log")
        self.msgagent = MessageAgent(logger=self.logger)
        # self._active_connections = {}
        
        self.client = mqtt.Client(client_id=self.id)
        self.mqtt_host = os.getenv('STEWARD_MQTT_HOST', 'localhost') 
        self.mqtt_port = int(os.getenv('STEWARD_MQTT_PORT', 1883))
        self.mqtt_ws_port = int(os.getenv('STEWARD_MQTT_WS_PORT', 51234))

        self.msgagent.find_event_handlers(self)
        signal.signal(signal.SIGINT, self._handle_disconnect)
        signal.signal(signal.SIGTERM, self._handle_disconnect)

        self.plugin_manager = StewardPlugins(logger=self.logger, client=self.client)
        self.plugin_manager.scan()

        # register any event handler methods
        for pname, p in list(self.plugin_manager.plugins.items()):
            
            print(f"Registering event handlers for {p}")
            self.msgagent.find_event_handlers(p)

    def connect(self):
        self.logger.debug(f"Connecting to MQTT broker: {self.mqtt_host}:{self.mqtt_port}")
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.msgagent.message_processor
        self.client.on_disconnect = self.on_disconnect
        self.client.on_error = self.on_error
        self.client.on_close = self.on_close

        self.client.enable_logger()
        self.client.connect(self.mqtt_host, self.mqtt_port, 60)
        
        try:
            self.client.loop_forever()

        except KeyboardInterrupt:
            self.disconnect()

    def disconnect(self):
        self.logger.warn("Shutting down")
        self.logger.debug("Notifying clients of server shutdown")
        stop_event = StewardEvent(EventType.NOTICE, "SERVER_STOP")
        self.client.publish("steward/broadcast", stop_event.toJSON())
        self.client.disconnect()
        self.client.loop_stop()

    def _handle_disconnect(self, SIGNAL, FRAME):    
        self.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        self.logger.debug("Connected with result code "+str(rc))
        client.subscribe("steward/#")

        start_event = StewardEvent(EventType.NOTICE, "SERVER_START")
        client.publish("steward/broadcast", start_event.toJSON())

    def on_disconnect(self, client, userdata, rc):
        self.logger.debug("Disconnected with result code "+str(rc))


    def on_error(self, client, userdata, exc):
        self.logger.debug("Error: "+str(exc))

    def on_close(self, client, userdata, rc):
        self.logger.debug("Connection closed with result code "+str(rc))


    
        
    