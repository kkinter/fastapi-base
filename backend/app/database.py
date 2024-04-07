from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import Settings

engine = create_engine(Settings().DATABASE_URL)

# Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    with Session(engine) as session:
        yield session
