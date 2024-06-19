
from steward.plugins._base_plugin import BasePlugin
from steward.decorators import STEWARD_DIR, is_event_handler
from steward.event import StewardEvent, EventType

class PluginInfoIO(BasePlugin):
    def __init__(self, logger=None, client=None):
        super().__init__()
        self.name = "StewardServer"   
        self.logger = logger
        self.mqtt_client = client
        self.datadir = f"{STEWARD_DIR}/{self.name.lower()}"

        self._active_connections = {}

    @is_event_handler(event="CLIENT_REGISTER")
    def register_client(self, event, message=None):
        """
        Register a client.  
        Adds the client details to the internal _active_connections dictionary.
        Client details normally include a client_id, and a client_type value, but may include other information.
        
        Params:
            event (StewardEvent): The event that triggered this function.
            message: The mqtt message that triggered this function.

        Returns:
            None
        """
        data = event.payload
        client_id = event.payload['id']
        if not client_id in self._active_connections:
            self._active_connections[client_id] = data

    @is_event_handler("CLIENT_STOP")
    def unregister_client(self, event, message=None):
        """
        Un-registers a client.
        Removes the client details from the internal _active_connections dictionary.
        
        Params:
            event (StewardEvent): The event that triggered this function.
            message: The mqtt message that triggered this function.

        Returns:
            None
        """
        client_id = message.topic.split("/")[1]
        if client_id in self._active_connections:
            self.logger.debug(f"Unregistering client: {client_id}")
            del self._active_connections[client_id]

    @is_event_handler("LIST_CLIENTS")
    def command_list_clients(self, event, message=None):
        """
        Retrieves the current list of active clients.

        Params:
            event (StewardEvent): The event that triggered this function.
            message: The mqtt message that triggered this function.

        Returns:
            StewardEvent response containing the list of active clients as the payload property.
        """
        if event.is_command:
            data = list(self._active_connections.items())
            response = StewardEvent(EventType.RESPONSE, event.name, payload=data)
            self.send_response_event(message, response)