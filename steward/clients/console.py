from steward.clients.base_client import BaseClient
from steward.logger import COLORS

class ConsoleClient(BaseClient):
    def __init__(self, *args, **kwargs):
        # Extract specific parameters if needed
        # self.other_param = kwargs.pop('other_param', None)

        super().__init__(*args, **kwargs)

        self.intro = "I am your steward. How can I help?\n"
        self.prompt = f"{COLORS['GREEN']}Steward: {COLORS['DEFAULT']}"

    def _handle_message(self, message):
        self.logger.info(f'MSG: {message}')