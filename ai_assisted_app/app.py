from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Load dataset (with model predictions)
DATASET_PATH = "dataset.csv"  # dataset should have a column 'model_output'
df = pd.read_csv(DATASET_PATH)
data = df.to_dict(orient='records')

# Output file (same as human-only, all responses in one file)
OUTPUT_FILE = "all_responses.csv"

@app.route('/')
def index():
    return render_template('index.html', data=data)

@app.route('/submit', methods=['POST'])
def submit():
    # Get participant name
    name = request.form.get('participant_name', '').strip()
    if not name:
        return "Error: Please enter your name before submitting."

    # Collect responses
    responses = []
    for i, item in enumerate(data):
        selected = request.form.get(f"response_{i}")
        if selected:
            responses.append({
                "participant_name": name,
                "text": item['text'],
                "selected_label": selected,
                "model_output": item.get('model_output', ''),
                "ground_truth": item.get('ground_truth', '')
            })

    # Convert to DataFrame
    result_df = pd.DataFrame(responses)

    # Append to CSV (or create if it doesn't exist)
    if os.path.exists(OUTPUT_FILE):
        result_df.to_csv(OUTPUT_FILE, mode='a', index=False, header=False)
    else:
        result_df.to_csv(OUTPUT_FILE, index=False)

    return f"✅ Thank you, {name}! Your responses have been saved."

if __name__ == '__main__':
    app.run(debug=True)
