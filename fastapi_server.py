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
from jinja2 import Template

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
                if val is None:
                    return None
                if isinstance(val, str):
                    if val.strip().upper() == "NA" or val.strip() == "":
                        return None
                try:
                    return float(val)
                except (ValueError, TypeError):
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


# # === AI Insights ===
# @app.post("/indicator-summary")
# async def generate_indicator_summary(
#     data: IndicatorSelection,
#     db: AsyncSession = Depends(get_session)
# ):
#     # Direct function calls, no HTTP overhead
#     stats_data = await compute_indicator_stats(data, db)
#     correlations = await compute_indicator_correlations(data, db)

#     context = f"""
#     Indicator statistics:
#     {stats_data}

#     Indicator correlations:
#     {correlations}

#     Task:
#         Write a clear, professional, and factual analytical summary (200–300 words) of the indicator data.
#         - Emphasize the minimum and maximum values, including the associated indicator names and states/districts mentioned.
#         - Discuss the standard deviation and variability across indicators.
#         - Highlight significant correlations between indicators and their possible implications.
#         - Important : Provide the **summary** not the codes or json 
#     """

#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             "http://localhost:11434/api/generate",
#             json={
#                 "model": "gemma3:270m",
#                 "prompt": context,
#                 "stream": False,
#                 "temperature": 0.5
#             },
#             timeout=300
#         )

#     if response.status_code != 200:
#         raise HTTPException(status_code=500, detail=f"Ollama request failed: {response.text}")
    
#     print(response.json(), '------------- GEN SUMMARY -------------')

#     return {"summary": response.json().get("response", "").strip()}

########################################################################################################
# === Static Summary Template ===

# === Templates ===
STATIC_SUMMARY_TEMPLATE = """
The data reveals key variations across the selected indicators:

{% for stat in stats_data %}
- **{{ stat['Indicator Name'] }}**
  - Lowest: {{ stat['Lowest Value'] }} in {{ stat['Lowest State'] }} (compared to national average {{ stat['National Average'] }})
  - Highest: {{ stat['Highest Value'] }} in {{ stat['Highest State'] }} (compared to national average {{ stat['National Average'] }})
{% endfor %}
"""

# === Indicator-Specific Vocabulary for Better Context ===
INDICATOR_VOCABULARY = {
    "BMI": {
        "keywords": ["nutrition", "malnutrition", "underweight", "obesity", "dietary habits", "food security"],
        "interventions": ["nutrition programs", "food supplementation", "dietary counseling", "ICDS strengthening"],
        "health_focus": "nutritional status and body mass index variations"
    },
    "overweight": {
        "keywords": ["obesity epidemic", "lifestyle diseases", "physical inactivity", "metabolic syndrome", "cardiovascular risk"],
        "interventions": ["lifestyle modification programs", "exercise promotion", "healthy diet campaigns", "weight management clinics"],
        "health_focus": "overweight and obesity prevalence"
    },
    "obese": {
        "keywords": ["obesity epidemic", "lifestyle diseases", "physical inactivity", "metabolic syndrome", "cardiovascular risk"],
        "interventions": ["lifestyle modification programs", "exercise promotion", "healthy diet campaigns", "weight management clinics"],
        "health_focus": "overweight and obesity prevalence"
    },
    "waist": {
        "keywords": ["metabolic risk", "abdominal obesity", "cardiovascular disease", "diabetes risk", "central adiposity"],
        "interventions": ["metabolic screening", "lifestyle counseling", "preventive healthcare", "diabetes prevention"],
        "health_focus": "metabolic complications and abdominal obesity"
    },
    "anemia": {
        "keywords": ["iron deficiency", "hemoglobin levels", "maternal health", "child nutrition", "micronutrient deficiency"],
        "interventions": ["iron supplementation", "fortified foods", "deworming programs", "prenatal care"],
        "health_focus": "anemia prevalence and iron deficiency"
    },
    "stunting": {
        "keywords": ["growth retardation", "chronic malnutrition", "child development", "height-for-age", "early childhood nutrition"],
        "interventions": ["nutrition programs", "growth monitoring", "maternal nutrition", "ICDS expansion"],
        "health_focus": "child growth and development indicators"
    },
    "wasting": {
        "keywords": ["acute malnutrition", "weight-for-height", "food insecurity", "child mortality", "severe malnutrition"],
        "interventions": ["therapeutic feeding", "emergency nutrition", "food security programs", "malnutrition treatment"],
        "health_focus": "acute malnutrition and wasting"
    }
}

def get_indicator_context(stats_data: list) -> dict:
    """Extract relevant vocabulary and context based on indicators."""
    all_keywords = set()
    all_interventions = set()
    health_focuses = []
    
    for stat in stats_data:
        indicator_name = stat.get("Indicator Name", "").lower()
        
        # Find matching vocabulary
        for key, context in INDICATOR_VOCABULARY.items():
            if key in indicator_name:
                all_keywords.update(context["keywords"])
                all_interventions.update(context["interventions"])
                health_focuses.append(context["health_focus"])
                break
        else:
            # Default health context
            all_keywords.update(["public health", "health outcomes", "healthcare access"])
            all_interventions.update(["health programs", "policy interventions"])
    
    return {
        "keywords": list(all_keywords)[:8],  # Limit to prevent prompt overload
        "interventions": list(all_interventions)[:6],
        "focus_areas": health_focuses[:3]
    }

# === Improved Summary Template for Gemma3:270m ===
IMPROVED_SUMMARY_TEMPLATE = """You are a health data analyst. Write a factual summary using the exact data provided below.

HEALTH DATA:
{{ static_summary }}

HEALTH CONTEXT: Focus on {{ health_focus }}. Use terms like: {{ keywords }}

TASK: Write exactly 3 paragraphs:

Paragraph 1 - Data Summary:
Write: "The analysis of {{ indicator_count }} health indicators reveals significant state-level variations." Then mention the specific lowest and highest performing states with their exact percentages from the data above.

Paragraph 2 - State Comparisons: 
Compare the performance gaps between states. Use phrases like "{{ comparison_phrases }}" and mention specific percentage differences.

Paragraph 3 - Policy Recommendations:
Suggest {{ interventions }} for addressing these health disparities. Focus on evidence-based interventions.

IMPORTANT RULES:
- Compare the lowest, highest values with National Average like (Jharkhand , achieved a 21.5 percent low birth weight rate, while the highest state, Meghalaya 78.8, achieved a high birth weight rate (as compared to **national average**))
- Use EXACT state names, indicator names and numbers from the data above
- Do NOT repeat the same sentence
- Do NOT use generic phrases like "consistent high values"
- Keep each paragraph focused on different aspects
- Use the health terminology provided

Write the summary:"""

# === Enhanced Preprocessing Function ===
def preprocess_stats(stats_data: list) -> list:
    """Clean and structure stats data for consistent usage."""
    processed = []
    for stat in stats_data:
        try:
            # Handle different input formats
            if isinstance(stat.get("Lowest"), str) and " (" in stat["Lowest"]:
                # Example format: "59.2 (Bihar)"
                lowest_val, lowest_state = stat["Lowest"].split(" (")
                highest_val, highest_state = stat["Highest"].split(" (")
                lowest_state = lowest_state.replace(")", "").strip()
                highest_state = highest_state.replace(")", "").strip()
            else:
                # Handle direct values
                lowest_val = str(stat.get("Lowest", "N/A"))
                highest_val = str(stat.get("Highest", "N/A"))
                lowest_state = stat.get("Lowest State", "Unknown")
                highest_state = stat.get("Highest State", "Unknown")

            processed.append({
                "Indicator Id": stat.get("Indicator Id", ""),
                "Indicator Name": stat.get("Indicator Name", "Health Indicator"),
                "Lowest Value": lowest_val.strip(),
                "Lowest State": lowest_state,
                "Highest Value": highest_val.strip(),
                "Highest State": highest_state,
                "National Average": stat.get("National Average", "N/A"),
                "Level": stat.get("Level", "")
            })
        except Exception as e:
            print(f"Error processing stat: {e}")
            # Keep raw stat if malformed with safe defaults
            processed.append({
                "Indicator Id": stat.get("Indicator Id", ""),
                "Indicator Name": stat.get("Indicator Name", "Health Indicator"),
                "Lowest Value": "N/A",
                "Lowest State": "Unknown",
                "Highest Value": "N/A", 
                "Highest State": "Unknown",
                "National Average": stat.get("National Average", "N/A"),
                "Level": stat.get("Level", "")
            })
    return processed

# === Static Summary Renderer ===
def generate_static_summary(stats_data: list) -> str:
    """Render a static summary from structured stats data."""
    template = Template(STATIC_SUMMARY_TEMPLATE)
    return template.render(stats_data=stats_data)

# === Enhanced Pattern Analysis Function ===
def analyze_cross_indicator_patterns(stats_data: list) -> str:
    """Analyze patterns across indicators to identify consistent performers."""
    state_performance = {}
    
    for stat in stats_data:
        low_state = stat.get("Lowest State", "Unknown")
        high_state = stat.get("Highest State", "Unknown")
        
        # Skip unknown states
        if low_state == "Unknown" or high_state == "Unknown":
            continue
            
        # Track states that appear frequently in lowest/highest
        if low_state in state_performance:
            state_performance[low_state]["lowest_count"] += 1
        else:
            state_performance[low_state] = {"lowest_count": 1, "highest_count": 0}
            
        if high_state in state_performance:
            state_performance[high_state]["highest_count"] += 1
        else:
            state_performance[high_state] = {"lowest_count": 0, "highest_count": 1}
    
    # Identify consistent performers (appearing in 2+ indicators)
    consistent_low = [state for state, counts in state_performance.items() 
                     if counts["lowest_count"] >= 2]
    consistent_high = [state for state, counts in state_performance.items() 
                      if counts["highest_count"] >= 2]
    
    pattern_summary = ""
    if consistent_low:
        pattern_summary += f"States consistently performing well: {', '.join(consistent_low)}. "
    if consistent_high:
        pattern_summary += f"States needing priority attention: {', '.join(consistent_high)}. "
    
    # Check for data anomalies
    national_averages = [stat.get("National Average", "N/A") for stat in stats_data]
    unique_averages = set(avg for avg in national_averages if avg != "N/A")
    
    if len(unique_averages) == 1:
        pattern_summary += f"Data quality note: All indicators show identical national average ({list(unique_averages)[0]}), requiring verification."
    
    return pattern_summary

# === Enhanced API Endpoint ===
@app.post("/indicator-summary")
async def generate_indicator_summary(
    data: IndicatorSelection,
    db: AsyncSession = Depends(get_session)
):
    try:
        # Step 1: Compute stats + correlations
        stats_data = await compute_indicator_stats(data, db)
        stats_data = preprocess_stats(stats_data)
        correlations = await compute_indicator_correlations(data, db)

        # Step 2: Create static summary
        static_summary = generate_static_summary(stats_data)
        
        # Step 3: Analyze cross-indicator patterns
        pattern_summary = analyze_cross_indicator_patterns(stats_data)
        
        # Step 4: Get indicator-specific context
        indicator_context = get_indicator_context(stats_data)

        # Step 5: Create optimized prompt for Gemma3:270m
        template = Template(IMPROVED_SUMMARY_TEMPLATE)
        context = template.render(
            static_summary=static_summary,
            health_focus=", ".join(indicator_context.get("focus_areas", ["health outcomes"])),
            keywords=", ".join(indicator_context["keywords"]),
            interventions=", ".join(indicator_context["interventions"]),
            indicator_count=len(stats_data),
            comparison_phrases="significant regional disparities, performance gaps, state-level variations"
        )

        print("=== OPTIMIZED PROMPT FOR GEMMA ===")
        print(context[:300] + "..." if len(context) > 300 else context)

        # Step 6: Call LLM API with optimized parameters for Gemma3:270m
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma3:4b",
                    "prompt": context,
                    "stream": False,
                    "temperature": 0.1,  # Very low for factual accuracy
                    "top_p": 0.7,        # More focused sampling
                    "repeat_penalty": 1.4,  # High penalty to prevent repetition
                    "num_predict": 350,     # Shorter for better quality with small model
                    "stop": ["Human:", "Assistant:", "Data:", "Task:", "Paragraph 4"],
                    "seed": 123  # For reproducible results during testing
                },
                timeout=300
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Ollama request failed: {response.text}"
            )

        generated_summary = response.json().get("response", "").strip()

        # Step 7: Enhanced post-processing
        validated_summary = enhanced_post_process_summary(
            generated_summary, 
            stats_data, 
            indicator_context,
            pattern_summary
        )

        print("=== RAW LLM OUTPUT ===")
        print(generated_summary)
        print("=== PROCESSED OUTPUT ===") 
        print(validated_summary)

        return {
            "summary": validated_summary,
            "raw_summary": generated_summary,
            "static_summary": static_summary,
            "patterns": pattern_summary,
            "stats_count": len(stats_data),
            "context_keywords": indicator_context["keywords"],
            "health_focus": indicator_context.get("focus_areas", [])
        }
        
    except Exception as e:
        print(f"Error in summary generation: {e}")
        # Enhanced fallback
        fallback_summary = create_enhanced_fallback_summary(
            stats_data if 'stats_data' in locals() else [], 
            indicator_context if 'indicator_context' in locals() else {}
        )
        return {
            "summary": fallback_summary,
            "error": str(e),
            "fallback_used": True
        }

# === Enhanced Post-processing ===
def enhanced_post_process_summary(summary: str, stats_data: list, context: dict, patterns: str) -> str:
    """Enhanced post-processing specifically for Gemma3:270m output issues."""
    
    # Remove repetitive content
    lines = summary.split('\n')
    unique_lines = []
    seen_content = set()
    
    for line in lines:
        line = line.strip()
        if line and line not in seen_content:
            # Skip lines with repetitive patterns
            if not ("consistent high values" in line.lower() or 
                   "high values for the highest" in line.lower() or
                   line.count("consistent") > 2):
                unique_lines.append(line)
                seen_content.add(line)
    
    cleaned_summary = '\n'.join(unique_lines)
    
    # Check if output quality is poor
    quality_indicators = [
        len(cleaned_summary) < 200,
        "consistent" in cleaned_summary and cleaned_summary.count("consistent") > 3,
        not any(stat["Lowest State"] in cleaned_summary for stat in stats_data if stat["Lowest State"] != "Unknown"),
        "high values for the highest values" in cleaned_summary.lower()
    ]
    
    # Use template fallback if quality is poor
    if sum(quality_indicators) >= 2:
        return create_template_based_summary(stats_data, context, patterns)
    
    # Add section headers if missing
    if "##" not in cleaned_summary:
        cleaned_summary = "## Health Indicators Analysis\n\n" + cleaned_summary
    
    # Supplement with missing data if needed
    if not any(stat["Lowest State"] in cleaned_summary for stat in stats_data[:2] if stat["Lowest State"] != "Unknown"):
        data_supplement = create_factual_data_summary(stats_data[:2])
        cleaned_summary = data_supplement + "\n\n" + cleaned_summary
    
    return cleaned_summary

def create_template_based_summary(stats_data: list, context: dict, patterns: str) -> str:
    """Create a template-based summary when LLM output is poor."""
    
    if not stats_data:
        return "## Health Indicators Analysis\n\nInsufficient data available for comprehensive analysis."
    
    summary_parts = ["## Health Indicators Summary: State vs National Comparison\n"]
    
    # Data analysis section
    keywords = context.get("keywords", ["health outcomes"])
    focus_areas = context.get("focus_areas", ["health indicators"])
    
    summary_parts.append(f"Analysis of {len(stats_data)} health indicators focusing on {focus_areas[0] if focus_areas else 'health outcomes'} reveals significant interstate variations.")
    
    # Add specific data points
    for i, stat in enumerate(stats_data[:3]):  # Limit to first 3
        if stat["Lowest State"] != "Unknown" and stat["Highest State"] != "Unknown":
            summary_parts.append(
                f"For {stat['Indicator Name']}, {stat['Lowest State']} shows the best performance "
                f"with {stat['Lowest Value']}%, while {stat['Highest State']} has the highest burden "
                f"at {stat['Highest Value']}% (national average: {stat['National Average']}%)."
            )
    
    # Pattern analysis
    if patterns:
        summary_parts.append(f"\n{patterns}")
    
    # Policy recommendations
    interventions = context.get("interventions", ["targeted health programs", "system strengthening"])
    
    summary_parts.append(f"\n## Policy Recommendations\n")
    summary_parts.append(
        f"Priority interventions should focus on {', '.join(interventions[:3])} in high-burden states. "
        f"This includes strengthening {keywords[0] if keywords else 'health systems'} and implementing "
        f"evidence-based programs to address regional disparities in {focus_areas[0] if focus_areas else 'health outcomes'}."
    )
    
    return "\n\n".join(summary_parts)

def create_factual_data_summary(stats_data: list) -> str:
    """Create factual data summary to supplement poor LLM output."""
    if not stats_data:
        return ""
    
    data_points = []
    for stat in stats_data:
        if stat["Lowest State"] != "Unknown" and stat["Highest State"] != "Unknown":
            data_points.append(
                f"**{stat['Indicator Name']}**: Best performing - {stat['Lowest State']} ({stat['Lowest Value']}%); "
                f"Needs attention - {stat['Highest State']} ({stat['Highest Value']}%)"
            )
    
    if data_points:
        return "### Key Findings:\n" + "\n".join(data_points)
    return ""

def create_enhanced_fallback_summary(stats_data: list, context: dict) -> str:
    """Ultimate fallback when everything fails."""
    keywords = context.get("keywords", ["health outcomes"])
    
    return f"""## Health Indicators Analysis

The analysis reveals significant variations in {keywords[0] if keywords else "health outcomes"} across Indian states. 
Regional disparities indicate the need for targeted policy interventions focusing on {", ".join(keywords[:3]) if keywords else "healthcare access, nutrition, and preventive care"}.

## Key Recommendations

**Immediate Actions:**
- Strengthen health monitoring systems in underperforming states
- Implement targeted {context.get("interventions", ["health programs"])[0] if context.get("interventions") else "nutrition programs"}
- Enhance data collection for accurate performance tracking

**Strategic Interventions:**
- Scale successful approaches from better-performing states
- Develop state-specific action plans based on identified health priorities
- Strengthen healthcare infrastructure in high-burden areas

Priority should be given to evidence-based interventions that address root causes of health disparities while building sustainable healthcare systems."""

# === Keep original function for backwards compatibility ===
def post_process_summary(summary: str, stats_data: list) -> str:
    """Legacy post-processing function - now calls enhanced version."""
    context = get_indicator_context(stats_data)
    patterns = analyze_cross_indicator_patterns(stats_data)
    return enhanced_post_process_summary(summary, stats_data, context, patterns)

# === Alternative Validation Function (keeping for backwards compatibility) ===
def validate_and_clean_summary(summary: str, stats_data: list) -> str:
    """Ensure LLM output aligns with correct statistics (legacy function)."""
    return post_process_summary(summary, stats_data)


##########################################################################################################

if __name__ == "__main__":
    uvicorn.run("fastapi_server:app", host="127.0.0.1", port=8000, reload=True)
