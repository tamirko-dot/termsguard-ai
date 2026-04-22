import { isToSPage } from "./lib/detector.js";
import { clearHighlights, highlightFinding } from "./lib/highlighter.js";

if (isToSPage()) {
  chrome.runtime.sendMessage({ type: "SET_BADGE", text: "ToS", color: "#d69e2e" });
}

chrome.runtime.onMessage.addListener((message) => {
  if (message.type === "HIGHLIGHT_FINDING") {
    highlightFinding(message.sourceQuote, message.risk);
  }
  if (message.type === "CLEAR_HIGHLIGHTS") {
    clearHighlights();
  }
  if (message.type === "GET_PAGE_TEXT") {
    return Promise.resolve({
      text: document.body?.innerText || "",
      url: window.location.href,
      title: document.title,
    });
  }
});
