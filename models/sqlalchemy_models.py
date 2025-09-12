from sqlalchemy import Column, NUMERIC, VARCHAR
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel
from typing import List, AsyncGenerator, Optional

Base = declarative_base()

######################
# ===Table: Categories===
class Category(Base):
    __tablename__ = "Categories"
    categories_id = Column(NUMERIC, nullable=False, primary_key=True)
    categories = Column(VARCHAR)

class IndicatorSelection(BaseModel):
    selected_indicators: List[int]
    category_type: str
    selected_state: Optional[int] = None

class IndicatorTypeOut(BaseModel):
    indicator_id: float  # or int if you're not using decimal
    indicator_name: str
    indicator_type: str

    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    selected_value: int
    state_name: Optional[str] = None

# Pydantic Input model (for POST requests)
class CategoryIn(BaseModel):
    categories_id: float  
    categories: str  

# Pydantic Output model (for GET responses)
class CategoryOut(BaseModel):
    categories_id: float  
    categories: str
    class Config:
        from_attributes = True

# ===Table: Districts===
# SQLAlchemy model
class District(Base):
    __tablename__ = "Districts"
    district_id = Column(NUMERIC, nullable=False, primary_key=True)
    state_id = Column(NUMERIC)
    district_name = Column(VARCHAR)

# Pydantic Input model (for POST requests)
class DistrictIn(BaseModel):
    district_id: float
    state_id: float  
    district_name: str  

# Pydantic Output model (for GET responses)
class DistrictOut(BaseModel):
    district_id: float
    state_id: float  
    district_name: str
    class Config:
        from_attributes = True

# ===Table: Indicators===
# SQLAlchemy model
class Indicator(Base):
    __tablename__ = "Indicators"
    indicator_id = Column(NUMERIC, nullable=False, primary_key=True)
    indicator_name = Column(VARCHAR)
    indicator_type_id = Column(NUMERIC)
    indicator_type = Column(VARCHAR)

# Pydantic Input model (for POST requests)
class IndicatorIn(BaseModel):
    indicator_id: float
    indicator_name: str
    indicator_type_id: float  
    indicator_type: str  

# Pydantic Output model (for GET responses)
class IndicatorOut(BaseModel):
    indicator_id: float
    indicator_name: str
    indicator_type_id: float  
    indicator_type: str
    class Config:
        from_attributes = True

# ===Table: NFHS_District_Data===
# SQLAlchemy model
class NFHSDistrictData(Base):
    __tablename__ = "NFHS_District_Data"
    data_id = Column(NUMERIC, nullable=False, primary_key=True)
    state_id = Column(NUMERIC)
    district_id = Column(NUMERIC)
    indicator_id = Column(NUMERIC)
    categories_id = Column(NUMERIC)
    nfhs_id = Column(NUMERIC)
    st = Column(VARCHAR)
    non_st = Column(VARCHAR)
    total = Column(VARCHAR)
    st_avg_total = Column(VARCHAR)

# ===Table: NFHS_Rounds===
# SQLAlchemy model
class NFHSRound(Base):
    __tablename__ = "NFHS_Rounds"
    nfhs_id = Column(NUMERIC, nullable=False, primary_key=True)
    nfhs_round = Column(VARCHAR)

# ===Table: NFHS_State_Data===
# SQLAlchemy model
class NFHSStateData(Base):
    __tablename__ = "NFHS_State_Data"
    data_id = Column(NUMERIC, nullable=False, primary_key=True)
    state_id = Column(NUMERIC)   
    indicator_id = Column(NUMERIC)
    categories_id = Column(NUMERIC)
    nfhs_id = Column(NUMERIC)
    st = Column(VARCHAR)
    non_st = Column(VARCHAR)
    total = Column(VARCHAR)
    nat_avg_total = Column(VARCHAR)

# Table: State
# SQLAlchemy model
class State(Base):
    __tablename__ = "States"
    state_id = Column(NUMERIC, nullable=False, primary_key=True)
    state_name = Column(VARCHAR)
    state_acronym = Column(VARCHAR)

# Pydantic Input model (for POST requests)
class StateIn(BaseModel):
    state_id: float
    state_name: str
    state_acronym: str
    
# Pydantic Output model (for GET responses)
class StateOut(BaseModel):
    state_id: float
    state_name: str
    state_acronym: str
    class Config:
        from_attributes = True
