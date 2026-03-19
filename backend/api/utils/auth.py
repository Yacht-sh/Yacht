from ..settings import Settings
from ..db.database import SessionLocal

settings = Settings()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
