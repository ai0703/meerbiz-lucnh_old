import csv  # To read from and write to CSV files.
import datetime  # For handling dates and times.
import json  # To encode and decode JSON data.
import random  # To generate random numbers, for delays perhaps.
import requests  # To make HTTP requests to external APIs or webhooks.
import time  # For handling time-related tasks, like sleeping.
import threading  # To run tasks in separate threads.
import os  # To interact with the operating system, like accessing environment variables.
from flask import Flask, request, jsonify  # Core Flask imports for web app development.

app = Flask(__name__)
def send_data_to_webhook(first_name, last_name, email, linkedin_profile, company_name, webhook_url, session_cookies, user_agent):
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "linkedin_profile": linkedin_profile,
        "company_name": company_name,
        "session_cookies": session_cookies,
        "User-Agent": user_agent
    }

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(webhook_url, json=data, headers=headers)  # Changed data=json.dumps(data) to json=data
        if response.status_code == 200:
            print(f"Data sent successfully to the webhook. LinkedIn Profile: {linkedin_profile}")
        else:
            print(f"Failed to send data to the webhook. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while sending data to the webhook: {e}")

def wait_until_next_window(current_time):
    # If before 8 AM, wait until 8 AM
    if current_time.hour < 8:
        wait_time = ((7 - current_time.hour) * 60 + (60 - current_time.minute)) * 60
    # If after 5 PM, wait until 8 AM next day
    elif current_time.hour >= 17:  # Changed the condition to use elif for clarity
        wait_time = ((31 - current_time.hour) * 60 + (60 - current_time.minute)) * 60
    else:
        return  # No waiting required if within allowed time
    print(f"Waiting {wait_time/3600:.2f} hours until the next allowed window...")
    time.sleep(wait_time)

def main(csv_filename, webhook_url, session_cookies, user_agent):
    with open(csv_filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            first_name = row.get('first_name')
            last_name = row.get('last_name')
            email = row.get('email')
            linkedin_profile = row.get('linkedin_profile')
            company_name = row.get('company_name')

            current_time = datetime.datetime.utcnow()
            if current_time.hour < 8 or current_time.hour >= 17:
                wait_until_next_window(current_time)

            send_data_to_webhook(first_name, last_name, email, linkedin_profile, company_name, webhook_url, session_cookies, user_agent)

            # Random wait between 15 to 30 minutes
            delay_minutes = random.randint(15, 30)
            print(f"Waiting for {delay_minutes} minutes before sending the next row.")
            time.sleep(delay_minutes * 60)

@app.route('/get_cookies', methods=['GET'])
def get_cookies():
    session_cookies = os.environ.get('SESSION_COOKIES', 'No cookies found')
    return jsonify({'session_cookies': session_cookies})
    

@app.route('/start-script', methods=['POST'])
def start_script():
    data = request.get_json()
    csv_filename = data.get('csv_filename')
    webhook_url = data.get('webhook_url')
    session_cookies = data.get('session_cookies')
    user_agent = data.get('user_agent')

    if not all([csv_filename, webhook_url, session_cookies, user_agent]):
        return jsonify({'error': 'Missing required parameters'}), 400

    thread = threading.Thread(target=main, args=(csv_filename, webhook_url, session_cookies, user_agent))
    thread.start()
    return jsonify({'message': 'Script is running'}), 202

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
