from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL", pool_pre_pring=True, pool_recycle=300) # Checks if connection is alive before using it and refreshes it every 5 mnt.
if not db_url:
    raise RuntimeError("DATABASE_URL is not set.")

engine = create_engine(db_url)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



