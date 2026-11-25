from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class PredictionResponse(BaseModel):
    predicted_category: str = Field(
        ...,
        description="The predicted insurance premium category",
        example="High"
    )
    confidence: float = Field(
        ...,
        description="Model's confidence score for the predicted class (range: 0 to 1)",
        example=0.8432
    )
    class_probabilities: Dict[str, float] = Field(
        ...,
        description="Probability distribution across all possible classes",
        example={"Low": 0.01, "Medium": 0.15, "High": 0.84}
    )
    risk_score: Optional[float] = Field(
        default=None,
        description="Calculated cumulative health & lifestyle risk score",
        example=3.5
    )
    risk_factors: Optional[List[str]] = Field(
        default=None,
        description="Identified medical and lifestyle risk factors influencing underwriting",
        example=["Tobacco / Smoking", "Pre-Existing Medical Conditions"]
    )
