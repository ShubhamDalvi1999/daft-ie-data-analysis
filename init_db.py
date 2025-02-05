from sqlalchemy import create_engine
from models import Base
from config import DATABASE_URL
import os

def init_db():
    # Remove existing database file if it exists
    if os.path.exists('daft_properties.db'):
        os.remove('daft_properties.db')
        print("Removed existing database file")
    
    # Create new database and tables
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db() 