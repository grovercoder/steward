from steward.server import StewardServer
from steward.logger import root_logger

root_logger().info("Starting Steward Server")
srv = StewardServer(level="DEBUG")
srv.connect()
