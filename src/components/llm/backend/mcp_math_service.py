# from fastapi import FastAPI, Request
# import numpy as np
# import pandas as pd

# app = FastAPI()

# ### stats compute API endpoint
# @app.post("/compute-stats")
# async def compute_stats(request: Request):
#     body = await request.json()
#     indicator_data = body.get("indicator_data", [])

#     stats = {}
#     df_map = {}

#     for entry in indicator_data:
#         if not isinstance(entry, dict):
#             continue

#         name = entry.get("indicator_name")
#         data = entry.get("data", []) or []
#         valid = [r for r in data if isinstance(r, dict) and r.get("Total") is not None]

#         if not name or not valid:
#             continue

#         values = [r["Total"] for r in valid if isinstance(r["Total"], (int, float))]
#         if not values:
#             continue

#         df_map[name] = values
#         stats[name] = {
#             "mean": float(np.mean(values)),
#             "min": float(np.min(values)),
#             "max": float(np.max(values)),
#             "std_dev": float(np.std(values))
#         }

#     correlation = {}
#     if df_map:
#         df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in df_map.items()]))
#         correlation = df.corr().to_dict()

#     return {"stats": stats, "correlation": correlation}


#########################################################################################################

from fastapi import FastAPI, Request
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import json

app = FastAPI()

class StatisticalSignificance(Enum):
    VERY_HIGH = 0.8
    HIGH = 0.6
    MODERATE = 0.4
    LOW = 0.2

@dataclass
class EnhancedStats:
    """Enhanced statistical measures for better insights"""
    mean: float
    median: float
    min: float
    max: float
    std_dev: float
    coefficient_of_variation: float
    q25: float  # 25th percentile
    q75: float  # 75th percentile
    range_span: float
    outlier_count: int
    variability_level: str

@dataclass
class CorrelationAnalysis:
    """Detailed correlation analysis"""
    correlation_coefficient: float
    strength_category: str
    significance_level: str
    relationship_type: str  # positive/negative/neutral

@dataclass
class ComparativeAnalysis:
    """Comparative analysis between indicators"""
    performance_ranking: List[Dict[str, Any]]
    variability_ranking: List[Dict[str, Any]]
    regional_patterns: Dict[str, Any]

class EnhancedStatsCalculator:
    """Enhanced statistical calculator with comprehensive analysis"""
    
    def __init__(self):
        self.significance_thresholds = {
            'very_high': 0.8,
            'high': 0.6,
            'moderate': 0.4,
            'low': 0.2
        }
    
    def calculate_enhanced_stats(self, values: List[float], name: str) -> EnhancedStats:
        """Calculate comprehensive statistics for an indicator"""
        if not values:
            return None
            
        values_array = np.array(values)
        
        # Basic statistics
        mean_val = float(np.mean(values_array))
        median_val = float(np.median(values_array))
        min_val = float(np.min(values_array))
        max_val = float(np.max(values_array))
        std_dev = float(np.std(values_array))
        
        # Advanced statistics
        q25 = float(np.percentile(values_array, 25))
        q75 = float(np.percentile(values_array, 75))
        cv = (std_dev / mean_val * 100) if mean_val != 0 else 0
        range_span = max_val - min_val
        
        # Outlier detection using IQR method
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        outliers = values_array[(values_array < lower_bound) | (values_array > upper_bound)]
        outlier_count = len(outliers)
        
        # Variability classification
        variability_level = self._classify_variability(cv)
        
        return EnhancedStats(
            mean=mean_val,
            median=median_val,
            min=min_val,
            max=max_val,
            std_dev=std_dev,
            coefficient_of_variation=cv,
            q25=q25,
            q75=q75,
            range_span=range_span,
            outlier_count=outlier_count,
            variability_level=variability_level
        )
    
    def _classify_variability(self, cv: float) -> str:
        """Classify variability based on coefficient of variation"""
        if cv >= 20:
            return "very_high"
        elif cv >= 15:
            return "high"
        elif cv >= 10:
            return "moderate"
        elif cv >= 5:
            return "low"
        else:
            return "very_low"
    
    def analyze_correlation(self, corr_value: float, 
                          indicator1: str, indicator2: str) -> CorrelationAnalysis:
        """Analyze correlation with detailed categorization"""
        abs_corr = abs(corr_value)
        
        # Strength classification
        if abs_corr >= 0.8:
            strength = "very_strong"
        elif abs_corr >= 0.6:
            strength = "strong"
        elif abs_corr >= 0.4:
            strength = "moderate"
        elif abs_corr >= 0.2:
            strength = "weak"
        else:
            strength = "negligible"
        
        # Significance level
        if abs_corr >= 0.7:
            significance = "high"
        elif abs_corr >= 0.5:
            significance = "moderate"
        elif abs_corr >= 0.3:
            significance = "low"
        else:
            significance = "not_significant"
        
        # Relationship type
        if corr_value > 0.1:
            relationship = "positive"
        elif corr_value < -0.1:
            relationship = "negative"
        else:
            relationship = "neutral"
        
        return CorrelationAnalysis(
            correlation_coefficient=corr_value,
            strength_category=strength,
            significance_level=significance,
            relationship_type=relationship
        )
    
    def generate_comparative_analysis(self, enhanced_stats: Dict[str, EnhancedStats]) -> ComparativeAnalysis:
        """Generate comparative analysis across indicators"""
        if not enhanced_stats:
            return ComparativeAnalysis([], [], {})
        
        # Performance ranking (by mean)
        performance_ranking = []
        for name, stats in enhanced_stats.items():
            performance_ranking.append({
                "indicator": name,
                "mean": stats.mean,
                "median": stats.median,
                "performance_tier": self._classify_performance(stats.mean)
            })
        performance_ranking.sort(key=lambda x: x["mean"], reverse=True)
        
        # Variability ranking
        variability_ranking = []
        for name, stats in enhanced_stats.items():
            variability_ranking.append({
                "indicator": name,
                "coefficient_of_variation": stats.coefficient_of_variation,
                "variability_level": stats.variability_level,
                "outlier_count": stats.outlier_count
            })
        variability_ranking.sort(key=lambda x: x["coefficient_of_variation"], reverse=True)
        
        # Regional patterns analysis
        regional_patterns = self._analyze_regional_patterns(enhanced_stats)
        
        return ComparativeAnalysis(
            performance_ranking=performance_ranking,
            variability_ranking=variability_ranking,
            regional_patterns=regional_patterns
        )
    
    def _classify_performance(self, mean_value: float) -> str:
        """Classify performance tier"""
        if mean_value >= 80:
            return "excellent"
        elif mean_value >= 60:
            return "good"
        elif mean_value >= 40:
            return "moderate"
        elif mean_value >= 20:
            return "poor"
        else:
            return "very_poor"
    
    def _analyze_regional_patterns(self, enhanced_stats: Dict[str, EnhancedStats]) -> Dict[str, Any]:
        """Analyze patterns across regions"""
        if not enhanced_stats:
            return {}
        
        # Calculate overall statistics
        all_means = [stats.mean for stats in enhanced_stats.values()]
        all_cvs = [stats.coefficient_of_variation for stats in enhanced_stats.values()]
        
        return {
            "overall_mean_range": {
                "min": min(all_means),
                "max": max(all_means),
                "span": max(all_means) - min(all_means)
            },
            "variability_overview": {
                "most_variable": max(all_cvs),
                "least_variable": min(all_cvs),
                "average_cv": np.mean(all_cvs)
            },
            "performance_distribution": {
                "high_performers": len([m for m in all_means if m >= 70]),
                "moderate_performers": len([m for m in all_means if 40 <= m < 70]),
                "low_performers": len([m for m in all_means if m < 40])
            }
        }

### Enhanced API endpoint
@app.post("/compute-enhanced-stats")
async def compute_enhanced_stats(request: Request):
    """Enhanced statistics computation with comprehensive analysis"""
    body = await request.json()
    indicator_data = body.get("indicator_data", [])
    
    calculator = EnhancedStatsCalculator()
    
    # Enhanced statistics for each indicator
    enhanced_stats = {}
    raw_data_map = {}
    
    for entry in indicator_data:
        if not isinstance(entry, dict):
            continue
        
        name = entry.get("indicator_name")
        data = entry.get("data", []) or []
        valid = [r for r in data if isinstance(r, dict) and r.get("Total") is not None]
        
        if not name or not valid:
            continue
        
        values = [r["Total"] for r in valid if isinstance(r["Total"], (int, float))]
        if not values:
            continue
        
        raw_data_map[name] = values
        enhanced_stats[name] = calculator.calculate_enhanced_stats(values, name)
    
    # Enhanced correlation analysis
    enhanced_correlations = {}
    basic_correlations = {}
    
    if raw_data_map:
        # Create DataFrame for correlation calculation
        df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in raw_data_map.items()]))
        correlation_matrix = df.corr()
        basic_correlations = correlation_matrix.to_dict()
        
        # Enhanced correlation analysis
        indicators = list(raw_data_map.keys())
        for i, indicator1 in enumerate(indicators):
            enhanced_correlations[indicator1] = {}
            for j, indicator2 in enumerate(indicators):
                corr_value = correlation_matrix.loc[indicator1, indicator2]
                if i != j:  # Skip self-correlation
                    analysis = calculator.analyze_correlation(corr_value, indicator1, indicator2)
                    enhanced_correlations[indicator1][indicator2] = asdict(analysis)
                else:
                    enhanced_correlations[indicator1][indicator2] = {
                        "correlation_coefficient": 1.0,
                        "strength_category": "perfect",
                        "significance_level": "self",
                        "relationship_type": "self"
                    }
    
    # Generate comparative analysis
    comparative_analysis = calculator.generate_comparative_analysis(enhanced_stats)
    
    # Convert enhanced stats to serializable format
    serializable_stats = {}
    for name, stats in enhanced_stats.items():
        if stats:
            serializable_stats[name] = asdict(stats)
    
    # Prepare response with enhanced structure
    response = {
        "basic_stats": {name: {
            "mean": stats.mean,
            "min": stats.min,
            "max": stats.max,
            "std_dev": stats.std_dev
        } for name, stats in enhanced_stats.items() if stats},
        
        "enhanced_stats": serializable_stats,
        
        "basic_correlation": basic_correlations,
        
        "enhanced_correlation": enhanced_correlations,
        
        "comparative_analysis": asdict(comparative_analysis),
        
        "metadata": {
            "indicator_count": len(enhanced_stats),
            "total_data_points": sum(len(values) for values in raw_data_map.values()),
            "analysis_type": "comprehensive",
            "calculation_method": "enhanced_statistical_analysis"
        },
        
        "summary": {
            "highest_performing": comparative_analysis.performance_ranking[0] if comparative_analysis.performance_ranking else None,
            "most_variable": comparative_analysis.variability_ranking[0] if comparative_analysis.variability_ranking else None,
            "significant_correlations": len([
                corr for indicator_corrs in enhanced_correlations.values()
                for corr in indicator_corrs.values()
                if corr.get("significance_level") in ["high", "moderate"]
            ]) // 2  # Divide by 2 to avoid double counting
        }
    }
    
    return response

### Backward compatibility endpoint
@app.post("/compute-stats")
async def compute_stats(request: Request):
    """Backward compatible endpoint that maintains existing structure"""
    # Get enhanced analysis
    enhanced_response = await compute_enhanced_stats(request)
    
    # Return in original format for compatibility
    return {
        "stats": enhanced_response["basic_stats"],
        "correlation": enhanced_response["basic_correlation"],
        
        # Add enhanced data for new features
        "_enhanced": {
            "enhanced_stats": enhanced_response["enhanced_stats"],
            "enhanced_correlation": enhanced_response["enhanced_correlation"],
            "comparative_analysis": enhanced_response["comparative_analysis"],
            "metadata": enhanced_response["metadata"],
            "summary": enhanced_response["summary"]
        }
    }
