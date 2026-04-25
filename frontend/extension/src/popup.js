import { analyzeText } from "./lib/api_client.js";

const analyzeBtn = document.getElementById("analyze-btn");
const statusEl = document.getElementById("status");
const loadingEl = document.getElementById("loading");
const resultEl = document.getElementById("result");
const trafficLightEl = document.getElementById("traffic-light");
const summaryEl = document.getElementById("summary");
const findingsEl = document.getElementById("findings");
const clearBtn = document.getElementById("clear-btn");
const metaEl = document.getElementById("meta");

const RISK_ICONS = { red: "🔴", yellow: "🟡", green: "🟢" };
const RISK_LABELS = { red: "HIGH RISK", yellow: "MEDIUM RISK", green: "LOW RISK" };

let stepTimers = [];

function showLoading() {
  loadingEl.style.display = "block";
  const s1 = document.getElementById("step-extract");
  const s2 = document.getElementById("step-analyze");
  const s3 = document.getElementById("step-report");
  s1.className = "step active";
  s2.className = "step pending";
  s3.className = "step pending";
  stepTimers.push(setTimeout(() => { s1.className = "step done"; s2.className = "step active"; }, 4000));
  stepTimers.push(setTimeout(() => { s2.className = "step done"; s3.className = "step active"; }, 25000));
}

function hideLoading() {
  loadingEl.style.display = "none";
  stepTimers.forEach(clearTimeout);
  stepTimers = [];
}

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

  showLoading();

  let report;
  try {
    report = await analyzeText(text, url, title);
  } catch (err) {
    hideLoading();
    statusEl.textContent = `Error: ${err.message}`;
    analyzeBtn.disabled = false;
    return;
  }

  hideLoading();
  renderReport(report, tab.id);
  analyzeBtn.disabled = false;
});

clearBtn.addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => {
      document.querySelectorAll(".termsguard-highlight").forEach((el) => {
        el.replaceWith(...el.childNodes);
      });
    },
  });
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
    card.addEventListener("click", async () => {
      const COLORS = { red: "#fed7d7", yellow: "#fefcbf", green: "#c6f6d5" };
      const color = COLORS[finding.risk] || "#e2e8f0";
      const quote = finding.source_quote;
      await chrome.scripting.executeScript({
        target: { tabId: tabId },
        func: (sourceQuote, bgColor) => {
          const candidates = [
            sourceQuote,
            sourceQuote.slice(0, 120).trim(),
            sourceQuote.slice(0, 80).trim(),
            sourceQuote.slice(0, 50).trim(),
          ];
          for (const text of candidates) {
            if (text.length < 15) break;
            if (!window.find(text, false, false, true, false, false, false)) continue;
            const sel = window.getSelection();
            if (!sel || !sel.rangeCount) continue;
            const range = sel.getRangeAt(0);
            try {
              const mark = document.createElement("mark");
              mark.className = "termsguard-highlight";
              mark.style.cssText = `background:${bgColor}; border-radius:3px; padding:1px 3px; color:inherit; outline:2px solid rgba(0,0,0,0.15);`;
              range.surroundContents(mark);
              mark.scrollIntoView({ behavior: "smooth", block: "center" });
            } catch {
              range.startContainer.parentElement?.scrollIntoView({ behavior: "smooth", block: "center" });
            }
            sel.removeAllRanges();
            return;
          }
        },
        args: [quote, color],
      });
    });
    findingsEl.appendChild(card);
  });

  metaEl.textContent = `${report.findings.length} findings · ${report.processing_ms}ms · ${report.doc_meta?.url || ""}`;
  resultEl.style.display = "block";
}
