import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import FriendFlow from './FriendFlow.jsx';
import './index.css';

// A friend invite link is anaphora.app/?f=<token> — no router needed, just
// a query-string check before the normal app's state machine takes over.
const friendToken = new URLSearchParams(window.location.search).get('f');

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {friendToken ? <FriendFlow token={friendToken} /> : <App />}
  </React.StrictMode>
);
