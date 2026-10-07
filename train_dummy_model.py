from sklearn.ensemble import RandomForestClassifier
import joblib
import numpy as np

print("Generating dummy training data for 30-feature vector schema...")
# Create random training data matching your 30 features (Class 0 = Safe, Class 1 = Threat)
X_train = np.random.rand(100, 30)
y_train = np.random.choice([0, 1], size=100, p=[0.8, 0.2])

print("Training baseline Random Forest classifier...")
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

# Save the model to the project root directory
model_filename = "model.joblib"
joblib.dump(model, model_filename)
print(f"[SUCCESS] Created and saved '{model_filename}' to your project root!")