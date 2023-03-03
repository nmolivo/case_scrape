import os

from criminal_scrape_lambda.db.db_config import DBConfig
from criminal_scrape_lambda.db.models import Base


def init_db():
    engine = DBConfig(
        password=os.getenv("DB_PASSWORD"),
        user=os.getenv("DB_USER"),
        database=os.getenv("DB_DATABASE"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        scheme=os.getenv("DB_SCHEME"),
    ).get_engine()

    Base.metadata.create_all(bind=engine)

    print("Initialized the db")


if __name__ == "__main__":
    init_db()
