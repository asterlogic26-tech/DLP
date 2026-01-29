import { useState, useEffect } from "react";
import Login from "./Login";
import Dashboard from "./Dashboard";
import { API_URL } from "./api";

export default function App() {
  const [token, setToken] = useState(localStorage.token);

  useEffect(() => {
    // Expose configuration for the extension
    localStorage.api_url = API_URL;
    localStorage.dlp_app_id = "true";
  }, []);

  const handleLogin = (newToken) => {
    localStorage.token = newToken;
    setToken(newToken);
  };

  const handleLogout = () => {
    delete localStorage.token;
    setToken(null);
  };

  return token ? <Dashboard onLogout={handleLogout} /> : <Login onLogin={handleLogin} />;
}
