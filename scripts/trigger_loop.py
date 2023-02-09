import os
import requests

from sqlalchemy import func
from criminal_scrape_lambda.db import models
from criminal_scrape_lambda.db.engine import get_db
from criminal_scrape_lambda.db.db_config import get_db_config
from criminal_scrape_lambda.db.models import Base


### make engine
db_config = get_db_config()
engine = db_config.get_engine()

Base.metadata.create_all(bind=engine, checkfirst=True)


def get_last_scraped() -> int:
    db = get_db()
    max_id = db.query(func.max(models.Progress.case_id)).scalar()
    return max_id


case_numbers = (
    [str(x) for x in range(655783, 666532)]
    + [str(x) for x in range(655656, 666532)]
    + [str(x) for x in range(647313, 655655)]
    + [str(x) for x in range(635863, 647312)]
    + [str(x) for x in range(624667, 635860)]
    + [str(x) for x in range(612912, 624666)]
    + [str(x) for x in range(602355, 612910)]
)

last_case_scraped = get_last_scraped()

if last_case_scraped:
    next_idx = case_numbers.index(str(last_case_scraped)) + 1
else:
    next_idx = 0

cases_to_srape = case_numbers[next_idx:]

for case in cases_to_scrape:
    url = os.getenv("LAMBDA_ENDPOINT")
    data = {"event": str(case)}
    requests.post(url, data=data)
