# TaxGenie AI — API Reference

**Base URL:** `http://localhost:8000/api/v1`  
**Interactive Docs:** `http://localhost:8000/docs`

---

## Health

### `GET /health`
Returns server status and service availability.

**Response 200:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "services": {
    "redis": "connected",
    "chromadb": "connected (186 chunks)"
  }
}
```

---

## Upload

### `POST /api/v1/upload`
Upload a Form 16 PDF. Must be called before `/analyze`.

**Request:** `multipart/form-data`
- `file` (File, required): PDF file, max 10MB

**Response 200:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "form16_2024.pdf",
  "size_mb": 0.45,
  "status": "uploaded",
  "message": "File uploaded successfully. Call /analyze to start analysis."
}
```

**Errors:**
- `400` — Not a PDF file
- `413` — File exceeds 10MB

---

## Analysis

### `POST /api/v1/analyze/sync`
Run the full LangGraph pipeline synchronously. Waits for result.

**Request:** `multipart/form-data`
- `session_id` (string, required): From `/upload`
- `risk_profile` (string, optional): `conservative` | `moderate` | `aggressive` (default: `moderate`)
- `manual_income` (float, optional): Override gross salary
- `additional_rent_paid` (float, optional): Monthly rent for HRA calculation

**Response 200:** Full `AnalysisResult` object (see schema below)

---

### `POST /api/v1/analyze`
Async version — returns immediately, use WebSocket or poll for updates.

**Response 200:**
```json
{
  "session_id": "...",
  "status": "processing",
  "estimated_time_seconds": 45,
  "websocket_url": "/api/v1/ws/session/{session_id}",
  "poll_url": "/api/v1/results/{session_id}"
}
```

---

### `GET /api/v1/results/{session_id}`
Poll for analysis results.

**Response 200:** `AnalysisResult` with `status` field:
- `"processing"` — Still running, poll again
- `"completed"` — Full results available
- `"failed"` — Error in `error` field

---

### `WebSocket /api/v1/ws/session/{session_id}`
Real-time progress stream. Connect **before** calling `/analyze`.

**Messages received:**
```json
{
  "stage": "parsing | analyzing | calculating | recommending | done",
  "message": "🔄 Parsing your Form 16...",
  "progress": 35
}
```

---

## Chat

### `POST /api/v1/chat`
Send a message to TaxGenie chatbot with session context.

**Request:**
```json
{
  "session_id": "...",
  "message": "Which tax regime is better for me?",
  "context_type": "tax_analysis"
}
```

**Response 200:**
```json
{
  "response": "Based on your salary of ₹12 LPA...",
  "sources": ["Section 80C - Deductions", "Finance Act 2023 - New Tax Regime"],
  "follow_up_suggestions": [
    "How much can I save with Old Regime if I invest more?",
    "What deductions are available only in Old Regime?"
  ]
}
```

---

### `GET /api/v1/chat/history/{session_id}`
Retrieve full chat history for a session.

### `DELETE /api/v1/chat/history/{session_id}`
Clear chat history for a session.

---

## Data Schemas

### `AnalysisResult`
```typescript
{
  session_id: string;
  status: "processing" | "completed" | "failed";
  parsed_data?: ParsedFormData;
  missed_deductions?: DeductionResult;
  regime_comparison?: RegimeComparison;
  investment_recommendations: InvestmentRecommendation[];
  summary?: string;
  total_potential_savings: number;
  error?: string;
}
```

### `RegimeComparison`
```typescript
{
  old_regime: { gross_income, total_deductions, taxable_income, tax_before_cess, health_education_cess, total_tax, breakdown };
  new_regime: { ... };
  recommended_regime: "OLD" | "NEW";
  savings_with_recommended: number;
  recommendation_reason: string;
  breakeven_deduction_amount: number;
}
```

### `MissedDeduction`
```typescript
{
  section: string;
  potential_saving: number;
  description: string;
  suggestions: string[];
  urgency: "HIGH" | "MEDIUM" | "LOW";
}
```

### `InvestmentRecommendation`
```typescript
{
  instrument: string;
  section: string;
  recommended_amount: number;
  expected_returns: string;
  lock_in_period: string;
  risk_level: string;
  reason: string;
  top_picks: string[];
}
```