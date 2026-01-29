// Check if this is the DLP Dashboard (local or prod)
if (window.location.hostname === "localhost" || localStorage.getItem("dlp_app_id")) {
  // Check for token and configuration periodically or on change
  setInterval(() => {
    const token = localStorage.getItem("token");
    const apiUrl = localStorage.getItem("api_url");
    
    if (token) {
      chrome.runtime.sendMessage({ 
        type: "SET_TOKEN", 
        token: token,
        apiUrl: apiUrl 
      });
    }
  }, 2000);
}
