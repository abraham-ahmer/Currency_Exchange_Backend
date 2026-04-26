from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL") 
if not db_url:
    raise RuntimeError("DATABASE_URL is not set.")

engine = create_engine(
    db_url,
    pool_pre_ping=True,   # checks if connection is alive before using it
    pool_recycle=300,     # recycles connections every 5 minutes
    pool_size=5,          # number of persistent connections
    max_overflow=10,      # extra connections allowed beyond pool_size
    pool_timeout=30       # wait time before giving up on a connection
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



