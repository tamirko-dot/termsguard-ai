import { analyzeText } from "./lib/api_client.js";

const analyzeBtn = document.getElementById("analyze-btn");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const trafficLightEl = document.getElementById("traffic-light");
const summaryEl = document.getElementById("summary");
const findingsEl = document.getElementById("findings");
const clearBtn = document.getElementById("clear-btn");
const metaEl = document.getElementById("meta");

const RISK_ICONS = { red: "🔴", yellow: "🟡", green: "🟢" };
const RISK_LABELS = { red: "HIGH RISK", yellow: "MEDIUM RISK", green: "LOW RISK" };

analyzeBtn.addEventListener("click", async () => {
  analyzeBtn.disabled = true;
  statusEl.textContent = "Extracting page text...";
  resultEl.style.display = "none";

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  let pageData;
  try {
    [pageData] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => ({ text: document.body?.innerText || "", url: location.href, title: document.title }),
    });
  } catch {
    statusEl.textContent = "Cannot access this page.";
    analyzeBtn.disabled = false;
    return;
  }

  const { text, url, title } = pageData.result;
  if (!text.trim()) {
    statusEl.textContent = "No text found on this page.";
    analyzeBtn.disabled = false;
    return;
  }

  statusEl.textContent = "Analyzing with TermsGuard AI (up to 60s)...";

  let report;
  try {
    report = await analyzeText(text, url, title);
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
    analyzeBtn.disabled = false;
    return;
  }

  statusEl.textContent = "";
  renderReport(report, tab.id);
  analyzeBtn.disabled = false;
});

clearBtn.addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.tabs.sendMessage(tab.id, { type: "CLEAR_HIGHLIGHTS" });
});

function renderReport(report, tabId) {
  const level = report.traffic_light;
  trafficLightEl.className = `traffic-light ${level}`;
  trafficLightEl.textContent = `${RISK_ICONS[level]} ${RISK_LABELS[level]}`;

  summaryEl.textContent = report.summary;

  findingsEl.innerHTML = "";
  const sorted = [...report.findings].sort((a, b) => {
    const order = { red: 0, yellow: 1, green: 2 };
    return order[a.risk] - order[b.risk];
  });

  sorted.forEach((finding) => {
    const card = document.createElement("button");
    card.className = `finding ${finding.risk}`;
    card.title = "Click to highlight in page";
    card.innerHTML = `
      <div class="finding-title">${RISK_ICONS[finding.risk]} ${finding.title} <span class="find-icon">🔍</span></div>
      <div class="finding-explanation">${finding.explanation}</div>
    `;
    card.addEventListener("click", () => {
      chrome.tabs.sendMessage(tabId, {
        type: "HIGHLIGHT_FINDING",
        sourceQuote: finding.source_quote,
        risk: finding.risk,
      });
    });
    findingsEl.appendChild(card);
  });

  metaEl.textContent = `${report.findings.length} findings · ${report.processing_ms}ms · ${report.doc_meta?.url || ""}`;
  resultEl.style.display = "block";
}
