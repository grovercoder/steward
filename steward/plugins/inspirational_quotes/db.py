# project_dir/db.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True)
    quote = Column(String)
    author = Column(String)
    created_at = Column(Integer)

class DB:
    def __init__(self, dbpath=None):
        self.dbpath = dbpath
        self.engine = None

        self.setup_db()

    def setup_db(self):
        if not self.dbpath:
            raise ValueError("No database path provided")
        
        print(f"dbpath: {self.dbpath}")
        self.engine = create_engine(f"sqlite:///{self.dbpath}")

        Base.metadata.create_all(self.engine, checkfirst=True)

    def get_session(self):
        if self.engine:
            Session = sessionmaker(bind=self.engine)
            return Session()
    
        return None
    
    def get_todays_quotes(self):
        session = self.get_session()
        sod = datetime.combine(datetime.today(), datetime.min.time())
        start_of_day = int(sod.timestamp() * 1000)
        data = session.query(Quote).filter(Quote.created_at >= start_of_day).all()
        return data

    def add_quote(self, quote, author):
        session = self.get_session()
        current_timestamp = int(datetime.today().timestamp() * 1000)
        q = Quote(quote=quote, author=author, created_at=current_timestamp)
        session.add(q)
        session.commit()


# from . import DB_URL

# # Create the SQLAlchemy engine
# engine = create_engine(DB_URL)

# # Create a configured "Session" class
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Create a Base class for our models to inherit from
# Base = declarative_base()

# # Initialize the database (optional, if you want to automate table creation)
# def init_db():
#     from .models import Quote  # Import all models here to ensure they are registered with SQLAlchemy from
#     Base.metadata.create_all(bind=engine)




# # Replace this with your actual database URL
# DB_URL = f"{os.path.join(PLUGIN_DIR, 'quotes.db')}"

# os.makedirs(PLUGIN_DIR, exist_ok=True)

# def set_db_path(path):
#     global DB_URL
#     DB_URL = path

# def init_db():
#     Base.metadata.create_all(engine)
