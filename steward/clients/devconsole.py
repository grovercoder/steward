from steward.clients.base_client import BaseClient
from steward.logger import COLORS
from steward.event import StewardEvent

class DevConsoleClient(BaseClient):
    def __init__(self, *args, **kwargs):
        # Extract specific parameters if needed
        # self.other_param = kwargs.pop('other_param', None)

        super().__init__(*args, **kwargs)

        self.intro = "I am your steward. How can I help?\n"
        self.prompt = f"{COLORS['GREEN']}Steward: {COLORS['DEFAULT']}"
        self.client_type = 'DevConsole'

    def _handle_message(self, message):
        self.logger.debug(f'[CONSOLE] MSG: {message}')
        
        if isinstance(message, StewardEvent):
            if message.name == "STEWARD_STOPPING":
                self.logger.warn("Server has stopped")
                self._stop_signal.set()

            