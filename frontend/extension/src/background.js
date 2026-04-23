const DEFAULT_API_BASE_URL = "https://backend-production-1d50.up.railway.app";

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get("apiBaseUrl", (data) => {
    if (!data.apiBaseUrl) {
      chrome.storage.local.set({ apiBaseUrl: DEFAULT_API_BASE_URL });
    }
  });
});

// Listen for badge update requests from content script
chrome.runtime.onMessage.addListener((message, sender) => {
  if (message.type === "SET_BADGE" && sender.tab?.id) {
    chrome.action.setBadgeText({ text: message.text, tabId: sender.tab.id });
    chrome.action.setBadgeBackgroundColor({
      color: message.color || "#e53e3e",
      tabId: sender.tab.id,
    });
  }
});
