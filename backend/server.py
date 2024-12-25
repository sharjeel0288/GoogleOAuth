import os
from flask import Flask, jsonify, redirect, request, session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import requests
from flask_cors import CORS
from flask_session import Session
from googleapiclient.discovery import build
import requests
from google.auth.transport.requests import Request


# Initialize Flask app
app = Flask(__name__)

# Secret key for session management
app.secret_key = os.urandom(24)

# Flask-Session Configuration
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions on the server filesystem
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = True
Session(app)

# Enable CORS with credentials
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Google OAuth2 Client ID and Client Secret
CLIENT_SECRETS_FILE = "client_secret.json"  # Update with the correct path

# Scopes requested for the application
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/gmail.send',
]

# Redirect URI is set to this endpoint for Google OAuth2 callback
REDIRECT_URI = 'https://localhost:3001/oauth2callback'  # Adjust for your setup


@app.route('/')
def index():
    # Check if user is logged in
    print("Session data:", session)  # Debugging log to check session content
    if 'credentials' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    credentials = Credentials.from_authorized_user_info(session['credentials'])
    user_info = get_user_info(credentials.token)

    if user_info:
        return jsonify(user_info)
    return jsonify({'error': 'Failed to retrieve user info'}), 500



@app.route('/send-email', methods=['POST'])
def send_email():
    """
    Endpoint to send email using the user's Gmail account.
    Expects `to_email`, `subject`, and `html_body` in the request JSON.
    """
    if 'credentials' not in session:
        return jsonify({'error': 'User not authenticated'}), 401

    # Get the credentials from the session
    credentials = Credentials.from_authorized_user_info(session['credentials'])

    # Refresh the token if it's expired
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        session['credentials'] = credentials_to_dict(credentials)

    try:
        # Initialize the Gmail API
        service = build('gmail', 'v1', credentials=credentials)

        # Parse the request JSON
        data = request.get_json()
        to_email = data.get('to_email')
        subject = data.get('subject')
        html_body = data.get('html_body')

        if not all([to_email, subject, html_body]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Create the email message
        message = create_email_message(to_email, subject, html_body)

        # Send the email using the Gmail API
        sent_message = service.users().messages().send(userId='me', body=message).execute()

        return jsonify({'message': 'Email sent successfully', 'id': sent_message['id']})
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'error': 'Failed to send email', 'details': str(e)}), 500


def create_email_message(to_email, subject, html_body):
    """
    Creates an email message in the required format for the Gmail API.
    """
    import base64
    from email.mime.text import MIMEText

    # Construct the email message
    message = MIMEText(html_body, 'html')
    message['to'] = to_email
    message['subject'] = subject

    # Encode the message in base64 as required by Gmail API
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': encoded_message}


@app.route('/login')
def login():
    # Initialize OAuth2 flow
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI

    # Generate the authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )

    # Save state in session to verify it during the callback
    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Retrieve the authorization code from the request URL
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI

    # Fetch the OAuth2 token using the code from the callback URL
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response, state=session['state'])

    # Get the credentials and store them in the session
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    # Redirect to the frontend after successful login
    return redirect('http://localhost:3000/')


@app.route('/logout')
def logout():
    # Remove the user's credentials from the session
    session.pop('credentials', None)
    return jsonify({'message': 'Logged out successfully'})


def credentials_to_dict(credentials):
    """Converts credentials to a dictionary."""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


def get_user_info(access_token):
    """Fetch user information using the access token."""
    try:
        user_info_endpoint = "https://www.googleapis.com/oauth2/v1/userinfo"
        response = requests.get(user_info_endpoint, headers={
            'Authorization': f'Bearer {access_token}'
        })
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch user info: {e}")
        return None


if __name__ == '__main__':
    app.run(ssl_context=('server.crt', 'server.key'), port=3001)
