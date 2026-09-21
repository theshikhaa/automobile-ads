export const API_URL = import.meta.env.VITE_API_URL || "https://automobile-ads.onrender.com";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail || response.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return payload;
}

export const api = {
  health: () => request("/health"),
  metrics: () => request("/api/v1/metrics"),
  insights: () => request("/api/v1/insights"),
  drift: () => request("/api/v1/drift"),
  schema: () => request("/api/v1/schema"),
  sample: () => request("/api/v1/sample"),
  predict: (body) =>
    request("/api/v1/predict", { method: "POST", body: JSON.stringify(body) }),
  explain: (body) =>
    request("/api/v1/explain", { method: "POST", body: JSON.stringify(body) }),
};
