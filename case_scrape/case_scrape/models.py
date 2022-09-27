from sqlalchemy import Column, String, DateTime, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import PrimaryKeyConstraint

Base = declarative_base()


class CaseInformation(Base):
    __tablename__ = "case_information"
    __table_args__ = PrimaryKeyConstraint("id", name="case_information_primary_key")

    id = Column(Integer, autoincrement=True)
    case_number = Column(String, primary_key=True)
    status = Column(String)
    judge_name = Column(String)
    next_event = Column(String)
    arrested_date = Column(String)
    arresting_agency = Column(String)
    arresting_agency_report = Column(String)
    court_of_appeals_case = Column(String)


class DefendantInformation(Base):
    __tablename__ = "defendant_information"
    __table_args__ = PrimaryKeyConstraint(
        "id", name="defendant_information_primary_key"
    )

    id = Column(Integer, autoincrement=True)
    case_number = Column(String)
    number = Column(String, primary_key=True)
    name = Column(String)
    status = Column(String)
    date_of_birth = Column(String)
    race = Column(String)
    sex = Column(String)
    other_cases = Column(String)
    co_defendants = Column(String)


class Charges(Base):
    __tablename__ = "charges"
    __table_args__ = PrimaryKeyConstraint("id", name="charges_primary_key")

    id = Column(Integer, autoincrement=True)
    case_number = Column(String)
    type = Column(String)
    statute = Column(String)
    charge_description = Column(String)
    disposition = Column(String)


class BondInformation(Base):
    __tablename__ = "bond_information"
    __table_args__ = PrimaryKeyConstraint("id", name="bond_information_primary_key")

    id = Column(Integer, autoincrement=True)
    case_number = Column(String)
    number = Column(String)
    amount = Column(Float)
    type = Column(String)
    date_set = Column(DateTime)
    date_posted = Column(DateTime)
    bondsman_surety_co = Column(String)


class CaseActions(Base):
    __tablename__ = "case_actions"
    __table_args__ = PrimaryKeyConstraint("id", name="case_action_primary_key")

    id = Column(Integer, autoincrement=True)
    case_number = Column(String)
    event_date = Column(DateTime)
    event_description = Column(String)


class DocketInformation(Base):
    __tablename__ = "docket_information"
    __table_args__ = PrimaryKeyConstraint("id", name="docket_information_primary_key")

    id = Column(Integer, autoincrement=True)
    proceeding_date = Column(DateTime)
    filing_date = Column(DateTime)
    docket_party = Column(String)
    docket_type = Column(String)
    docket_description = Column(String)
    pdf_link = Column(String)
    image_s3_path = Column(String, nullable=True)


class CostInformation(Base):
    __tablename__ = "cost_information"
    __table_args__ = PrimaryKeyConstraint("id", name="cost_primary_key")

    case_information
    id = Column(Integer, autoincrement=True)
    account = Column(String)
    amount = Column(String)


class Defendant(Base):
    __tablename__ = "defendant"
    __table_args__ = PrimaryKeyConstraint("id", name="defendant_primary_key")

    id = Column(Integer, autoincrement=True)
    name = Column(String)
    id = Column(String)
    status = Column(String)
    marital_status = Column(String)
    birth_city = Column(String)
    birth_state = Column(String)
    citizenship = Column(String)
    address_1 = Column(String)
    address_2 = Column(String)
    address_3 = Column(String)
    city_state_zip = Column(String)
    aliases = Column(String)
    race = Column(String)
    height = Column(String)
    sex = Column(String)
    weight = Column(String)
    age = Column(String)
    eyes = Column(String)
    date_of_birth = Column(String)
    hair = Column(String)


class Attorney(Base):
    __tablename__ = "attorny"
    __table_args__ = PrimaryKeyConstraint("id", name="attorney_primary_key")

    id = Column(Integer, autoincrement=True)
    attorney_id = Column()
    name = Column(String)
    address_phone = Column(String)
