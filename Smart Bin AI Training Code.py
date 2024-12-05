from sklearn.ensemble import RandomForestClassifier
import joblib

# Example training data: moisture levels and corresponding waste types
# X_train: Moisture levels (input feature)
# y_train: Waste types (target labels)

X_train = [[10], [0], [55], [75], [30], [60]]  # Moisture levels
y_train = ['Organic', 'Inorganic', 'Organic', 'Organic', 'Inorganic', 'Organic']  # Waste type labels

# Store the unique moisture levels used during training
trained_moisture_levels = set([x[0] for x in X_train])

# Initialize and train the classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the trained model and the list of trained moisture levels
joblib.dump((model, trained_moisture_levels), 'waste_classifier_model.pkl')

# Output the trained moisture levels for reference
print("Trained on the following moisture levels:", trained_moisture_levels)