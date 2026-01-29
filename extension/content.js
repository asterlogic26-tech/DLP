// DLP Regex Patterns
const PATTERNS = {
  PAN: /[A-Z]{5}[0-9]{4}[A-Z]{1}/,
  AADHAR: /\b\d{4}\s?\d{4}\s?\d{4}\b/,
  CREDIT_CARD: /\b(?:\d{4}[ -]?){3}\d{4}\b/
};

let userToken = null;

// Load token
chrome.runtime.sendMessage({ type: "GET_TOKEN" }, (response) => {
  if (response && response.token) {
    userToken = response.token;
  }
});

// Sync Token from Dashboard if we are on the dashboard
if (window.location.href.includes("extension-blocker") || window.location.href.includes("localhost")) {
  const token = localStorage.getItem("token");
  if (token) {
    chrome.runtime.sendMessage({ type: "SAVE_TOKEN", token: token });
  }
}

// Monitor Inputs
document.addEventListener("input", (e) => {
  const target = e.target;
  if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") {
    const value = target.value;
    
    for (const [type, regex] of Object.entries(PATTERNS)) {
      if (regex.test(value)) {
        // Check if we already warned for this specific input session
        if (target.dataset.warned === "true") return;

        // Block immediately (blur)
        target.blur();
        
        showWarningModal(type, target, value);
        break;
      }
    }
  }
}, true);

// Adult Content / Spam Keywords (Simple version)
const BAD_KEYWORDS = ["xxx", "porn", "lottery winner", "click here to claim"];
const pageText = document.body.innerText.toLowerCase();
if (BAD_KEYWORDS.some(kw => pageText.includes(kw))) {
  // Report event
  chrome.runtime.sendMessage({
    type: "LOG_EVENT",
    data: {
      event_type: "CONTENT_FILTER",
      description: "Suspicious content detected on page",
      url: window.location.href,
      action_taken: "WARNING"
    }
  });
}

function showWarningModal(type, inputElement, value) {
  // Create Modal DOM
  const modal = document.createElement("div");
  modal.style.cssText = `
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(15, 23, 42, 0.9); z-index: 999999;
    display: flex; align-items: center; justify-content: center;
    font-family: sans-serif;
  `;

  modal.innerHTML = `
    <div style="background: #1e293b; padding: 30px; border-radius: 12px; border: 1px solid #ef4444; max-width: 400px; text-align: center; color: white;">
      <h2 style="color: #ef4444; margin-top: 0; font-size: 24px;">⚠️ Security Alert</h2>
      <p style="color: #cbd5e1; margin: 20px 0;">
        We detected sensitive <strong>${type}</strong> information.
        Sharing this data on untrusted sites can lead to identity theft.
      </p>
      <div style="display: flex; gap: 10px; justify-content: center;">
        <button id="cg-block" style="background: #10b981; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold;">Block (Recommended)</button>
        <button id="cg-allow" style="background: transparent; border: 1px solid #64748b; color: #94a3b8; padding: 10px 20px; border-radius: 6px; cursor: pointer;">Ignore & Allow</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  document.getElementById("cg-block").onclick = () => {
    inputElement.value = ""; // Clear it
    inputElement.dataset.warned = "false";
    modal.remove();
    logEvent("LEAK_ATTEMPT", `Blocked ${type} on ${window.location.hostname}`, "BLOCKED");
  };

  document.getElementById("cg-allow").onclick = () => {
    inputElement.dataset.warned = "true"; // Don't warn again for this input
    modal.remove();
    inputElement.focus();
    logEvent("LEAK_ATTEMPT", `User allowed ${type} on ${window.location.hostname}`, "ALLOWED");
  };
}

function logEvent(type, desc, action) {
  chrome.runtime.sendMessage({
    type: "LOG_EVENT",
    data: {
      event_type: type,
      description: desc,
      url: window.location.href,
      action_taken: action
    }
  });
}
