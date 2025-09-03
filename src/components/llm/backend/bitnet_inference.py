# import re
# import os
# import subprocess
# import json
# import httpx
# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse

# app = FastAPI()

# ### === Prompt builder codes ===
# def build_instruction_from_table(indicator_data):
#     formatted_rows = []
#     for entry in indicator_data:
#         if not isinstance(entry, dict):
#             continue
#         name = entry.get("indicator_name")
#         data = entry.get("data", []) or []
#         valid = [r for r in data if r.get("Total") is not None]
#         if not name or not valid:
#             continue

#         sample = valid[:6]
#         key = "state_name" if "state_name" in sample[0] else "district_name"
#         snippet = ", ".join(f"{r[key]} ({r['Total']}%)" for r in sample)
#         formatted_rows.append(f"- {name}: {snippet}")

#     if not formatted_rows:
#         raise ValueError("No valid indicators with Total data found.")

#     return (
#         "Below are several indicators measured\n"
#         "as percentages across the same set of regions:\n\n"
#         f"{chr(10).join(formatted_rows)}\n\n"
#         "Generate a clear, concise narrative comparing these indicators based on the pre-computed statistics."
#     )

# # === Call MCP math service ===
# async def get_stats_from_mcp(indicator_data):
#     try:
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.post("http://localhost:8001/compute-stats", json={"indicator_data": indicator_data})
#             response.raise_for_status()
#             return response.json()
#     except Exception as e:
#         print(f"[Warning] MCP service failed: {e}")
#         return {"stats": {}, "correlation": {}}

# # === Gemini insight generation ===
# def generate_stat_summary(
#     instruction: str,
#     max_tokens: int = 500,
#     verbose: bool = True
# ) -> str:
#     prompt = (
#         "ONLY output a clear markdown report.\n"
#         "Do NOT explain your reasoning, do NOT write 'Thinking...'.\n"
#         "Use this format:\n"
#         "## Indicator Summary\n"
#         "- Key stats for each indicator\n\n"
#         "## Variability\n"
#         "- Indicators with the most variability\n\n"
#         "## Correlations\n"
#         "- Strong positive or negative correlations\n\n"
#         "Now, analyze:\n\n" + instruction
#     )

#     try:
#         result = subprocess.run(
#             ["ollama", "run", "gemma3:270m"],
#             input=prompt,
#             text=True,
#             capture_output=True,
#             encoding="utf-8",
#             errors="ignore"
#         )

#         if verbose:
#             print("DEBUG: Gemini raw output:", result.stdout)
#             print("DEBUG: Gemini stderr:", result.stderr)

#         response = result.stdout.strip()

#         ## If regex matches, extract key content, otherwise keep full response
#         match = re.search(r"(?:##|1\.)[\s\S]+", response, re.IGNORECASE)
#         if match:
#             response = match.group(0)
#         elif not response:
#             response = "No insights generated."

#         print(response, '***************************')

#     except Exception as e:
#         print(f"Error calling the LLM Model: {e}")
#         response = "Error generating insights!."

#     return response.strip()

# # === Helper function to format summary in Markdown ===
# def format_summary_markdown(summary: str) -> str:
#     # Here we can add more formatting rules if needed
#     formatted_summary = (
#         "# AI Insights Summary\n\n"
#         + summary.replace("\n", "\n\n")  # Ensure double line breaks for paragraphs
#     )
#     return formatted_summary


############################################################################################

import re
import os
import subprocess
import json
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

### === Prompt builder codes === (Original function maintained)
def build_instruction_from_table(indicator_data):
    formatted_rows = []
    for entry in indicator_data:
        if not isinstance(entry, dict):
            continue
        name = entry.get("indicator_name")
        data = entry.get("data", []) or []
        valid = [r for r in data if r.get("Total") is not None]
        if not name or not valid:
            continue

        sample = valid[:6]
        key = "state_name" if "state_name" in sample[0] else "district_name"
        snippet = ", ".join(f"{r[key]} ({r['Total']}%)" for r in sample)
        formatted_rows.append(f"- {name}: {snippet}")

    if not formatted_rows:
        raise ValueError("No valid indicators with Total data found.")

    return (
        "Below are several indicators measured\n"
        "as percentages across the same set of regions:\n\n"
        f"{chr(10).join(formatted_rows)}\n\n"
        "Generate a clear, concise narrative comparing these indicators based on the pre-computed statistics."
    )

# === Call MCP math service === (Original function maintained)
async def get_stats_from_mcp(indicator_data):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("http://localhost:8001/compute-stats", json={"indicator_data": indicator_data})
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"[Warning] MCP service failed: {e}")
        return {"stats": {}, "correlation": {}}

# === Gemini insight generation === (FIXED - this was the missing function)
def generate_stat_summary(
    instruction: str,
    max_tokens: int = 500,
    verbose: bool = True
) -> str:
    prompt = (
        "ONLY output a clear markdown report.\n"
        "Do NOT explain your reasoning, do NOT write 'Thinking...'.\n"
        "Use this format:\n"
        "## Indicator Summary\n"
        "- Key stats for each indicator\n\n"
        "## Variability\n"
        "- Indicators with the most variability\n\n"
        "## Correlations\n"
        "- Strong positive or negative correlations\n\n"
        "Now, analyze:\n\n" + instruction
    )

    try:
        result = subprocess.run(
            ["ollama", "run", "gemma3:270m"],
            input=prompt,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="ignore"
        )

        if verbose:
            print("DEBUG: Gemini raw output:", result.stdout)
            print("DEBUG: Gemini stderr:", result.stderr)

        response = result.stdout.strip()

        ## If regex matches, extract key content, otherwise keep full response
        match = re.search(r"(?:##|1\.)[\s\S]+", response, re.IGNORECASE)
        if match:
            response = match.group(0)
        elif not response:
            response = "No insights generated."

        print(response, '***************************')

    except Exception as e:
        print(f"Error calling the LLM Model: {e}")
        response = "Error generating insights!."

    return response.strip()

# === Helper function to format summary in Markdown === (Original function maintained)
def format_summary_markdown(summary: str) -> str:
    # Here we can add more formatting rules if needed
    formatted_summary = (
        "# AI Insights Summary\n\n"
        + summary.replace("\n", "\n\n")  # Ensure double line breaks for paragraphs
    )
    return formatted_summary

# === ENHANCED STANDARDIZED FUNCTIONS (NEW) ===

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class CorrelationStrength(Enum):
    VERY_STRONG = 0.8
    STRONG = 0.6
    MODERATE = 0.4
    WEAK = 0.2

class VariabilityLevel(Enum):
    VERY_HIGH = 20.0
    HIGH = 15.0
    MODERATE = 10.0
    LOW = 5.0

@dataclass
class InsightTemplate:
    """Standardized template for generating insights"""
    stats_template: str
    variability_template: str
    correlation_template: str
    summary_template: str

class StandardizedInsightGenerator:
    def __init__(self):
        self.insight_template = InsightTemplate(
            stats_template="""
## Key Statistics Summary
{stats_summary}

**Performance Ranges:**
{performance_ranges}
""",
            variability_template="""
## Variability Analysis
{variability_analysis}

**Most Variable Indicators:**
{most_variable}
""",
            correlation_template="""
## Correlation Insights
{correlation_summary}

**Notable Relationships:**
{relationships}
""",
            summary_template="""
## Executive Summary
{executive_summary}

**Key Findings:**
{key_findings}
"""
        )
    
    def classify_correlation_strength(self, correlation: float) -> str:
        """Classify correlation strength with consistent messaging"""
        abs_corr = abs(correlation)
        direction = "positive" if correlation > 0 else "negative"
        
        if abs_corr >= CorrelationStrength.VERY_STRONG.value:
            return f"very strong {direction}"
        elif abs_corr >= CorrelationStrength.STRONG.value:
            return f"strong {direction}"
        elif abs_corr >= CorrelationStrength.MODERATE.value:
            return f"moderate {direction}"
        elif abs_corr >= CorrelationStrength.WEAK.value:
            return f"weak {direction}"
        else:
            return "negligible"
    
    def classify_variability(self, std_dev: float, mean: float) -> str:
        """Classify variability level with coefficient of variation"""
        if mean == 0:
            return "undefined"
        
        cv = (std_dev / mean) * 100  # Coefficient of variation
        
        if cv >= VariabilityLevel.VERY_HIGH.value:
            return "very high"
        elif cv >= VariabilityLevel.HIGH.value:
            return "high"
        elif cv >= VariabilityLevel.MODERATE.value:
            return "moderate"
        else:
            return "low"
    
    def generate_stats_summary(self, stats: Dict[str, Dict]) -> str:
        """Generate standardized statistics summary"""
        if not stats:
            return "No statistical data available."
        
        summary_parts = []
        performance_parts = []
        
        # Sort indicators by mean value for consistent ordering
        sorted_indicators = sorted(stats.items(), key=lambda x: x[1]['mean'], reverse=True)
        
        for name, data in sorted_indicators:
            mean_val = data['mean']
            min_val = data['min']
            max_val = data['max']
            std_dev = data['std_dev']
            
            # Standardized summary format
            summary_parts.append(
                f"- **{name}**: Average {mean_val:.1f}% (±{std_dev:.1f}%)"
            )
            
            # Performance range analysis
            range_span = max_val - min_val
            variability = self.classify_variability(std_dev, mean_val)
            
            performance_parts.append(
                f"- **{name}**: Range {min_val:.1f}%-{max_val:.1f}% (span: {range_span:.1f}%, variability: {variability})"
            )
        
        return {
            'stats_summary': '\n'.join(summary_parts),
            'performance_ranges': '\n'.join(performance_parts)
        }
    
    def generate_variability_analysis(self, stats: Dict[str, Dict]) -> str:
        """Generate standardized variability analysis"""
        if not stats:
            return "No variability data available."
        
        # Calculate coefficient of variation for each indicator
        variability_data = []
        for name, data in stats.items():
            mean_val = data['mean']
            std_dev = data['std_dev']
            cv = (std_dev / mean_val * 100) if mean_val != 0 else 0
            variability_data.append((name, cv, std_dev, self.classify_variability(std_dev, mean_val)))
        
        # Sort by coefficient of variation
        variability_data.sort(key=lambda x: x[1], reverse=True)
        
        # Generate analysis
        analysis_parts = []
        most_variable_parts = []
        
        if variability_data:
            highest_cv = variability_data[0][1]
            lowest_cv = variability_data[-1][1]
            
            analysis_parts.append(
                f"Variability across indicators ranges from {lowest_cv:.1f}% to {highest_cv:.1f}% "
                f"(coefficient of variation)."
            )
            
            # Highlight top 3 most variable
            for i, (name, cv, std_dev, level) in enumerate(variability_data[:3]):
                most_variable_parts.append(
                    f"{i+1}. **{name}**: {cv:.1f}% CV ({level} variability)"
                )
        
        return {
            'variability_analysis': ' '.join(analysis_parts),
            'most_variable': '\n'.join(most_variable_parts)
        }
    
    def generate_correlation_analysis(self, correlation: Dict[str, Dict]) -> str:
        """Generate standardized correlation analysis"""
        if not correlation:
            return "No correlation data available."
        
        correlations = []
        
        # Extract unique correlations (avoid duplicates)
        indicators = list(correlation.keys())
        for i, indicator1 in enumerate(indicators):
            for j, indicator2 in enumerate(indicators[i+1:], i+1):
                corr_value = correlation[indicator1].get(indicator2, 0)
                if abs(corr_value) > 0.1:  # Only include meaningful correlations
                    correlations.append((indicator1, indicator2, corr_value))
        
        # Sort by absolute correlation strength
        correlations.sort(key=lambda x: abs(x[2]), reverse=True)
        
        summary_parts = []
        relationships_parts = []
        
        if correlations:
            strongest_corr = abs(correlations[0][2])
            summary_parts.append(
                f"Analysis reveals {len(correlations)} notable correlations between indicators, "
                f"with the strongest relationship showing {strongest_corr:.2f} correlation coefficient."
            )
            
            # Highlight top correlations
            for i, (ind1, ind2, corr_val) in enumerate(correlations[:5]):  # Top 5
                strength = self.classify_correlation_strength(corr_val)
                relationships_parts.append(
                    f"{i+1}. **{ind1}** ↔ **{ind2}**: {strength} correlation ({corr_val:.2f})"
                )
        else:
            summary_parts.append("No significant correlations detected between indicators.")
        
        return {
            'correlation_summary': ' '.join(summary_parts),
            'relationships': '\n'.join(relationships_parts)
        }
    
    def generate_executive_summary(self, stats: Dict[str, Dict], correlation: Dict[str, Dict]) -> str:
        """Generate standardized executive summary"""
        if not stats:
            return "Insufficient data for comprehensive analysis."
        
        num_indicators = len(stats)
        
        # Find highest and lowest performing indicators
        sorted_by_mean = sorted(stats.items(), key=lambda x: x[1]['mean'], reverse=True)
        highest_performer = sorted_by_mean[0]
        lowest_performer = sorted_by_mean[-1]
        
        # Find most variable indicator
        variability_data = [(name, data['std_dev']/data['mean']*100) 
                           for name, data in stats.items() if data['mean'] != 0]
        most_variable = max(variability_data, key=lambda x: x[1]) if variability_data else None
        
        # Count significant correlations
        significant_correlations = 0
        if correlation:
            indicators = list(correlation.keys())
            for i, indicator1 in enumerate(indicators):
                for indicator2 in indicators[i+1:]:
                    if abs(correlation[indicator1].get(indicator2, 0)) > 0.4:
                        significant_correlations += 1
        
        summary_parts = []
        key_findings_parts = []
        
        summary_parts.append(
            f"Analysis of {num_indicators} indicators reveals varying performance patterns "
            f"across regions, with {significant_correlations} significant inter-indicator relationships."
        )
        
        # Key findings
        key_findings_parts.extend([
            f"**Highest Performance**: {highest_performer[0]} (avg: {highest_performer[1]['mean']:.1f}%)",
            f"**Lowest Performance**: {lowest_performer[0]} (avg: {lowest_performer[1]['mean']:.1f}%)",
        ])
        
        if most_variable:
            key_findings_parts.append(
                f"**Most Variable**: {most_variable[0]} (CV: {most_variable[1]:.1f}%)"
            )
        
        if significant_correlations > 0:
            key_findings_parts.append(
                f"**Correlations**: {significant_correlations} significant relationships identified"
            )
        
        return {
            'executive_summary': ' '.join(summary_parts),
            'key_findings': '\n'.join(key_findings_parts)
        }
    
    def build_standardized_instruction(self, mcp_result: Dict[str, Any], 
                                     indicator_names: List[str],
                                     region_type: str = "regions") -> str:
        """Build standardized instruction from MCP result"""
        stats = mcp_result.get('stats', {})
        correlation = mcp_result.get('correlation', {})
        
        # Generate all standardized sections
        stats_data = self.generate_stats_summary(stats)
        variability_data = self.generate_variability_analysis(stats)
        correlation_data = self.generate_correlation_analysis(correlation)
        summary_data = self.generate_executive_summary(stats, correlation)
        
        # Build final instruction
        instruction = f"""
# Statistical Analysis Report

You are analyzing {len(indicator_names)} indicators across multiple {region_type}. 
Generate insights using the following standardized structure:

{self.insight_template.stats_template.format(**stats_data)}

{self.insight_template.variability_template.format(**variability_data)}

{self.insight_template.correlation_template.format(**correlation_data)}

{self.insight_template.summary_template.format(**summary_data)}

**Instructions for AI Model:**
1. Use ONLY the provided statistical data
2. Follow the exact markdown structure shown above
3. Keep language objective and data-driven
4. Include specific numerical values where provided
5. Do not add speculative interpretations
6. Maximum response length: 400 words
7. Use bullet points for key findings only
"""
        return instruction

# === NEW ENHANCED FUNCTIONS ===
def generate_standardized_insights(instruction: str, max_tokens: int = 400) -> str:
    """Generate insights with consistent formatting and error handling"""
    
    # Enhanced prompt with strict formatting requirements
    prompt = f"""
        CRITICAL INSTRUCTIONS:
        - Output ONLY markdown formatted analysis
        - Follow the EXACT structure provided in the instruction
        - Do NOT add explanations, thinking process, or meta-commentary
        - Use specific numerical values from the data
        - Keep response under {max_tokens} words
        - Start immediately with "# Statistical Analysis Report"

        {instruction}
    """
    
    try:
        result = subprocess.run(
            ["ollama", "run", "gemma3:270m"],
            input=prompt,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30  # Add timeout for reliability
        )
        
        if result.returncode != 0:
            print(f"WARNING: Ollama process failed with code {result.returncode}")
            return generate_fallback_insights(instruction)
        
        response = result.stdout.strip()
        
        # Validate and clean response
        if not response or len(response) < 50:
            print("WARNING: Insufficient response from model")
            return generate_fallback_insights(instruction)
        
        # Extract markdown content
        if "# Statistical Analysis Report" in response:
            response = response[response.find("# Statistical Analysis Report"):]
        elif "##" in response:
            response = response[response.find("##"):]
        
        return response
        
    except subprocess.TimeoutExpired:
        print("ERROR: Model generation timed out")
        return generate_fallback_insights(instruction)
    except Exception as e:
        print(f"ERROR: Model generation failed - {e}")
        return generate_fallback_insights(instruction)

def generate_fallback_insights(instruction: str) -> str:
    """Generate basic insights when AI model fails"""
    return """
                # Statistical Analysis Report

                ## Key Statistics Summary
                Analysis completed using available data. Detailed insights require model processing.

                ## Variability Analysis  
                Regional variations identified across indicators.

                ## Correlation Insights
                Relationship patterns detected between indicators.

                ## Executive Summary
                Statistical analysis provides foundation for data-driven insights.
            """

# === NEW ENHANCED INSTRUCTION BUILDER ===
def build_standardized_instruction_from_table(indicator_data, region_type="regions"):
    """Enhanced version of build_instruction_from_table with standardization"""
    generator = StandardizedInsightGenerator()
    
    # Get MCP data
    import asyncio
    mcp_result = asyncio.run(get_stats_from_mcp(indicator_data))
    
    indicator_names = [entry.get("indicator_name", "") 
                      for entry in indicator_data 
                      if isinstance(entry, dict)]
    
    return generator.build_standardized_instruction(mcp_result, indicator_names, region_type)