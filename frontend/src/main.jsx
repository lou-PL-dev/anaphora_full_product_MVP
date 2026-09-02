import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import FriendFlow from './FriendFlow.jsx';
import AdminTestSessions from './AdminTestSessions.jsx';
import './index.css';

const friendToken = new URLSearchParams(window.location.search).get('f');
const isAdminSessions = window.location.pathname.replace(/\/$/, '') === '/admin/test-sessions';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {isAdminSessions ? <AdminTestSessions /> : friendToken ? <FriendFlow token={friendToken} /> : <App />}
  </React.StrictMode>
);
