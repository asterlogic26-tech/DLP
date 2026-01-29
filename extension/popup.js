document.getElementById("login").onclick = () => {
  chrome.tabs.create({ url: "http://localhost:5173" });
};

// Check status from background page
chrome.runtime.sendMessage({ type: "GET_STATUS" }, (response) => {
    // This part requires background.js to listen for GET_STATUS
    // For now, we'll just check storage directly if possible or rely on simple UI
    updateUI();
});

function updateUI() {
    chrome.storage.local.get(["token"], (result) => {
        const statusDiv = document.getElementById("status");
        if (result.token) {
            statusDiv.innerHTML = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">● Connected</span>';
        } else {
            statusDiv.innerHTML = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">● Not Connected</span>';
        }
    });
}

updateUI();
