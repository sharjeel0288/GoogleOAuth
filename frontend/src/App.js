import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);
  const [toEmail, setToEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [htmlBody, setHtmlBody] = useState('');
  const [message, setMessage] = useState(null);

  useEffect(() => {
    // Fetch user info from backend
    axios.get('https://localhost:3001/', { withCredentials: true }) // Pass credentials
      .then(response => {
        setUser(response.data); // Store user info
        setError(null); // Clear any errors
      })
      .catch(err => {
        setUser(null); // Reset user state on error
        setError(err.response?.data?.error || 'Failed to fetch user info');
      });
  }, []);

  const handleLogin = () => {
    window.location.href = 'https://localhost:3001/login'; // Redirect to login endpoint
  };

  const handleLogout = () => {
    axios.get('https://localhost:3001/logout', { withCredentials: true })
      .then(() => {
        setUser(null); // Clear user state after logout
        setError(null); // Clear any errors
      })
      .catch(err => {
        setError(err.response?.data?.error || 'Failed to log out');
      });
  };

  const handleSendEmail = () => {
    const payload = {
      to_email: toEmail,
      subject: subject,
      html_body: htmlBody,
    };

    axios.post('https://localhost:3001/send-email', payload, { withCredentials: true })
      .then(response => {
        setMessage('Email sent successfully');
        setError(null);
      })
      .catch(err => {
        setMessage(null);
        setError(err.response?.data?.error || 'Failed to send email');
      });
  };

  return (
    <div>
      <h1>Welcome to the Google OAuth App</h1>
      {user ? (
        <div>
          <h2>Hello, {user.name} ({user.email})</h2>
          <button onClick={handleLogout}>Logout</button>

          <div style={{ marginTop: '20px' }}>
            <h3>Send Email</h3>
            <input
              type="email"
              placeholder="Recipient's Email"
              value={toEmail}
              onChange={e => setToEmail(e.target.value)}
              style={{ display: 'block', marginBottom: '10px' }}
            />
            <input
              type="text"
              placeholder="Subject"
              value={subject}
              onChange={e => setSubject(e.target.value)}
              style={{ display: 'block', marginBottom: '10px' }}
            />
            <textarea
              placeholder="HTML Body"
              value={htmlBody}
              onChange={e => setHtmlBody(e.target.value)}
              style={{ display: 'block', marginBottom: '10px', width: '300px', height: '100px' }}
            />
            <button onClick={handleSendEmail}>Send Email</button>
            {message && <p style={{ color: 'green' }}>{message}</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
          </div>
        </div>
      ) : (
        <div>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <button onClick={handleLogin}>Login with Google</button>
        </div>
      )}
    </div>
  );
}

export default App;
