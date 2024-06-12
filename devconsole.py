import os
from steward.clients.devconsole import DevConsoleClient
from dotenv import load_dotenv

load_dotenv()
client = DevConsoleClient(id="DEV", socket_host=os.getenv('STEWARD_SOCKET_HOST'), socket_port=os.getenv('STEWARD_SOCKET_PORT'))

client.logger.setLevel('DEBUG')
client.logger.info(f'CLIENT ID: {client.id}')
client.start()
