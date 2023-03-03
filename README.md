# case_scrape
A repo to teach web scraping basics, supported by AWS resources and public data.

***

There's a lot you can do with court data. This repo contains materials for learning web scraping and creating a database.

Project Features:
- Selenium Web Scraper
- SQLAlchemy ORM

How it Runs:
- AWS Lambda
- AWS ECR (Elasitc Container Registry)
- AWS RDS (Relational Database Service) - Postgres
- AWS IAM roles

***

# Learn to make this
There are a few components to this tool.
1. The scraper
    Written in python, uses Selenium to navigate website. I used Chrome extensions X and Y to help me find the XPATHs used in this scraper. While the Criminal Court docket website requires some navigation and clicks for our scraper to agree to the Terms of Service before gathering public data, these XPATHs make the scraper rather frail. Should the website change these tags over time, we would need to deploy a new version.
    
2. The AWS Lambda function
    A lambda function spins up a new virtual computer for each request made to it. This is how the scraper runs in such a way that it will not get blocked by the website. In this case, we deploy the Lambda function as a container image hosted on AWS ECR, and take advantage of the Lambda function's URL endpoint to run the scrape. 

3. AWS Elastic Container Registry
    By containerizing our Lambda function with Docker, we are able to take advantage of Lambda's most generous default quota for code package size. This is needed because installing a browser to scrape with Selenium require time and space beyond what the other deployment options offer. (.zip Deployment package, code in the console)

4. AWS Relational Database Service
    Under Amazon's free tier offering, we can house the entire Criminal Court Case docket. I used Postgres because it has a free-tier offering and I'm familiar with it. I would love to try Aurora.

3. Github actions
    With each push to main, a new ECR image is created and the Lambda function is updated.

I've created a terraform script to describe how each of these items fit together, but actually did not use terraform to create this, yet. 

A consideration in running scrapers is we do not wish to crash the host website. As a result, we choose a friendly rate of about 3 cases per minute. Given there are about 70K cases total, it takes about 16 days to obtain all the data if it runs non-stop. Manual and programmatic data quality checks are performed and a case can be re-scraped to be updated or corrected. Each time a case is re-scraped, all its corresponding records (charges, cost, docket, attorney, bond, defendent) are deleted and re-written so that the database will not contain duplicate records.

***

# Request permission to access this data

This is public data previously scraped by The Marshall Project under research grant XXXXX.XX. After learning about the Marshall Project's efforts at DataDays Cleveland, I wanted to give it a try.
Building an API to access this data would be a great pleasure of mine but is currently done on a volunteer basis around other obligations to my livelihood. 
At this time, I can grant read-only access to the database to anybody who requests on my own time. I can be motivated with gifts.

***

# Getting Started

I'm not sure who the audience of this github repo is, but once I find out, I'll update this. 
- Are you trying to deploy a scraper? - If so, where are your pain points?
- Are you trying to research criminal court cases? - If so, let's collab.
- Are you curious about what happens with this project? - Feel free to "Watch" this repository. While data analysis and the API will be housed in a different repository, I'll do my best to keep this README abreast of any updates.


# To scrape:

### Import packages
```python
import json
import random
import time


from sqlalchemy import func
from sqlalchemy.orm import Session
from db import models
from db.db_config import DBConfig
```

### Make engine
```python
db_config = DBConfig(password=os.getenv("DB_PASSWORD"),
                     user=os.getenv("DB_USER"),
                     database=os.getenv("DB_DATABASE"),
                     host=os.getenv("DB_HOST"),
                     port=os.getenv("DB_PORT"),
                     scheme=os.getenv("DB_SCHEME"))
engine = db_config.get_engine()
```

### Get the cases that were already scraped
```python
def get_cases(engine):
    with Session(engine) as db:
        cases = db.query(models.Progress.case_id).all()
    return [x[0] for x in cases]

case_numbers = (
    [str(x) for x in range(655656, 666532)]
    + [str(x) for x in range(647313, 655655)]
    + [str(x) for x in range(635863, 647312)]
    + [str(x) for x in range(624667, 635860)]
    + [str(x) for x in range(612912, 624666)]
    + [str(x) for x in range(602355, 612910)]
)

cases_to_scrape = sorted(list(set(case_numbers) - set(cases)), reverse=True)
```

### Use boto to send payload to Lambda endpoint
```python
client = boto3.client("lambda")

for case in sorted_cases:
    data = json.dumps({"event": str(case)})
    headers = {'Content-type': 'application/json', 'SignatureHeader': 'XYZ'}
    response = client.invoke(FunctionName="criminal_case_scrape",
                             InvocationType="Event",
                             Payload = json.dumps({"case_number": case}))
    print(f"scraped case {case}")
    time.sleep(random.randrange(15, 25))
```


(C) :fly: 

***

