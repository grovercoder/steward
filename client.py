
from steward.clients.client import StewardClient
from steward.logger import root_logger

root_logger().info("Starting Steward Client")
client=StewardClient(level="DEBUG")
client.connect()


# from steward.plugins.inspiration_quotes import PluginInspirationQuotes

# quotes = PluginInspirationQuotes()
# print(quotes.load_quotes())

