import os
from case_scrape.models import Base
from case_scrape.db.db_config import DBConfig


def init_db():

    engine = DBConfig(
        password=os.getenv("DB_PASSWORD"),
        user=os.getenv("DB_USER")
    ).get_engine()

    Base.metadata.create_all(bind=engine)

    print("Initialized the db")


if __name__ == "__main__":
    init_db()
