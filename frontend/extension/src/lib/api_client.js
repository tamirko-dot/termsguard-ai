async function getApiBaseUrl() {
  return new Promise((resolve) => {
    chrome.storage.local.get("apiBaseUrl", (data) => {
      resolve(data.apiBaseUrl || "https://backend-production-1d50.up.railway.app");
    });
  });
}

export async function analyzeText(rawText, url = null, title = null) {
  const baseUrl = await getApiBaseUrl();

  const submitRes = await fetch(`${baseUrl}/api/v1/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: rawText, url, title }),
  });

  if (!submitRes.ok) {
    const err = await submitRes.text();
    throw new Error(`API error ${submitRes.status}: ${err}`);
  }

  const { job_id } = await submitRes.json();

  while (true) {
    await new Promise((resolve) => setTimeout(resolve, 5000));

    const pollRes = await fetch(`${baseUrl}/api/v1/analyze/${job_id}`);
    if (!pollRes.ok) throw new Error(`Poll error ${pollRes.status}`);

    const job = await pollRes.json();
    if (job.status === "done") return job.result;
    if (job.status === "error") throw new Error(job.error || "Analysis failed");
  }
}
