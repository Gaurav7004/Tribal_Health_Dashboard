from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, VARCHAR, NUMERIC
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, aliased
from sqlalchemy import Column, String, Numeric, cast, select, func, text
from pydantic import BaseModel
from typing import List, AsyncGenerator, Optional
import uvicorn
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi import Request
import json, asyncio, os, re
from src.components.llm.backend.bitnet_inference import *
import httpx
from analysis_utils import compute_indicator_correlations, compute_indicator_stats
from models.sqlalchemy_models import *

# Load cluster district IDs that needs to blocked
with open(os.path.join(os.path.dirname(__file__), "cluster_district_ids.json")) as f:
    BLOCKED_DISTRICT_IDS = set(json.load(f))


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
) 

# Database configuration
DATABASE_URL = "postgresql+asyncpg://postgres:T_DashPCC01@localhost:5432/Tribal_Dashboard"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
                                bind=engine,
                                class_=AsyncSession,
                                expire_on_commit=False
                            )
Base = declarative_base()


###########################################
''' FastAPI app setup '''
###########################################

# Dependency to get database session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# Lifespan event handler to create tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

###########################################
''' API Endpoints '''
###########################################

@app.post("/indicator-stats")
async def get_indicator_stats(data: IndicatorSelection, db: AsyncSession = Depends(get_session)):
    stats_data = await compute_indicator_stats(data, db)
    return {"stats": stats_data}

@app.post("/indicator-correlation")
async def get_indicator_correlation(data: IndicatorSelection, db: AsyncSession = Depends(get_session)):
    correlations = await compute_indicator_correlations(data, db)
    return {"correlations": correlations}

@app.post("/getStatesByIndicators")
async def get_states_by_indicators(
        data: IndicatorSelection,
        db: AsyncSession = Depends(get_session)
    ):
    indicator_data = []

    column_mapping = {
        "ST": "st",
        "Non-ST": "non_st",
        "Total": "total"
    }

    category_value = data.category_type
    if category_value not in column_mapping:
        raise HTTPException(status_code=400, detail=f"Invalid category_type: {category_value}")

    column_name = column_mapping[category_value]

    if data.selected_state:  
        # Query NFHS_District_Data filtered by selected state
        selected_category = getattr(NFHSDistrictData, column_name)

        for indicator_id in data.selected_indicators:
            stmt = (
                select(NFHSDistrictData.indicator_id, District.district_name, District.district_id, selected_category)
                .join(NFHSDistrictData, NFHSDistrictData.district_id == District.district_id)
                .where(
                    NFHSDistrictData.indicator_id == indicator_id,
                    District.state_id == data.selected_state
                )
            )
            result = await db.execute(stmt)
            rows = result.all()

            # Filter out blocked cluster districts
            rows = [r for r in rows if int(r[2]) not in BLOCKED_DISTRICT_IDS]

            indicator = await db.get(Indicator, indicator_id)

            def safe_float(val):
                try:
                    return float(val)
                except ValueError:
                    return None

            indicator_data.append({
                "indicator_id": indicator_id,
                "indicator_name": indicator.indicator_name,
                "data": [{"district_name": r[0], category_value: safe_float(r[3])} for r in rows]
            })

    else:
        # Query NFHS_State_Data
        selected_category = getattr(NFHSStateData, column_name)

        for indicator_id in data.selected_indicators:
            stmt = (
                select(State.state_name, State.state_acronym, selected_category)
                .join(NFHSStateData, NFHSStateData.state_id == State.state_id)
                .where(NFHSStateData.indicator_id == indicator_id)
            )
            result = await db.execute(stmt)
            rows = result.all()

            indicator = await db.get(Indicator, indicator_id)

            def safe_float(val):
                try:
                    return float(val)
                except ValueError:
                    return None

            indicator_data.append({
                "indicator_id": indicator_id,
                "indicator_name": indicator.indicator_name,
                "data": [{"state_name": r[0], "state_acronym": r[1], category_value: safe_float(r[2])} for r in rows]
            })

    return JSONResponse(
        status_code=200,
        content={"indicator_data": indicator_data}
    )

@app.post("/getDistrictsByIndicators")
async def get_districts_by_indicators(
    data: IndicatorSelection,
    db: AsyncSession = Depends(get_session)
):
    indicator_data = []

    column_mapping = {
        "ST": "st",
        "Non-ST": "non_st",
        "Total": "total"
    }

    category_value = data.category_type
    if category_value not in column_mapping:
        raise HTTPException(status_code=400, detail=f"Invalid category_type: {category_value}")

    column_name = column_mapping[category_value]
    selected_category = getattr(NFHSDistrictData, column_name)

    for indicator_id in data.selected_indicators:
        stmt = (
            select(
                NFHSDistrictData.indicator_id,
                District.district_name,
                District.district_id,
                NFHSDistrictData.state_id,
                selected_category
            )
            .join(NFHSDistrictData, NFHSDistrictData.district_id == District.district_id)
            .where(
                NFHSDistrictData.indicator_id == indicator_id,
                District.state_id == data.selected_state
            )
        )
        result = await db.execute(stmt)
        rows = result.all()

        # Filter out blocked cluster districts
        rows = [r for r in rows if int(r[2]) not in BLOCKED_DISTRICT_IDS]

        indicator = await db.get(Indicator, indicator_id)

        def safe_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        indicator_data.append({
            "indicator_id": indicator_id,
            "indicator_name": indicator.indicator_name,
            "data": [
                {
                    "district_name": r[1],
                    "district_id": int(r[2]),
                    "state_id": int(r[3]),
                    category_value: safe_float(r[4])
                }
                for r in rows
            ]
        })

    return JSONResponse(
        status_code=200,
        content={"indicator_data": indicator_data}
    )

# === Categories ===
@app.get("/Categories", response_model=List[CategoryOut])
async def get_categories(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Category))
    return result.scalars().all()

@app.post("/receiveCategories")
async def receive_categories(data: CategoryResponse, db: AsyncSession = Depends(get_session)):
    category_id_from_categories_dropdown = data.selected_value

    result = await db.execute(
        select(Indicator)
        .join(NFHSStateData, NFHSStateData.indicator_id == Indicator.indicator_id)
        .where(NFHSStateData.categories_id == category_id_from_categories_dropdown)
        .order_by(Indicator.indicator_id.asc())
        .distinct()
    )

    indicators = result.scalars().all()

    indicators_list = [
        {"indicator_id": int(i.indicator_id), "indicator_name": i.indicator_name} for i in indicators
    ]

    return JSONResponse(
        status_code=200,
        content={"state_indicators": indicators_list}
    )

# === Indicators ===
@app.get("/Indicators", response_model=List[IndicatorOut])
async def get_indicators(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Indicator))
    return result.scalars().all()

@app.get("/IndicatorType", response_model=List[IndicatorTypeOut])
async def get_indicators_type(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Indicator))
    return result.scalars().all()

# === State ===
@app.get("/States", response_model=List[StateOut])
async def get_states(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(State))
    return result.scalars().all()

def format_summary_markdown(summary: str) -> str:
    # Converted Qwen raw summary into clean markdown format
    summary = summary.replace("## Indicator Summary", "## Indicator Summary")
    summary = summary.replace("## Variability", "\n---\n\n## Variability")
    summary = summary.replace("## Correlations", "\n---\n\n## Correlations")

    # Added bold styling for numeric stats
    summary = re.sub(r"(\d+\.\d+%)", r"**\1**", summary)
    summary = re.sub(r"(standard deviation: )(\d+\.\d+)", r"\1**\2**", summary)
    summary = re.sub(r"(correlation coefficient: )(\d+\.\d+)", r"\1**\2**", summary)

    return summary.strip()


# === AI Insights ===
@app.post("/indicator-summary")
async def generate_indicator_summary(
    data: IndicatorSelection,
    db: AsyncSession = Depends(get_session)
):
    # Direct function calls, no HTTP overhead
    stats_data = await compute_indicator_stats(data, db)
    correlations = await compute_indicator_correlations(data, db)

    context = f"""
    Indicator statistics:
    {stats_data}

    Indicator correlations:
    {correlations}

    Task:
        Write a clear, professional, and factual analytical summary (200–300 words) of the indicator data.
        - Emphasize the minimum and maximum values, including the associated indicator names and states/districts mentioned.
        - Discuss the standard deviation and variability across indicators.
        - Highlight significant correlations between indicators and their possible implications.
        - Important : Provide the **summary** not the codes or json 
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:270m",
                "prompt": context,
                "stream": False,
                "temperature": 0.5   # 👈 keep it low for factual output
            },
            timeout=300
        )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Ollama request failed: {response.text}")
    
    print(response.json(), '------------- GEN SUMMARY -------------')

    return {"summary": response.json().get("response", "").strip()}


if __name__ == "__main__":
    uvicorn.run("fastapi_server:app", host="127.0.0.1", port=8000, reload=True)
