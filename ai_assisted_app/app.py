from flask import Flask, render_template, request
import pandas as pd
import smtplib
from email.message import EmailMessage
import os
import io

app = Flask(__name__)

# -----------------------------
# Load dataset
# -----------------------------
DATASET_PATH = "dataset.csv"
df = pd.read_csv(DATASET_PATH)
data = df.to_dict(orient='records')

# -----------------------------
# Email Configuration
# -----------------------------
EMAIL_ADDRESS = "amansonidps85@gmail.com"
EMAIL_PASSWORD = "xjzy qqfn jzrv oubp"  # Use App Password if using Gmail

def send_email_with_csv(subject, body_text, df_to_attach, to_address, csv_filename="data.csv"):
    """
    Sends an email with a pandas DataFrame attached as a CSV file.

    Args:
        subject (str): The subject line of the email.
        body_text (str): The plain text content for the email body.
        df_to_attach (pd.DataFrame): The pandas DataFrame to convert and attach.
        to_address (str): The recipient's email address.
        csv_filename (str, optional): The name for the attached CSV file. 
                                      Defaults to "data.csv".
    """
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_address
    
    # Set the plain text body
    msg.set_content(body_text)

    # --- Attach the DataFrame as a CSV ---
    if df_to_attach is not None and isinstance(df_to_attach, pd.DataFrame):
        # Create an in-memory string buffer
        with io.StringIO() as csv_buffer:
            # Write the DataFrame to the buffer as CSV (index=False to avoid saving row numbers)
            df_to_attach.to_csv(csv_buffer, index=False)
            
            # Get the CSV data as a string from the buffer
            csv_data = csv_buffer.getvalue()

        # Attach the CSV data to the email
        # We encode it to 'utf-8' as add_attachment expects bytes
        msg.add_attachment(
            csv_data.encode('utf-8'),
            maintype='text',
            subtype='csv',
            filename=csv_filename
        )
    # ----------------------------------------

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

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
    for i, item in enumerate(data):
        selected = request.form.get(f"response_{i}")
        if selected:
            responses.append({
                'Text': item['text'],
                'Selected Label': selected,
                'Ground Truth': item.get('ground_truth', ''),
                'AI Prediction': item.get('model_output')
            })

    df_responses = pd.DataFrame(responses)

    # Send email
    subject = f"Sarcasm Detection Responses - {participant_name} (AI Assisted)"
    body = f"Responses from participant: {participant_name}"
    send_email_with_csv(subject, body, df_responses, EMAIL_ADDRESS, csv_filename=f"{participant_name}_AI_assisted_resp.csv")

    return f"✅ Thank you {participant_name}! Your responses have been saved."


# -----------------------------
# Run app
# -----------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)