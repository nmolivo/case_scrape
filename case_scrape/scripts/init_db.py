import os

from case_scrape.db.db_config import DBConfig
from case_scrape.models import Base


def init_db():

    engine = DBConfig(
        password=os.getenv("DB_PASSWORD"),
        user=os.getenv("DB_USER"),
        database="cuyacourts",
        host="cuya-courts.cz4nubeqeyzc.us-east-1.rds.amazonaws.com",
        port=3306,
    ).get_engine()

    Base.metadata.create_all(bind=engine)

    print("Initialized the db")


if __name__ == "__main__":
    init_db()
