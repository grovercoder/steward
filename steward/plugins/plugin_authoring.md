# Plugin Authoring

## Easy Way:

Copy an existing plugin directory, rename the copy as needed, and then edit the `main.py` file to meet your needs.  If you take this route, I suggest using the "time" plugin as it is relatively simple and light on code.


## The "raw" way:
Creating a new plugin consists of a few simple steps:

1. Create a new directory in the `plugins` directory, named for the "new_plugin" (or something suitable for your plugin).
1. Ensure a `__init__.py` file exists in that "new_plugin" directory.  Create it if needed, an empty file will do.
1. Create a `main.py` file in the "new_plugin" directory.
1. Ensure the `main.py` file contains a minimum of the following code:

    ```python
    from steward.plugins._base_plugin import BasePlugin
    from steward.decorators import STEWARD_DIR, is_event_handler
    from steward.event import StewardEvent, EventType

    class PluginName(BasePlugin):
        def __init__(self, logger=None, client=None):
            super().__init__()
            self.name = "Time"   
            self.logger = logger
            self.mqtt_client = client
            self.datadir = f"{STEWARD_DIR}/{self.name.lower()}"

    ```

    Be sure to change the `PluginName` class name and the `self.name` values to something relevant for your plugin.

1. Extend this file as needed to provide the desired functionality for your plugin.  Feel free to import other modules, add new class methods, or add additional resource files in the plugin directory.

If another plugin provides some of the functionality you need, you can trigger an event if desired and listen for the particular response.  You should avoid creating instances of other plugins directly within your plugin - doing so causes tight coupling (or a "relies on" situation) and makes it harder to update/maintain the plugins.

## Handling Events

You can add a new event handler to your plugin by creating a new method in the `PluginName` class.  That method should have the following signature:

```python
@is_event_handler(event="EVENT_NAME")
def on_event_name(self, event, message=None):
```

- The `event` parameter is the StewardEvent object that was received from the client.
- The `message` parameter is the message that was received from the client.  There are edge cases where the message may not be specified.

The `@is_event_handler` decorator marks the event as an event handler for the specified event name.  The Steward system looks for these indicators when registering plugins.  Essentially, we are saying "this plugin wants to listen for this event type", and when we see it run this method.

## File Management

If your plugin needs to store any files or resources for later use, these should be stored in the `self.datadir` directory.  By default this equates to `/home/USERNAME/.steward/plugin_name`.  This folder should be created by the plugin's `__init__` method if/when needed.

Each plugin can choose how to structure information within that plugin data directory.  Steward only suggests this is where plugin specific info/resources/files should be located.
