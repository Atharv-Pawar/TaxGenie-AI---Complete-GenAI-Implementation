import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 120_000,
});

// ─── Upload ───────────────────────────────────────────────────────────────────
export async function uploadPDF(file: File): Promise<{ session_id: string }> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

// ─── Analyze ──────────────────────────────────────────────────────────────────
export async function analyzeSync(params: {
  session_id: string;
  risk_profile?: string;
  manual_income?: number;
  additional_rent_paid?: number;
}) {
  const form = new FormData();
  form.append("session_id", params.session_id);
  form.append("risk_profile", params.risk_profile ?? "moderate");
  if (params.manual_income) form.append("manual_income", String(params.manual_income));
  if (params.additional_rent_paid) form.append("additional_rent_paid", String(params.additional_rent_paid));

  const { data } = await api.post("/analyze/sync", form);
  return data;
}

export async function analyzeAsync(params: {
  session_id: string;
  risk_profile?: string;
  manual_income?: number;
}) {
  const form = new FormData();
  form.append("session_id", params.session_id);
  form.append("risk_profile", params.risk_profile ?? "moderate");
  if (params.manual_income) form.append("manual_income", String(params.manual_income));
  const { data } = await api.post("/analyze", form);
  return data;
}

// ─── Results ──────────────────────────────────────────────────────────────────
export async function getResults(sessionId: string) {
  const { data } = await api.get(`/results/${sessionId}`);
  return data;
}

// ─── Chat ─────────────────────────────────────────────────────────────────────
export async function sendChat(sessionId: string, message: string) {
  const { data } = await api.post("/chat", {
    session_id: sessionId,
    message,
    context_type: "tax_analysis",
  });
  return data as {
    response: string;
    sources: string[];
    follow_up_suggestions: string[];
  };
}

// ─── WebSocket ────────────────────────────────────────────────────────────────
export function createProgressSocket(
  sessionId: string,
  onMessage: (data: { stage: string; message: string; progress: number }) => void,
  onClose?: () => void
): WebSocket {
  const wsBase = BASE_URL.replace(/^http/, "ws");
  const ws = new WebSocket(`${wsBase}/api/v1/ws/session/${sessionId}`);
  ws.onmessage = (e) => {
    try { onMessage(JSON.parse(e.data)); } catch {}
  };
  ws.onclose = () => onClose?.();
  return ws;
}
