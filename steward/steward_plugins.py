import os
import sys
import importlib.util
import inspect

PLUGINS_DIR = os.path.join(os.path.dirname(__file__), "plugins")

class StewardPlugins:
    def __init__(self, logger=None, client=None, base_file='main.py'):
        self.plugins = {}
        self.base_file = base_file
        self.logger = logger
        self.client = client

    def scan(self):
        for item in os.listdir(PLUGINS_DIR):
            # skip items that begin with an underscore
            if item.startswith("_"):
                continue

            current_path = os.path.join(PLUGINS_DIR, item)
            if os.path.isdir(current_path):
                print(f"Loading plugin: {item} : {current_path}")
                self.load_plugin(current_path, item)
                
    def load_plugin(self, candidate_dir, plugin_name):
        # Add the plugin directory to sys.path
        sys.path.insert(0, candidate_dir)

        # load classes from candidate directory
        entry_file = os.path.join(candidate_dir, self.base_file)
        if os.path.isfile(entry_file):

            print(f"Loading plugin: {plugin_name} : {entry_file}")
            spec = importlib.util.spec_from_file_location(plugin_name, entry_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find the class defined in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Ensure the class is defined in the current module
                if obj.__module__ == plugin_name:
                    # Instantiate the class and append to the plugins list
                    inst = obj(logger=self.logger, client=self.client)
                    self.plugins[plugin_name] = inst
                    
                    if self.logger:
                        self.logger.debug(f"PLUGIN: {inst.name}")

                    break  #Assuming there's only one class per file, we can break the loop
        
        # Remove the plugin directory from sys.path to avoid conflicts
        sys.path.pop(0)