// DLP Regex Patterns - COMPREHENSIVE LIBRARY
const PATTERNS = {
  // Identity Documents (India)
  PAN_CARD: /[A-Z]{5}[0-9]{4}[A-Z]{1}/,
  AADHAR_CARD: /\b\d{4}\s?\d{4}\s?\d{4}\b/,
  PASSPORT: /\b[A-Z]{1}[0-9]{7}\b/,
  VOTER_ID: /\b[A-Z]{3}[0-9]{7}\b/,
  
  // Financial Data
  CREDIT_CARD: /\b(?:\d{4}[ -]?){3}\d{4}\b/,
  GSTIN: /\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b/,
  IFSC_CODE: /\b[A-Z]{4}0[A-Z0-9]{6}\b/,
  UPI_ID: /\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b/,
  
  // Contact Info
  EMAIL: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/,
  PHONE_INDIA: /\b(?:\+91|91)?[6-9]\d{9}\b/,
  
  // Technical Secrets
  AWS_ACCESS_KEY: /\bAKIA[0-9A-Z]{16}\b/,
  GOOGLE_API_KEY: /AIza[0-9A-Za-z-_]{35}/,
  PRIVATE_KEY: /-----BEGIN PRIVATE KEY-----/
};

let userToken = null;

// Load token
chrome.runtime.sendMessage({ type: "GET_TOKEN" }, (response) => {
  if (response && response.token) {
    userToken = response.token;
  }
});

// Token Sync Check (Add debug logs)
if (window.location.href.includes("networknimble.info") || window.location.href.includes("localhost")) {
  console.log("CyberGuard: Detected Dashboard. Syncing token...");
  const token = localStorage.getItem("token");
  if (token) {
    chrome.runtime.sendMessage({ type: "SAVE_TOKEN", token: token }, () => {
       console.log("CyberGuard: Token sent to extension.");
    });
  } else {
    console.warn("CyberGuard: No token found in localStorage.");
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
  // 1. Block the Content
  document.body.innerHTML = `
    <div style="
      position: fixed; top: 0; left: 0; width: 100%; height: 100%;
      background: #0f172a; color: white; display: flex; flex-direction: column;
      align-items: center; justify-content: center; z-index: 999999; font-family: sans-serif;
    ">
      <h1 style="color: #ef4444; font-size: 48px; margin-bottom: 20px;">🚫 Content Blocked</h1>
      <p style="font-size: 20px; color: #cbd5e1; margin-bottom: 30px;">
        CyberGuard detected unsafe/adult content on this page.
      </p>
      <button onclick="window.history.back()" style="
        background: #3b82f6; color: white; border: none; padding: 12px 24px;
        border-radius: 8px; font-size: 18px; cursor: pointer;
      ">Go Back</button>
    </div>
  `;

  // 2. Report event
  chrome.runtime.sendMessage({
    type: "LOG_EVENT",
    data: {
      event_type: "CONTENT_BLOCKED",
      description: "Adult/Spam content blocked",
      url: window.location.href,
      action_taken: "BLOCKED"
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
