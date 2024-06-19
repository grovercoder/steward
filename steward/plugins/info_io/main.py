import os
import requests

from steward.plugins._base_plugin import BasePlugin
from steward.decorators import STEWARD_DIR, is_event_handler
from steward.event import StewardEvent, EventType

class PluginInfoIO(BasePlugin):
    def __init__(self, logger=None, client=None):
        super().__init__()
        self.name = "DataIO"   
        self.logger = logger
        self.mqtt_client = client
        self.datadir = f"{STEWARD_DIR}/{self.name.lower()}"


    @is_event_handler("FILE_READ_CONTENTS")
    def on_file_read_contents(self, event: StewardEvent, message = None):
        """
        Read the contents of a text file specified in the event.payload['path'] field.

        Params:
        event   - A StewardEvent object containing the event data.
        message - The message associated with the event.

        Result:
        An MQTT message is sent containing a StewardEvent response object with the file contents stored in the event.payload property.
        The message is delivered to the MQTT topic defined in the original message.
        If an error occurs, a StewardEvent error object is sent instead.
        """
        if event.is_command:
            file_path = event.payload['path']
            
            # ensure the user has permission to read the file
            if not os.access(file_path, os.R_OK):
                self.logger.error(f"Permission denied: Cannot read file: {file_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="Permission denied")
                self.send_response_event(message, response)
                return
                        
            try:
                with open(file_path, "r") as f:
                    contents = f.read()
                response = StewardEvent(EventType.RESPONSE, event.name, payload=contents)
            except FileNotFoundError:
                self.logger.error(f"File not found: {file_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="File not found")
            except PermissionError:
                self.logger.error(f"Permission denied: Cannot read file: {file_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="Permission denied")
            except Exception as e:
                self.logger.error(f"An error occurred while reading the file: {file_path} - {e}")
                response = StewardEvent(EventType.ERROR, event.name, payload="An error occurred")

            self.send_response_event(message, response)
    
    @is_event_handler("FILE_WRITE_CONTENTS")
    def on_file_write_contents(self, event: StewardEvent, message = None):
        """
        Write text to a filespecified in the event.payload['path'] field.
        Text content is passed via the event.payload['contents'] field.

        Params:
        event   - A StewardEvent object containing the event data.
        message - The message associated with the event.

        Result:
        An MQTT message is sent containing a StewardEvent response object indicating file has been written
        The message is delivered to the MQTT topic defined in the original message.
        If an error occurs, a StewardEvent error object is sent instead.
        """
        if event.is_command:
            file_path = event.payload['path']
            contents = event.payload['contents']
            
            # ensure the user has permission to write the file
            if not os.access(file_path, os.W_OK):
                self.logger.error(f"Permission denied: Cannot write file: {file_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="Permission denied")
                self.send_response_event(message, response)
                return
                        
            try:
                with open(file_path, "w") as f:
                    f.write(contents)
                response = StewardEvent(EventType.RESPONSE, event.name, payload="File written")
            except FileNotFoundError:
                self.logger.error(f"File not found: {file_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="File not found")
            except PermissionError:
                self.logger.error(f"Permission denied: Cannot write file: {file_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="Permission denied")
            except Exception as e:
                self.logger.error(f"An error occurred while writing the file: {file_path} - {e}")
                response = StewardEvent(EventType.ERROR, event.name, payload="An error occurred")

            self.send_response_event(message, response)
    
    @is_event_handler("FILE_MOVE_FILE")
    def on_file_move_file(self, event: StewardEvent, message = None):
        """
        Move a file from one location to another.

        Params:
        event   - A StewardEvent object containing the event data.
        message - The message associated with the event.

        Result:
        An MQTT message is sent containing a StewardEvent response object indicating file has been moved.
        The message is delivered to the MQTT topic defined in the original message.
        If an error occurs, a StewardEvent error object is sent instead.
        """
        if event.is_command:
            file_path = event.payload['path']
            new_path = event.payload['new_path']
            
            # ensure the user can read the source file, and write the destination file
            if not os.access(file_path, os.R_OK):
                self.logger.error(f"Permission denied: Cannot read file: {file_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="Permission denied")
                self.send_response_event(message, response)
                return
            
            if not os.access(new_path, os.W_OK):
                self.logger.error(f"Permission denied: Cannot write file: {file_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="Permission denied")
                self.send_response_event(message, response)
                return
            
            try:
                os.rename(file_path, new_path)
                response = StewardEvent(EventType.RESPONSE, event.name, payload="File moved")
            except FileNotFoundError:
                self.logger.error(f"File not found: {file_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="File not found")
            except PermissionError:
                self.logger.error(f"Permission denied: Cannot write file: {file_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="Permission denied")
            except Exception as e:
                self.logger.error(f"An error occurred while moving the file: {file_path} - {e}")
                response = StewardEvent(EventType.ERROR, event.name, payload="An error occurred")

            self.send_response_event(message, response)

    @is_event_handler("FILE_CREATE_DIRECTORY")
    def on_file_create_directory(self, event: StewardEvent, message = None):
        """
        Create a directory specified in the event.payload['path'] field.

        Params:
        event   - A StewardEvent object containing the event data.
        message - The message associated with the event.

        Result:
        An MQTT message is sent containing a StewardEvent response object indicating directory has been created.
        The message is delivered to the MQTT topic defined in the original message.
        If an error occurs, a StewardEvent error object is sent instead.
        """
        if event.is_command:
            directory_path = event.payload['path']
            
            # ensure the user can write the directory
            if not os.access(directory_path, os.W_OK):
                self.logger.error(f"Permission denied: Cannot write directory: {directory_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="Permission denied")
                self.send_response_event(message, response)
                return
            
            try:
                os.mkdir(directory_path)
                response = StewardEvent(EventType.RESPONSE, event.name, payload="Directory created")
            except FileExistsError:
                self.logger.error(f"Directory already exists: {directory_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="Directory already exists")
            except PermissionError:
                self.logger.error(f"Permission denied: Cannot write directory: {directory_path}")
                response = StewardEvent(EventType.ERROR, event.name, payload="Permission denied")
            except Exception as e:
                self.logger.error(f"An error occurred while creating the directory: {directory_path} - {e}")
                response = StewardEvent(EventType.ERROR, event.name, payload="An error occurred")

            self.send_response_event(message, response)

    @is_event_handler("URL_GET_CONTENTS")
    def on_url_get_contents(self, event: StewardEvent, message = None):
        """
        Read the raw text contents of a URL specified in the event.payload['url'] field.

        Params:
        event   - A StewardEvent object containing the event data.
        message - The message associated with the event.

        Result:
        An MQTT message is sent containing a StewardEvent response object with the URL contents stored in the event.payload property.
        The message is delivered to the MQTT topic defined in the original message.
        If an error occurs, a StewardEvent error object is sent instead.
        """
        if event.is_command:
            try:
                url = event.payload['url']
                content = requests.get(url).text
                        
                response = StewardEvent(EventType.RESPONSE, event.name, payload=content)
            except Exception as e:
                self.logger.error(f"An error occurred while reading the URL: {url} - {e}")
                response = StewardEvent(EventType.ERROR, event.name, payload="An error occurred")

            self.send_response_event(message, response)

    @is_event_handler("URL_GET_JSON")
    def on_url_get_json(self, event: StewardEvent, message = None):
        """
        Read the JSON contents of a URL specified in the event.payload['url'] field.

        Params:
        event   - A StewardEvent object containing the event data.
        message - The message associated with the event.

        Result:
        An MQTT message is sent containing a StewardEvent response object with the URL JSON contents stored in the event.payload property.
        The message is delivered to the MQTT topic defined in the original message.
        If an error occurs, a StewardEvent error object is sent instead.
        """
        if event.is_command:
            try:
                url = event.payload['url']
                content = requests.get(url).json()
                        
                response = StewardEvent(EventType.RESPONSE, event.name, payload=content)
            except Exception as e:
                self.logger.error(f"An error occurred while reading the URL: {url} - {e}")
                response = StewardEvent(EventType.ERROR, event.name, payload="An error occurred")

            self.send_response_event(message, response)
        