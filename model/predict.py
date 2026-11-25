import os
import pickle
import warnings
import pandas as pd
from sklearn.exceptions import InconsistentVersionWarning
import sklearn.compose._column_transformer as _ct

# Suppress version mismatch warnings during unpickling across scikit-learn versions
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

# Compatibility shim: scikit-learn >= 1.7 refactored internal _RemainderColsList
# which was present in <= 1.6.1 when model.pkl was serialized.
if not hasattr(_ct, "_RemainderColsList"):
    class _RemainderColsList(list):
        """Compatibility stub for unpickling ColumnTransformers saved in scikit-learn <= 1.6."""
        pass
    _ct._RemainderColsList = _RemainderColsList

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.pkl")

# import the ml model
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# MLFlow
MODEL_VERSION = "1.0.0"

# Get class labels from model (important for matching probabilities to class names)
class_labels = model.classes_.tolist()

def predict_output(user_input: dict):

    df = pd.DataFrame([user_input])

    # Predict the class
    predicted_class = model.predict(df)[0]

    # Get probabilities for all classes
    probabilities = model.predict_proba(df)[0]
    confidence = max(probabilities)
    
    # Create mapping: {class_name: probability} with native python floats for clean JSON serialization
    class_probs = {str(label): round(float(prob), 4) for label, prob in zip(class_labels, probabilities)}

    return {
        "predicted_category": str(predicted_class),
        "confidence": round(float(confidence), 4),
        "class_probabilities": class_probs
    }
