async function getApiBaseUrl() {
  return new Promise((resolve) => {
    chrome.storage.local.get("apiBaseUrl", (data) => {
      resolve(data.apiBaseUrl || "https://backend-production-1d50.up.railway.app");
    });
  });
}

export async function analyzeText(rawText, url = null, title = null) {
  const baseUrl = await getApiBaseUrl();
  const response = await fetch(`${baseUrl}/api/v1/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: rawText, url, title }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`API error ${response.status}: ${err}`);
  }

  return response.json();
}
