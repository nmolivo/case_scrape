import os
from case_scrape.models import Base
from case_scrape.db.db_config import DBConfig


def init_db():

    engine = DBConfig(
        password=os.getenv("DB_PASSWORD"),
        user=os.getenv("DB_USER"),
        database=os.getenv("DB_DATABASE"),
        scheme=os.getenv("DB_SCHEME"),
        host=os.getenv("DB_HOST"),
        schema=os.getenv("DB_SCHEMA"),
    ).get_engine()

    Base.metadata.create_all(bind=engine)

    db_session.commit()

    print("Initialized the db")


if __name__ == "__main__":
    init_db()
