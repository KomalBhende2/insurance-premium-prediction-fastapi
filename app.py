import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from schema.user_input import UserInput
from schema.prediction_response import PredictionResponse
from model.predict import predict_output, model, MODEL_VERSION

app = FastAPI(
    title="Insurance Premium Prediction API",
    description="Machine Learning API and Web Interface for Health Insurance Premium Prediction",
    version=MODEL_VERSION
)

# Enable CORS for local and cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount static directory if available
try:
    from fastapi.staticfiles import StaticFiles
    if os.path.exists(STATIC_DIR):
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
except Exception:
    pass

# Web UI and human readable home route
@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    accept = request.headers.get("accept", "")
    # If explicitly requested as JSON by an API client
    if "application/json" in accept and "text/html" not in accept:
        return JSONResponse({'message': 'Insurance Premium Prediction API'})

    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h2>Insurance Premium Prediction API</h2><p>Visit /docs for API documentation.</p>")

# Machine readable health check
@app.get('/health')
def health_check():
    return {
        'status': 'OK',
        'version': MODEL_VERSION,
        'model_loaded': model is not None
    }

@app.post('/predict', response_model=PredictionResponse)
def predict_premium(data: UserInput):

    user_input = {
        'bmi': data.bmi,
        'age_group': data.age_group,
        'lifestyle_risk': data.lifestyle_risk,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'occupation': data.occupation
    }

    try:

        prediction = predict_output(user_input)

        # Collect identified medical & lifestyle risk factors
        risk_factors = []
        if data.smoker:
            risk_factors.append("Tobacco / Smoking Habit")
        if data.bmi > 30:
            risk_factors.append(f"Obesity (BMI {round(data.bmi, 1)})")
        elif data.bmi > 27:
            risk_factors.append(f"Overweight (BMI {round(data.bmi, 1)})")
        if data.alcohol_habit == "frequent":
            risk_factors.append("Regular / Frequent Alcohol")
        elif data.alcohol_habit == "occasional":
            risk_factors.append("Occasional / Social Alcohol")
        if data.pre_existing_conditions:
            risk_factors.append("Chronic Pre-Existing Condition (e.g. Diabetes/BP)")
        if data.surgical_history:
            risk_factors.append("Recent Surgery / Hospitalization (Past 3 Years)")
        if data.family_medical_history:
            risk_factors.append("Family History of Critical Illness")

        prediction["risk_score"] = data.risk_score
        prediction["risk_factors"] = risk_factors
        prediction["lifestyle_risk"] = data.lifestyle_risk

        return JSONResponse(status_code=200, content={'response': prediction})
    
    except Exception as e:

        return JSONResponse(status_code=500, content=str(e))
