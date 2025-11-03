from flask import Flask, render_template, request
import pandas as pd
import smtplib
from email.message import EmailMessage
import os
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

app = Flask(__name__)

# -----------------------------
# Load dataset
# -----------------------------
DATASET_PATH = "dataset.csv"
df = pd.read_csv(DATASET_PATH)
data = df.to_dict(orient='records')

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/submit', methods=['POST'])
def submit():
    participant_name = request.form.get('participant_name', '').strip()
    # participant_email = request.form.get('participant_email', '').strip()

    if not participant_name:
        return "Error: Please enter your name."

    responses = []
    for key in request.form:
        if key.startswith('response_'):
            index = key.split('_')[1]
            response = request.form.get(key)
            headline = request.form.get(f'headline_{index}')
            ground_truth = request.form.get(f'ground_truth_{index}')
            model_output = request.form.get(f'model_output_{index}')
            responses.append({
                'headline': headline,
                'response': response,
                'model_prediction': model_output,
                'ground_truth': ground_truth
            })
    doc_ref = db.collection('ai_assisted_responses').document(participant_name)
    doc_ref.set({
        'participant_name': participant_name,
        'responses': responses
    })

    return f"✅ Thank you {participant_name}! Your responses have been saved."


# -----------------------------
# Run app
# -----------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)