# TaxGenie AI — Architecture Documentation

## Overview

TaxGenie AI is a full-stack AI-native application built with:
- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI + LangGraph (agent orchestration)
- **AI Models**: GPT-4o (PDF parsing, calculations) + Claude 3.5 Sonnet (reasoning, chat)
- **Vector DB**: ChromaDB (local) / Pinecone (production)
- **Memory**: Redis for session state and chat history

---

## System Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (Next.js 14)                    │
│         Upload │ Dashboard │ Results │ Chat                        │
└────────────────────────────┬───────────────────────────────────────┘
                             │ REST API + WebSocket
                             ▼
┌────────────────────────────────────────────────────────────────────┐
│               FASTAPI BACKEND + LANGGRAPH ORCHESTRATOR             │
│                                                                    │
│   State: {pdf_bytes, parsed_data, deductions,                      │
│           regime_comparison, recommendations, summary}             │
│                                                                    │
│   Pipeline: parse_pdf → find_deductions → compare_regimes          │
│             → recommend_investments → generate_report              │
└──────┬──────────┬──────────┬──────────┬──────────┬────────────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
   PDF Parser  Deduction  Regime    Investment  Explainer
    Agent      Finder     Advisor   Recommender  Agent
   (GPT-4o)  (Claude+RAG)(GPT-4o)  (GPT-4o)  (Claude)
                  │
                  ▼
            ChromaDB / Pinecone
            (Tax Rules RAG)
                  │
              Redis
          (Session Memory)
```

---

## Agent Descriptions

### 1. PDF Parser Agent (`agents/pdf_parser_agent.py`)
- Extracts raw text from Form 16 PDFs using PyMuPDF
- Sends to GPT-4o with a specialised extraction prompt
- Returns a structured `ParsedFormData` Pydantic model
- Falls back to demo data if no API key / invalid PDF

### 2. Deduction Finder Agent (`agents/deduction_finder_agent.py`)
- Takes parsed form data and queries ChromaDB for relevant tax rules
- Uses Claude 3.5 Sonnet to reason about claimed vs missed deductions
- Returns `DeductionResult` with HIGH/MEDIUM/LOW urgency tags
- Rule-based fallback ensures it always produces output

### 3. Regime Advisor Agent (`agents/regime_advisor_agent.py`)
- Uses **deterministic Python math** for 100% accurate tax calculations
- Tax slabs, rebate 87A, cess — all computed precisely
- GPT-4o generates the human-readable explanation only
- Returns `RegimeComparison` with breakeven analysis

### 4. Investment Recommender Agent (`agents/investment_recommender_agent.py`)
- GPT-4o generates personalised investment recommendations
- Respects risk profile (conservative / moderate / aggressive)
- Prioritises filling 80C gap, then NPS, then health insurance
- Rule-based fallback covers all risk profiles

### 5. Explainer Agent (`agents/explainer_agent.py`)
- Claude 3.5 Sonnet generates the plain-English summary
- Personalised with actual rupee amounts from user data
- Friendly, encouraging tone — like a knowledgeable friend

### 6. Chat Agent (`agents/chat_agent.py`)
- Multi-turn conversational Q&A
- Full tax analysis loaded as context for personalised answers
- Chat history stored in Redis (last 10 turns)
- Claude 3.5 Sonnet as primary model, GPT-4o as fallback

---

## LangGraph State Machine

```
START
  │
  ▼
parse_pdf_node         ← PyMuPDF + GPT-4o
  │
  ▼
find_deductions_node   ← ChromaDB RAG + Claude 3.5
  │
  ▼
compare_regimes_node   ← Python math + GPT-4o explanation
  │
  ▼
recommend_investments_node ← GPT-4o + risk profile
  │
  ▼
generate_report_node   ← Claude 3.5 (plain English summary)
  │
  ▼
END (state persisted to Redis)
```

---

## Data Flow

1. User uploads Form 16 PDF → `POST /api/v1/upload`
2. Session created with PDF bytes stored in Redis (base64)
3. User submits risk profile → `POST /api/v1/analyze/sync`
4. LangGraph pipeline executes all 5 nodes sequentially
5. Final state persisted to Redis as `AnalysisResult`
6. Frontend polls `GET /api/v1/results/{session_id}`
7. WebSocket at `/api/v1/ws/session/{session_id}` streams progress

---

## RAG Knowledge Base

The Deduction Finder Agent uses ChromaDB for semantic search over:

| Document | Content |
|----------|---------|
| `section_80c.txt` | All 80C instruments, limits, eligibility |
| `section_80d.txt` | Health insurance deduction rules |
| `hra_rules.txt` | HRA exemption calculation (3-method formula) |
| `new_regime_2024.txt` | New Tax Regime slabs, available deductions |
| `old_regime_slabs.txt` | Old Regime slabs, senior citizen rules |
| `budget_2025_changes.txt` | Budget 2025 updates, new slab proposals |

Documents are chunked (~800 chars, 150 overlap) and embedded using `text-embedding-3-small`.

---

## Technology Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Agent orchestration | LangGraph | State machine gives reliable, inspectable pipeline |
| PDF extraction | PyMuPDF | Fast, accurate, handles complex layouts |
| Tax math | Pure Python | Deterministic, auditable, 100% accurate |
| LLM routing | LiteLLM | Single interface for OpenAI + Anthropic |
| Vector DB | ChromaDB (local) | Zero setup for hackathon; swap to Pinecone for prod |
| Memory | Redis | Fast session storage, TTL-based auto-cleanup |
| Frontend state | Zustand | Lightweight, no boilerplate |
| API client | React Query | Caching, refetching, loading states |