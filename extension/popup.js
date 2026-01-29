document.getElementById("dashboard-btn").addEventListener("click", () => {
  // Open the deployed dashboard URL (or localhost for dev)
  chrome.tabs.create({ url: "http://localhost:5173" }); // Update this after deployment!
});

chrome.storage.local.get("token", (data) => {
  const statusText = document.getElementById("status-text");
  if (data.token) {
    statusText.textContent = "Protected";
    statusText.className = "active";
  } else {
    statusText.textContent = "Login Required";
    statusText.className = "inactive";
  }
});
