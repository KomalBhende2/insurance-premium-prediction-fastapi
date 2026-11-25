from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Literal, Annotated
from config.city_tier import tier_1_cities, tier_2_cities


# pydantic model to validate incoming data
class UserInput(BaseModel):

    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the user')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the user in kg')]
    height: Annotated[float, Field(..., gt=0, lt=2.5, description='Height of the user in meters')]
    income_lpa: Annotated[float, Field(..., gt=0, description='Annual salary of the user in lpa')]
    smoker: Annotated[bool, Field(..., description='Is user a smoker / tobacco consumer')]
    city: Annotated[str, Field(..., description='The city that the user belongs to')]
    occupation: Annotated[Literal['retired', 'freelancer', 'student', 'government_job',
       'business_owner', 'unemployed', 'private_job'], Field(..., description='Occupation of the user')]
    
    # Extended Health & Medical Indicators (with backward-compatible defaults)
    alcohol_habit: Annotated[Literal['none', 'occasional', 'frequent'], Field(
        default='none', description='Alcohol consumption frequency'
    )] = 'none'
    pre_existing_conditions: Annotated[bool, Field(
        default=False, description='Any chronic medical conditions (e.g. Diabetes, Hypertension, Asthma)'
    )] = False
    surgical_history: Annotated[bool, Field(
        default=False, description='Major surgery or hospitalisation in past 3 years'
    )] = False
    family_medical_history: Annotated[bool, Field(
        default=False, description='Family hereditary history of early heart disease, stroke, or cancer'
    )] = False
    
    @field_validator('city')
    @classmethod
    def normalize_city(cls, v: str) -> str:
        v = v.strip().title()
        return v
    
    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight / (self.height ** 2)

    @computed_field
    @property
    def risk_score(self) -> float:
        score = 0.0
        # Tobacco impact
        if self.smoker:
            score += 2.0
        # BMI impact
        if self.bmi > 30:
            score += 2.0
        elif self.bmi > 27:
            score += 1.5
        # Alcohol consumption impact
        if self.alcohol_habit == 'frequent':
            score += 1.5
        elif self.alcohol_habit == 'occasional':
            score += 0.5
        # Pre-existing medical conditions
        if self.pre_existing_conditions:
            score += 2.0
        # Surgical history
        if self.surgical_history:
            score += 1.0
        # Family medical history
        if self.family_medical_history:
            score += 1.0
        return round(score, 1)
    
    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.risk_score >= 3.0:
            return "high"
        elif self.risk_score >= 1.5:
            return "medium"
        else:
            return "low"
        
    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "adult"
        elif self.age < 60:
            return "middle_aged"
        return "senior"
    
    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3
