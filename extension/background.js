let authToken = null;
let apiBaseUrl = "http://localhost:8000"; // Default, will be updated from content script
let isProtected = false;

// Load token and config on startup
chrome.storage.local.get(["token", "apiUrl"], (result) => {
  if (result.token) {
    authToken = result.token;
  }
  if (result.apiUrl) {
    apiBaseUrl = result.apiUrl;
  }
  if (authToken) checkLicense();
});

// Listen for token from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SET_TOKEN" && message.token) {
    let changed = false;
    if (authToken !== message.token) {
        authToken = message.token;
        chrome.storage.local.set({ token: message.token });
        changed = true;
    }
    if (message.apiUrl && apiBaseUrl !== message.apiUrl) {
        apiBaseUrl = message.apiUrl;
        chrome.storage.local.set({ apiUrl: message.apiUrl });
        changed = true;
    }
    
    if (changed) {
        checkLicense();
        console.log("Token/Config updated");
    }
  }
});

// Periodic License Check (every 5 minutes)
chrome.alarms.create("licenseCheck", { periodInMinutes: 5 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "licenseCheck") {
    checkLicense();
  }
});

async function checkLicense() {
  if (!authToken) return;

  try {
    const response = await fetch(`${apiBaseUrl}/auth/status`, {
      headers: {
        "Authorization": `Bearer ${authToken}`
      }
    });
    
    if (response.ok) {
        const data = await response.json();
        if (data.active) {
            enableProtection();
        } else {
            disableProtection();
        }
    } else {
        disableProtection(); // Auth failed or server error
    }
  } catch (e) {
    console.error("License check failed", e);
    // Optionally disable protection on network error, or keep last known state
  }
}

function enableProtection() {
  if (isProtected) return;
  isProtected = true;
  console.log("Protection Enabled");
  
  // Example: Block Social Media
  const rules = [
    {
      id: 1,
      priority: 1,
      action: { type: "block" },
      condition: { urlFilter: "facebook.com", resourceTypes: ["main_frame"] }
    },
    {
      id: 2,
      priority: 1,
      action: { type: "block" },
      condition: { urlFilter: "instagram.com", resourceTypes: ["main_frame"] }
    },
    {
      id: 3,
      priority: 1,
      action: { type: "block" },
      condition: { urlFilter: "twitter.com", resourceTypes: ["main_frame"] }
    }
  ];
  
  chrome.declarativeNetRequest.updateDynamicRules({
    addRules: rules,
    removeRuleIds: [1, 2, 3]
  });
  
  chrome.action.setBadgeText({ text: "ON" });
  chrome.action.setBadgeBackgroundColor({ color: "#4F46E5" });
}

function disableProtection() {
  if (!isProtected) return;
  isProtected = false;
  console.log("Protection Disabled");
  
  chrome.declarativeNetRequest.updateDynamicRules({
    removeRuleIds: [1, 2, 3]
  });
  
  chrome.action.setBadgeText({ text: "OFF" });
  chrome.action.setBadgeBackgroundColor({ color: "#6B7280" });
}
