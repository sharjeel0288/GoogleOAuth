

---

# Google OAuth Integration with Flask and React

This project demonstrates how to integrate Google OAuth for user authentication and Gmail email sending using Flask (backend) and React (frontend). Users can authenticate with Google, send emails through Gmail, and view their profile information.

## Prerequisites

Before setting up this project, ensure you have the following:
- Python 3.x
- Node.js and npm/yarn
- Google Cloud Project (to generate OAuth credentials)
- Flask and Flask extensions (`Flask`, `Flask-CORS`, `Flask-Session`, `google-auth-oauthlib`, `google-api-python-client`)

## Setup Google OAuth

### Step 1: Create a Project on Google Cloud Console
1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project:
   - Click on **Select a Project** at the top of the page.
   - Click **New Project** and fill in the necessary details (e.g., name and billing).
3. Enable the necessary APIs:
   - Go to **APIs & Services > Library**.
   - Search for **Gmail API** and click on **Enable**.
4. Create OAuth credentials:
   - Go to **APIs & Services > Credentials**.
   - Click **Create Credentials > OAuth 2.0 Client IDs**.
   - Configure the OAuth consent screen:
     - Choose **External** for the User Type.
     - Fill in the required fields (e.g., Application Name, Support Email).
     - Add a scope: `https://www.googleapis.com/auth/userinfo.email` and `https://www.googleapis.com/auth/gmail.send`.
   - Under **Authorized Redirect URIs**, add:
     - `https://localhost:3001/oauth2callback`
   - Under **Authorized JavaScript Origins**, add:
     - `http://localhost:3000`
   - After this, download the `client_secret.json` file.

Replace the contents of the `client_secret.json` file with your own credentials. Here's an example of the JSON structure:

```json
{
  "web": {
    "client_id": "YOUR_CLIENT_ID",
    "project_id": "YOUR_PROJECT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["https://localhost:3001/oauth2callback"],
    "javascript_origins": ["http://localhost:3000"]
  }
}
```

### Step 2: Backend Setup (Flask)
1. Clone or download the repository, and navigate to the **backend** folder.
2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Place the `client_secret.json` file in the **backend** directory.
4. **Generate SSL Certificates**:
   Before starting the Flask server, you need SSL certificates to enable secure communication. Run the following command to generate a new SSL certificate and key:

   ```bash
   openssl req -new -newkey rsa:2048 -days 365 -nodes -keyout server.key -out server.crt
   ```

   This command generates:
   - `server.key`: The private key for SSL.
   - `server.crt`: The certificate file for SSL.

5. Configure the backend settings:
   - Make sure the `REDIRECT_URI` in the Flask app matches the URI set in Google Cloud Console (`https://localhost:3001/oauth2callback`).
   - The backend is set up to run on `https://localhost:3001`. Ensure you have the `server.crt` and `server.key` files for SSL.
   
6. Run the Flask server:

   ```bash
   python server.py
   ```

The backend will be available at `https://localhost:3001`.

### Step 3: Frontend Setup (React)
1. Navigate to the **frontend** folder.
2. Install the necessary Node dependencies:

   ```bash
   npm install
   ```

3. In the `src/App.js` file, update the backend URL if necessary. The frontend makes API calls to `https://localhost:3001` for authentication and email functionalities.

4. Start the React development server:

   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`.

### Step 4: Testing the Setup
1. **Login**: Visit `http://localhost:3000`. Click the **Login with Google** button. The page will redirect to Google's OAuth login. After successful login, the backend will authenticate the user, and you will see the user's name and email on the frontend.
2. **Send Email**: Once logged in, you can use the form to send an email through Gmail. The backend will handle the Gmail API integration to send the email.

### Step 5: Logout
You can logout by clicking the **Logout** button, which will remove the session data from the backend and frontend.

## Folder Structure

```
GmailOAuth/
├── backend/
│   ├── client_secret.json  # OAuth credentials file
│   ├── server.py          # Flask application
│   ├── server.crt         # SSL certificate
│   ├── server.key         # SSL private key
│   ├── flask_session/     # Session storage
├── frontend/
│   ├── package.json       # React project metadata
│   ├── src/
│   │   ├── App.js         # React frontend
│   │   ├── App.css        # Styles
│   ├── public/
│   │   ├── index.html     # HTML file
│   ├── node_modules/      # Dependencies
```

## Backend Code Explanation

The backend is built using Flask and handles the following:

- **OAuth Flow**: It uses the `google-auth-oauthlib` library to handle the OAuth 2.0 authentication flow.
- **Session Management**: The `Flask-Session` extension stores user credentials in the server's session.
- **Gmail API Integration**: The backend allows sending emails using the Gmail API (`googleapiclient.discovery.build`).

The backend provides the following routes:
- **`/login`**: Initiates the OAuth login flow.
- **`/oauth2callback`**: Handles the callback from Google after successful authentication.
- **`/send-email`**: Sends an email using the Gmail API.
- **`/logout`**: Logs the user out by clearing session data.
- **`/`**: Fetches the authenticated user's information.

## Frontend Code Explanation

The frontend is a React app that interacts with the Flask backend:

- **Login**: It redirects the user to the backend `/login` route to initiate the OAuth flow.
- **User Info**: After successful login, it fetches the user's info from the `/` route.
- **Send Email**: The form allows users to send an email through Gmail by making a POST request to the backend's `/send-email` route.

## Notes

- Ensure that both the frontend (React) and backend (Flask) are running on different ports (e.g., React on `localhost:3000` and Flask on `localhost:3001`).
- You will need SSL certificates (`server.crt`, `server.key`) for secure communication between the backend and frontend.
- Modify the redirect URIs and origins in the Google Cloud Console if you deploy this app to production.

--- 
