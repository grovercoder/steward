import os
from steward.clients.console import ConsoleClient
from dotenv import load_dotenv

load_dotenv()
client = ConsoleClient(socket_host=os.getenv('STEWARD_SOCKET_HOST'), socket_port=os.getenv('STEWARD_SOCKET_PORT'))

# client.logger.setLevel('DEBUG')
client.start()
