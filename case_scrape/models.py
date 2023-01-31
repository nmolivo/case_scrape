from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import PrimaryKeyConstraint

Base = declarative_base()


class Progress(Base):
    __tablename__ = "progress"
    __table_args__ = (PrimaryKeyConstraint("id", name="progress_id"),)

    id = Column(Integer, autoincrement=True)
    case_id = Column(String)
    date_scraped = Column(DateTime)
    details = Column(String)


class CaseDefendant(Base):
    __tablename__ = "case_defendant"
    __table_args__ = (
        PrimaryKeyConstraint("case_number", name="case_defendant_primary_key"),
    )

    case_number = Column(String, primary_key=True, unique=True)
    status = Column(String)
    judge_name = Column(String)
    next_event = Column(String)
    arrested_date = Column(String)
    arresting_agency = Column(String)
    arresting_agency_report = Column(String)
    court_of_appeals_case = Column(String)
    date_scraped = Column(DateTime)
    defendant_id = Column(String)
    name = Column(String)
    defendant_status = Column(String)
    date_of_birth = Column(String)
    race = Column(String)
    sex = Column(String)
    other_cases = Column(String)
    co_defendants = Column(String)
    charges = relationship("Charge", back_populates="case_defendant")
    bonds = relationship("Bond", back_populates="case_defendant")
    actions = relationship("Action", back_populates="case_defendant")
    dockets = relationship("Docket", back_populates="case_defendant")
    costs = relationship("Cost", back_populates="case_defendant")
    attornies = relationship("Attorney", back_populates="case_defendant")


class Charge(Base):
    __tablename__ = "charge"
    __table_args__ = (PrimaryKeyConstraint("id", name="charges_primary_key"),)

    id = Column(Integer, autoincrement=True)
    case_number = Column(
        String, ForeignKey("case_defendant.case_number"), nullable=False, index=True
    )
    type = Column(String)
    statute = Column(String)
    charge_description = Column(String)
    disposition = Column(String)
    case_defendant = relationship("CaseDefendant", back_populates="charges")


class Bond(Base):
    __tablename__ = "bond"
    __table_args__ = (PrimaryKeyConstraint("id", name="bond_primary_key"),)

    id = Column(Integer, autoincrement=True)
    case_number = Column(
        String, ForeignKey("case_defendant.case_number"), nullable=False, index=True
    )
    bond_number = Column(String)
    amount = Column(String)
    type = Column(String)
    date_set = Column(String)
    date_posted = Column(String)
    bondsman_surety_co = Column(String)
    case_defendant = relationship("CaseDefendant", back_populates="bonds")


class Action(Base):
    __tablename__ = "action"
    __table_args__ = (PrimaryKeyConstraint("id", name="action_primary_key"),)

    id = Column(Integer, autoincrement=True)
    case_number = Column(
        String, ForeignKey("case_defendant.case_number"), nullable=False, index=True
    )
    event_date = Column(String)
    event_description = Column(String)
    case_defendant = relationship("CaseDefendant", back_populates="actions")


class Docket(Base):
    __tablename__ = "docket"
    __table_args__ = (PrimaryKeyConstraint("id", name="docket_primary_key"),)

    id = Column(Integer, autoincrement=True)
    case_number = Column(
        String, ForeignKey("case_defendant.case_number"), nullable=False, index=True
    )
    proceeding_date = Column(String)
    filing_date = Column(String)
    docket_party = Column(String)
    docket_type = Column(String)
    docket_description = Column(String)
    pdf_link = Column(String)
    image_s3_path = Column(String, nullable=True)
    case_defendant = relationship("CaseDefendant", back_populates="dockets")


class Cost(Base):
    __tablename__ = "cost"
    __table_args__ = (PrimaryKeyConstraint("id", name="cost_primary_key"),)

    id = Column(Integer, autoincrement=True)
    case_number = Column(
        String, ForeignKey("case_defendant.case_number"), nullable=False, index=True
    )
    account = Column(String)
    amount = Column(String)
    case_defendant = relationship("CaseDefendant", back_populates="costs")


class Defendant(Base):
    __tablename__ = "defendant"
    __table_args__ = (PrimaryKeyConstraint("id", name="defendant_primary_key"),)

    id = Column(String, primary_key=True, index=True, unique=True, nullable=False)
    name = Column(String)
    status = Column(String)
    marital_status = Column(String)
    birth_city = Column(String)
    birth_state = Column(String)
    citizenship = Column(String)
    address_1 = Column(String)
    address_2 = Column(String)
    address_3 = Column(String)
    city_state_zip = Column(String)
    race = Column(String)
    height = Column(String)
    sex = Column(String)
    weight = Column(String)
    age = Column(String)
    eyes = Column(String)
    date_of_birth = Column(String)
    hair = Column(String)
    aliases = relationship("Alias", back_populates="defendant")


class Alias(Base):
    __tablename__ = "alias"
    __table_args__ = (PrimaryKeyConstraint("id", name="alias_primary_key"),)

    id = Column(Integer, autoincrement=True)
    defendant_id = Column(String, ForeignKey("defendant.id"), nullable=False, index=True)
    case_number = Column(String)
    name = Column(String)
    dob = Column(String)
    defendant = relationship("Defendant", back_populates="aliases")


class Attorney(Base):
    __tablename__ = "attorney"
    __table_args__ = (PrimaryKeyConstraint("id", name="attorney_primary_key"),)

    id = Column(Integer, autoincrement=True)
    case_number = Column(
        String, ForeignKey("case_defendant.case_number"), nullable=False, index=True
    )
    name = Column(String)
    address = Column(String)
    phone = Column(String)
    case_defendant = relationship("CaseDefendant", back_populates="attornies")
