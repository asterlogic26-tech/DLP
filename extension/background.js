let API_URL = "http://localhost:8000"; // Will be updated dynamically if possible

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SAVE_TOKEN") {
    chrome.storage.local.set({ token: message.token }, () => {
      console.log("Token saved");
    });
  } else if (message.type === "GET_TOKEN") {
    chrome.storage.local.get("token", (data) => {
      sendResponse({ token: data.token });
    });
    return true; // Async response
  } else if (message.type === "LOG_EVENT") {
    logEventToBackend(message.data);
  }
});

function logEventToBackend(eventData) {
  chrome.storage.local.get("token", (data) => {
    if (!data.token) return;

    // Use fetch
    fetch(`${API_URL}/events`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${data.token}`
      },
      body: JSON.stringify(eventData)
    }).catch(err => console.error("Failed to log event", err));
  });
}
