import random
import re
from datetime import datetime
from typing import Tuple, Union, List

import pandas as pd

from sqlalchemy.orm import Session
from db.db_config import DBConfig
from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import and_
from sqlalchemy.orm import Session

from db import models


### Functions for committing to database :)


def check_tos(driver: WebDriver) -> webdriver.Chrome:
    # anticipates terms of service pop up
    driver.implicitly_wait(random.randrange(1, 5))
    if "TOS" in driver.current_url:
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "SheetContentPlaceHolder_btnYes"))
            ).click()
        except WebDriverException:
            return driver
        driver.implicitly_wait(3)
    return driver


def search_case_number(driver: WebDriver, case_number: str) -> webdriver.Chrome:
    """Goes to search page, upon landing on the search page, this function will navigate the agreement and then enter a case
    number to search criminal records and click the submit button.
    Be sure to already be on the case search page when you run this function."""
    driver.get("https://cpdocket.cp.cuyahogacounty.us/Search.aspx")
    driver = check_tos(driver)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_rbCrCase')]")
        )
    ).click()
    driver.implicitly_wait(2)

    if len(driver.find_elements(By.ID, "SheetContentPlaceHolder_btnYes")) > 0:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "SheetContentPlaceHolder_btnYes"))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_rbCrCase')]")
            )
        ).click()
        driver.implicitly_wait(3)

    # checks if searching elements are there
    if (
        len(driver.find_elements(By.ID, "SheetContentPlaceHolder_ctl00_gvCaseResults"))
        == 0
    ):
        text_box = driver.find_element(By.XPATH, "//input[(@type = 'text')]")
        text_box.clear()
        text_box.send_keys(case_number)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.ID, "SheetContentPlaceHolder_criminalCaseSearch_btnSubmitCase")
            )
        ).click()
        driver.implicitly_wait(random.randint(4, 15))

    return driver


def get_images(data, images) -> List[str]:
    # used to obtain a list of hrefs to the pdf images accompanying docket records
    data_list = []
    image_count = 0
    for d in data:
        if d.accessible_name == "View Docket Image":
            data_list.append(images[image_count].get_attribute("href"))
            image_count += 1
        else:
            data_list.append(d.text)
    return data_list


def get_table(
    driver: WebDriver,
    case_number: str,
    header_xpath: str,
    data_xpath: str,
    image_xpath: Union[None, str] = None,
) -> Tuple[webdriver.Chrome, pd.DataFrame]:
    headers = driver.find_elements(By.XPATH, header_xpath)
    data = driver.find_elements(By.XPATH, data_xpath)
    if image_xpath:
        images = driver.find_elements(By.XPATH, image_xpath)
        data_list = get_images(data, images)
    else:
        data_list = [d.text for d in data]
    table = {}
    for i, h in enumerate(headers):
        table[h.text.upper().strip()] = data_list[i :: len(headers)]
    df = pd.DataFrame(table)
    df["CASE_NUMBER"] = case_number
    return driver, df


def write_pandas_df_to_db(engine, df: pd.DataFrame, table_to_write_to: str) -> None:
    df.columns = df.columns.str.replace(" ", "_")
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace("/", "_")
    df.columns = df.columns.str.replace(".", "")
    df.to_sql(table_to_write_to, engine, if_exists="append", index=False)


def fetch_case_summary(engine, driver: WebDriver) -> Tuple[WebDriver, str]:
    """commits returns case_number"""
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblCaseNumber')]",
            )
        )
    )
    case_number = driver.find_element(
        By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblCaseNumber')]"
    ).text
    try:
        coa_case = court_of_appeals_case = driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblCOACase')]"
        ).text
    except NoSuchElementException:
        coa_case = court_of_appeals_case = (
            driver.find_element(
                By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_caseSummary_pCOACase')]"
            ).text,
        )
    case_defendant = models.CaseDefendant(
        case_number=case_number,
        status=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblCaseStatus')]"
        ).text,
        judge_name=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblJudgeName')]"
        ).text,
        next_event=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblNextEvent')]"
        ).text,
        arrested_date=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblArrested')]"
        ).text,
        arresting_agency=driver.find_element(
            By.XPATH,
            "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblArrestingAgency')]",
        ).text,
        arresting_agency_report=driver.find_element(
            By.XPATH,
            "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblArestingAgencyReport')]",
        ).text,
        court_of_appeals_case=coa_case,
        date_scraped=datetime.now(),
        defendant_id=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblNumber')]"
        ).text,
        name=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblName')]"
        ).text,
        defendant_status=driver.find_element(
            By.XPATH,
            "//*[(@id = 'SheetContentPlaceHolder_caseSummary_defStatus_lblDefStatus')]",
        ).text,
        date_of_birth=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblDOB')]"
        ).text,
        race=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblRace')]"
        ).text,
        sex=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_caseSummary_lblSex')]"
        ).text,
        other_cases=driver.find_element(
            By.XPATH,
            "//*[(@id = 'SheetContentPlaceHolder_caseSummary_otherCases_lblOtherCases')]",
        ).text,
        co_defendants=driver.find_element(
            By.XPATH,
            "//*[(@id = 'SheetContentPlaceHolder_caseSummary_otherDefs_lblCoDefs')]",
        ).text,
    )
    with Session(engine) as db:
        db.merge(case_defendant)
        db.commit()
    return driver, case_number


def fetch_case_summary_tables(engine, driver, case_number) -> Tuple[WebDriver, str]:
    """gets info from case summary page"""
    # additional tables
    driver, charge_df = get_table(
        driver,
        case_number,
        header_xpath="//table[(@id = 'SheetContentPlaceHolder_caseCharges_gvCharges')]//th",
        data_xpath="//table[(@id = 'SheetContentPlaceHolder_caseCharges_gvCharges')]//td",
    )
    # delete all before adding them if they exist
    with Session(engine) as db:
        if (
            len(
                db.query(models.Charge)
                .filter(models.Charge.case_number == case_number)
                .all()
            )
            > 0
        ):
            dele = models.Charge.__table__.delete().where(
                models.Charge.case_number == case_number
            )
            db.execute(dele)
            db.commit()
    write_pandas_df_to_db(engine, charge_df, "charge")

    driver, bond_df = get_table(
        driver,
        case_number,
        header_xpath="//table[(@id = 'SheetContentPlaceHolder_caseBondInfo_gvBonds')]//th",
        data_xpath="//table[(@id = 'SheetContentPlaceHolder_caseBondInfo_gvBonds')]//td",
    )
    with Session(engine) as db:
        if (
            len(
                db.query(models.Bond)
                .filter(models.Bond.case_number == case_number)
                .all()
            )
            > 0
        ):
            dele = models.Bond.__table__.delete().where(
                models.Bond.case_number == case_number
            )
            db.execute(dele)
            db.commit()
    write_pandas_df_to_db(engine, bond_df, "bond")

    driver, action_df = get_table(
        driver,
        case_number,
        header_xpath="//table[(@id = 'SheetContentPlaceHolder_caseActions_gvActions')]//th",
        data_xpath="//table[(@id = 'SheetContentPlaceHolder_caseActions_gvActions')]//td",
    )
    with Session(engine) as db:
        if (
            len(
                db.query(models.Action)
                .filter(models.Action.case_number == case_number)
                .all()
            )
            > 0
        ):
            dele = models.Action.__table__.delete().where(
                models.Action.case_number == case_number
            )
            db.execute(dele)
            db.commit()
    write_pandas_df_to_db(engine, action_df, "action")
    return driver, case_number


def fetch_docket_info(
    engine, driver: WebDriver, case_number: str
) -> Tuple[WebDriver, str]:
    """from case summary page, clicks docket, downloads information, checks if it already exists, deletes if so, then appends to database."""
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.ID, "SheetContentPlaceHolder_caseHeader_lbDocket")
        )
    ).click()
    driver = check_tos(driver)
    driver, docket_table = get_table(
        driver,
        case_number,
        header_xpath="//table[(@id = 'SheetContentPlaceHolder_caseDocket_gvDocketInformation')]//th",
        data_xpath="//table[(@id = 'SheetContentPlaceHolder_caseDocket_gvDocketInformation')]//td",
        image_xpath="//table[(@id = 'SheetContentPlaceHolder_caseDocket_gvDocketInformation')]//td//a",
    )
    docket_table.rename(columns={"VIEW IMAGE": "pdf_link"}, inplace=True)
    with Session(engine) as db:
        if (
            len(
                db.query(models.Docket)
                .filter(models.Docket.case_number == case_number)
                .all()
            )
            > 0
        ):
            dele = models.Docket.__table__.delete().where(
                models.Docket.case_number == case_number
            )
            db.execute(dele)
            db.commit()
    write_pandas_df_to_db(engine, docket_table, "docket")
    return driver, case_number


def fetch_cost_info(
    engine, driver: WebDriver, case_number: str
) -> Tuple[WebDriver, str]:
    """Clicks the cost panel, obtains table, observes if table already exists, deletes if so, appends new records to database"""
    WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable(
            (By.ID, "SheetContentPlaceHolder_caseHeader_lbCosts")
        )
    ).click()
    # anticipates terms of service
    driver = check_tos(driver)
    # SheetContentPlaceHolder_caseCosts_gvCosts
    driver, cost_table = get_table(
        driver,
        case_number,
        header_xpath="//table[(@id = 'SheetContentPlaceHolder_caseCosts_gvCosts')]//th",
        data_xpath="//table[(@id = 'SheetContentPlaceHolder_caseCosts_gvCosts')]//td",
    )
    # remove "Total" row, as we can calculate this ourselves.
    cost_table[cost_table["ACCOUNT"].str.contains("TOTAL") == False]
    with Session(engine) as db:
        if (
            len(
                db.query(models.Cost)
                .filter(models.Cost.case_number == case_number)
                .all()
            )
            > 0
        ):
            dele = models.Cost.__table__.delete().where(
                models.Cost.case_number == case_number
            )
            db.execute(dele)
            db.commit()
    write_pandas_df_to_db(engine, cost_table, "cost")
    return driver, case_number


def fetch_defendant_info(engine, driver, case_number):
    WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable(
            (By.ID, "SheetContentPlaceHolder_caseHeader_lbDefendant")
        )
    ).click()
    driver = check_tos(driver)
    defendant = models.Defendant(
        name=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defGeneral_lblName')]"
        ).text,
        id=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defGeneral_lblDefID')]"
        ).text,
        status=driver.find_element(
            By.XPATH,
            "//*[(@id = 'SheetContentPlaceHolder_defGeneral_defStatus_lblDefStatus')]",
        ).text,
        marital_status=driver.find_element(
            By.XPATH,
            "//*[(@id = 'SheetContentPlaceHolder_defGeneral_lblMaritalStatus')]",
        ).text,
        birth_city=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defGeneral_lblBirthCity')]"
        ).text,
        birth_state=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defGeneral_lblBirthState')]"
        ).text,
        citizenship=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defGeneral_lblCitizenship')]"
        ).text,
        address_1=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defAddress_lblAddress1')]"
        ).text,
        address_2=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defAddress_lblAddress2')]"
        ).text,
        # address_3=driver.find_elements(By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defAddress_lblAddress3')]").text,
        city_state_zip=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defAddress_lblCSZ')]"
        ).text,
        race=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defIDChar_lblRace')]"
        ).text,
        height=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defIDChar_lblHeight')]"
        ).text,
        sex=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defIDChar_lblSex')]"
        ).text,
        weight=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defIDChar_lblWeight')]"
        ).text,
        age=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defIDChar_lblAge')]"
        ).text,
        eyes=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defIDChar_lblEyes')]"
        ).text,
        date_of_birth=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defIDChar_lblDOB')]"
        ).text,
        hair=driver.find_element(
            By.XPATH, "//*[(@id = 'SheetContentPlaceHolder_defIDChar_lblHair')]"
        ).text,
    )
    with Session(engine) as db:
        db.merge(defendant)
        db.commit()
        driver, alias_table = get_table(
            driver,
            case_number,
            header_xpath="//table[(@id = 'SheetContentPlaceHolder_defAlias_gvAlias')]//th",
            data_xpath="//table[(@id = 'SheetContentPlaceHolder_defAlias_gvAlias')]//td",
        )
        alias_table["defendant_id"] = defendant.id
        # deletes existing records so as not to duplicate
        if (
            len(
                db.query(models.Alias)
                .filter(
                    and_(
                        models.Alias.case_number == case_number,
                        models.Alias.defendant_id == defendant.id,
                    )
                )
                .all()
            )
            > 0
        ):
            dele = models.Alias.__table__.delete().where(
                and_(
                    models.Alias.case_number == case_number,
                    models.Alias.defendant_id == defendant.id,
                )
            )
            db.execute(dele)
            db.commit()
    write_pandas_df_to_db(engine, alias_table, "alias")
    return driver, case_number


def get_attorney_table(engine, driver, case_number, table_data):
    data = driver.find_elements(By.XPATH, table_data)
    data_list = [d.text for d in data]
    atts = [
        x
        for x in list(set(data_list))
        if x.count("Address/Phone") == 1 and x.count("Attorney Name") == 1
    ]
    attorney_names = [
        x.split("\nAddress/Phone:")[0].replace("Attorney Name:", "").strip()
        for x in atts
    ]
    attorney_address = [
        x.split("\nAddress/Phone:")[1].split("\nPh:")[0].strip() for x in atts
    ]
    try:
        attorney_phone = [
            x.split("\nAddress/Phone:")[1].split("\nPh:")[1].strip() for x in atts
        ]
    except IndexError:
        attorney_phone = [
            x.split("\nAddress/Phone:")[1].split("\n")[-1].strip() for x in atts
        ]
    with Session(engine) as db:
        if (
            len(
                db.query(models.Attorney)
                .filter(models.Attorney.case_number == case_number)
                .all()
            )
            > 0
        ):
            dele = models.Attorney.__table__.delete().where(
                models.Attorney.case_number == case_number
            )
            db.execute(dele)
            db.commit()
        for n, a, p in zip(attorney_names, attorney_address, attorney_phone):
            if not re.match(r"^[1-9]\d{2}-\d{3}-\d{4}", p):
                p = ""
            else:
                a = a.replace(p, "").strip()
            attorney = models.Attorney(
                case_number=case_number, name=n, address=a, phone=p
            )
            db.add(attorney)
        db.commit()
    return driver


def fetch_attorney_info(engine, driver, case_number):
    WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable(
            (By.ID, "SheetContentPlaceHolder_caseHeader_lbAttorney")
        )
    ).click()
    driver = check_tos(driver)
    driver = get_attorney_table(
        engine,
        driver,
        case_number,
        "//table[(@id='SheetContentPlaceHolder_attyInfo_gvAttyInfo')]//*",
    )
    return driver, case_number


def update_case(engine, case_number, status):
    db_progress = models.Progress(
        case_id=case_number, date_scraped=datetime.now(), details=status
    )
    with Session(engine) as db:
        db.add(db_progress)
        db.commit()


### The lambda handler!!!


def lambda_handler(event, context):
    case_no_str = event["case_number"]
    opts = Options()
    opts.binary_location = "/opt/chrome/chrome"
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--no-zygote")
    opts.add_argument("--single-process")
    opts.add_argument("--user-data-dir=/tmp/chrome-user-data")
    opts.add_argument("--disable-gpu-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--dasable-dev-tools")
    opts.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome("/opt/chromedriver", options=opts)
    driver = search_case_number(driver, case_no_str)
    db_config = DBConfig()
    engine = db_config.get_engine()
    data_elems = driver.find_elements(
        By.XPATH,
        "//*[(@id='SheetContentPlaceHolder_ctl00_gvCaseResults')]//*[@href]",
    )
    if len(data_elems) > 0:
        for i, _ in enumerate(data_elems):
            data_elems = driver.find_elements(
                By.XPATH,
                "//*[(@id='SheetContentPlaceHolder_ctl00_gvCaseResults')]//*[@href]",
            )
            data_elems[i].click()
            driver, case_number = fetch_case_summary(engine, driver)
            driver, case_number = fetch_case_summary_tables(engine, driver, case_number)
            driver, case_number = fetch_docket_info(engine, driver, case_number)
            driver.back()
            driver = check_tos(driver)
            driver, case_number = fetch_cost_info(engine, driver, case_number)
            driver.back()
            driver = check_tos(driver)
            driver, case_number = fetch_defendant_info(engine, driver, case_number)
            driver.back()
            driver = check_tos(driver)
            driver, case_number = fetch_attorney_info(engine, driver, case_number)
            driver.back()
            driver = check_tos(driver)
            driver.back()
            update_case(engine, case_no_str, "Data Obtained")
    else:
        try:
            driver, case_number = fetch_case_summary(engine, driver)
            driver, case_number = fetch_case_summary_tables(engine, driver, case_number)
            driver, case_number = fetch_docket_info(engine, driver, case_number)
            driver, case_number = fetch_cost_info(engine, driver, case_number)
            driver, case_number = fetch_defendant_info(engine, driver, case_number)
            driver, case_number = fetch_attorney_info(engine, driver, case_number)
            update_case(engine, case_no_str, "Data Obtained")
            driver.close()
            driver.quit()

        except TimeoutException:
            driver.close()
            driver.quit()
            update_case(engine, case_no_str, "No Data")
