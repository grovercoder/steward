# Steward

Steward is intended to be a personal digital assistant similar to the "Jarvis" system from the Iron Man movies.  However the system will be personalized to the user, making use of capabilities relevant to the user.

That level of capability is challenging, so I'm starting with the basics.  

## Setup

1. clone the repo
1. create your virtual environment.  Pick your poison here - venv, conda, poetry, etc.  I chose venv.

    ```bash
    cd project_dir
    python3 -m venv .venv
    source .venv/bin/activate
    ```

1. run the pip installs needed.  The current list of requirements is:

    ```text
    certifi==2024.6.2
    charset-normalizer==3.3.2
    greenlet==3.0.3
    idna==3.7
    iniconfig==2.0.0
    nanoid==2.0.0
    packaging==24.0
    paho-mqtt==2.1.0
    pluggy==1.5.0
    psycopg2-binary==2.9.9
    pysqlite3==0.5.3
    pytest==8.2.2
    python-dotenv==1.0.1
    requests==2.32.3
    SQLAlchemy==2.0.30
    typing_extensions==4.12.2
    urllib3==2.2.1
    websockets==12.0
    ```

    Some of these are not needed and this will be cleaned up.


## Running the app

Don't get excited.  It doesn't do much yet. But here is the process:

1. Open a terminal and run the MQTT broker.

```bash
cd project_dir
docker compose up -d
```

1. Open another terminal and run the server:

```bash
cd project_dir
python3 main.py
```

1. Open another terminal and run the client:

```bash
cd project_dir
python3 client.py
```

The client and server utilize logging messages to show progress.  These are also written to the `logs` folder.  A "root" logger is run to capture ALL logging for a more complete picture.  Remember to clear these log files periodically.

The client connects to the server, and you'll see log messages on both the client and server windows indicating this.  The client will request an inspirational quote two seconds after starting.  It might take a moment to get the quote, but this will be displayed in the console window.  The quotes are selected from the `~/.steward/InspirationalQuotes/quotes.db` SQLite database. The query looks for any quotes that were received today, then chooses a random entry.  If there are no quotes for today then quotes are pulled from [zenquotes.io](https://zenquotes.io/) and written to the to the databased.  The client will not hit the database again util the next day (or until the database is cleared). 


## Basic Planning:

1. Server structure.  

    - Mostly done. MQTT seems to be the way.

1. Event Management.  

    - Operational draft.  This may change as the system grows.

1. Plugin System.

    - structure is in place
    - working code needs to be migrated to new structure and cleaned up
    - plugin work will continue and evlove as the system grows

1. Clients

    - development client in place but messy.  Needs to be replaced or cleaned up.
    - a more formal client is needed yet where we do not need to edit code to trigger functionality.
    - specific clients are also needed - web client, REST client, voice client, etc.
    - initial interface will likely be an HTML "start" page with some system monitoring capabilities.

1. Speech System

    - needs to be implemented

1. Core tasks

    - underway
    - The core tasks are the basic steps that are required to accomplish a task.  I.e. the task "analyze the contents of this file" requires a file to be found, opened, read, analyzed, and closed, all with suitable error handling.  Creating a project might need a directory created, one or more files created and populated, and perhaps other steps.  

1. Composite tasks

    - needs to be implemented.  
    - This is where a single task may need to make use of mutliple core tasks through multiple plugins.

1. AI / LLM integration

    - some proof of concept work has been done outside the project.
    - this will likely be introduced as a plugin
    - a "task planning" sub step will be the first focus.  This is having the system figure out what plugin calls need to be made to accomplish its current task.

1. Task development

    - needs to be implemented.
    - this is identifying the common tasks a user may undertake, and ensuring the system has the capabilities of satisfying that task
    - some tasks may require the creation of new plugins.  However the core capabilities should be sufficient to accomplish most tasks.

1. Testing

    - structure created, but will need to be expanded
    - testing needs to be updated to cover current functionality