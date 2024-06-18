import os

STEWARD_DIR=f"{os.path.expanduser('~')}/.steward"

#Decorator
def is_event_handler(event):
    def decorator(func):
        func.handles_event = event
        return func
    return decorator

