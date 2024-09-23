from flask import Flask, jsonify
from simple_salesforce import Salesforce
import requests
import os

app = Flask(__name__)

# Environment variables for Connected App
SF_USERNAME = os.getenv('SF_USERNAME')   
SF_PASSWORD = os.getenv('SF_PASSWORD')  
SF_SECURITY_TOKEN = os.getenv('SF_SECURITY_TOKEN')  
SF_CLIENT_ID = os.getenv('SF_CLIENT_ID')  
SF_CLIENT_SECRET = os.getenv('SF_CLIENT_SECRET')  
SF_DOMAIN = 'login'  # 'login' for production, 'test' for sandbox

# Salesforce token URL
TOKEN_URL = f"https://{SF_DOMAIN}.salesforce.com/services/oauth2/token"


# Function to get access token and instance URL
def get_salesforce_access():
    # Login payload for OAuth 2.0
    payload = {
        'grant_type': 'password',
        'client_id': SF_CLIENT_ID,
        'client_secret': SF_CLIENT_SECRET,
        'username': SF_USERNAME,
        'password': SF_PASSWORD + SF_SECURITY_TOKEN
    }

    try:
        # Request the access token
        response = requests.post(TOKEN_URL, data=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        auth_data = response.json()
        return auth_data.get('access_token'), auth_data.get('instance_url')
    except requests.exceptions.RequestException as e:
        return None, None, f"Error logging into Salesforce: {e}"


# Function to query Salesforce accounts
def fetch_accounts():
    access_token, instance_url = get_salesforce_access()

    if not access_token or not instance_url:
        return {"error": "Error logging into Salesforce"}
    
    try:
        # Initialize Salesforce session
        sf = Salesforce(instance_url=instance_url, session_id=access_token)

        # Query Accounts
        query = "SELECT Id, Name, Industry, BillingCity FROM Account LIMIT 10"
        accounts = sf.query(query)
        
        # Return account data
        return accounts['records']
    except Exception as e:
        return {"error": f"Error querying Salesforce accounts: {str(e)}"}


# Route to display the Salesforce records
@app.route('/accounts')
def index():
    accounts = fetch_accounts()
    return jsonify(accounts)


if __name__ == '__main__':
    app.run(debug=True)
