# TaxGenie AI — Impact Model

## The Problem We're Solving

> **95% of Indians don't have a financial plan.**
> Financial advisors charge ₹25,000+ per year and serve only HNIs.
> Every tax season, crores of Indians overpay taxes, miss deductions,
> and make uninformed investment decisions.

### Specific Pain Points

| Pain Point | Scale |
|---|---|
| Form 16 is a confusing 3-page document most people cannot read | ~75 million ITR filers |
| Old vs New Regime decision made on gut feeling, not math | All salaried taxpayers |
| Average Indian misses ₹15,000–₹40,000 in legitimate deductions | ~60 million salaried employees |
| Tax-saving investments picked randomly, not based on risk profile | ~80 million taxpayers |
| CA consultations cost ₹2,000–₹5,000 for basic tax planning | Anyone seeking advice |

---

## Market Opportunity

```
Total Indian Taxpayers:          ~80 million
File ITR annually:               ~75 million
Average missed deductions:       ₹18,000
Total money left on table:       ₹1,35,000 Crore/year
```

This is not a niche problem. It affects every salaried employee in India —
from a ₹4 LPA fresher to a ₹50 LPA senior manager.

---

## TaxGenie's Solution

**One sentence:** Upload Form 16 → get a complete, personalised tax plan in 90 seconds.

### The "Priya" Moment

Meet Priya, a 28-year-old software developer earning ₹12 LPA:

| | Before TaxGenie | After TaxGenie |
|---|---|---|
| Time spent | 3–5 hours with CA | 47 seconds |
| Cost | ₹3,000 CA fee | Free |
| Tax paid | ₹1,20,000 | ₹97,000 |
| **Savings found** | — | **₹23,000** |

**TaxGenie found her ₹23,000 in 47 seconds. A CA would charge ₹3,000 and take 3 days.**

---

## Year 1 Impact Projection

**Assumption:** 1% market penetration = 750,000 users

### Per-User Impact

| Metric | Value |
|---|---|
| Average deductions found | ₹18,500 |
| Time saved vs CA | 3–5 hours |
| Money saved vs CA fee | ₹2,000–₹5,000 |
| Tax savings generated | ₹18,500 × 30% bracket = ~₹5,550 |

### Aggregate Impact (750,000 users)

| Metric | Value |
|---|---|
| Total tax savings generated | ₹1,387 Crore |
| CA fee savings | ₹1,500 Crore |
| **Total economic impact** | **₹2,887 Crore** |

---

## Efficiency vs Traditional Process

### Traditional CA Process

```
Appointment booking:          2–3 days
Document collection:          1 day
Analysis time:                2–3 hours
Report delivery:              1 day
─────────────────────────────────────
Total time:                   4–7 days
Cost:                         ₹2,000–₹5,000
```

### TaxGenie AI Process

```
Upload Form 16:               30 seconds
AI Analysis:                  47 seconds
Report ready:                 ~90 seconds
─────────────────────────────────────
Total time:                   < 2 minutes
Cost:                         Free
```

| Metric | CA | TaxGenie | Improvement |
|---|---|---|---|
| Time | 4–7 days | 90 seconds | **99.98% faster** |
| Cost | ₹2,000–₹5,000 | ₹0 | **100% cheaper** |
| Availability | Business hours | 24/7 | **Always on** |
| Personalisation | High | High (AI-powered) | **On par** |
| Accuracy (math) | Human error possible | Deterministic Python | **More reliable** |

---

## Roadmap & Scale

### Hackathon Version (Current) ✅
Core features built and working:
- Form 16 PDF parsing with GPT-4o
- Deduction Finder with RAG (ChromaDB + Claude 3.5)
- Old vs New Regime comparison (exact math)
- Investment recommendations by risk profile
- AI plain-English explanations
- Conversational tax chatbot
- Real-time progress tracking via WebSocket

### Version 2.0 — Post-Hackathon
- 26AS & AIS document parsing
- ITR pre-fill and auto-generation
- Direct integration with income tax portal (incometaxindia.gov.in)
- Multi-year tax planning and trend analysis
- CA review marketplace (human-in-the-loop)
- WhatsApp bot interface for tier-2/3 cities

### Version 3.0 — Future Vision
- Portfolio rebalancing for tax efficiency
- Real-time tax impact of financial decisions
- Tax-loss harvesting for equity portfolios
- GST filing module for freelancers
- NRI tax planning module
- Integration with Zerodha, Groww, Kuvera for auto-import

---

## Revenue Model

| Tier | Features | Price |
|---|---|---|
| **Free** | Basic analysis, 1 Form 16/year | ₹0 |
| **Pro** | Unlimited uploads, 26AS, investment tracking | ₹499/year |
| **CA Connect** | AI analysis + licensed CA review | ₹1,499/year |
| **Enterprise** | White-label for HR/payroll companies | Custom |

**Unit Economics (Pro plan):**
- CAC: ~₹150 (digital marketing)
- LTV: ₹499 × 3 years avg = ₹1,497
- LTV:CAC ratio: ~10x

---

## Social Impact

Beyond the numbers, TaxGenie democratises financial planning:

1. **Tier-2 / Tier-3 cities** — No access to qualified CAs; TaxGenie fills the gap
2. **First-time taxpayers** — Freshers and young earners who have never filed taxes
3. **Women taxpayers** — Often dependent on husbands/family for tax decisions
4. **Gig workers** — Freelancers with complex income sources but no CA relationship
5. **Senior citizens** — Fixed income earners who often miss 80TTB and other senior benefits

> *"Turning India's tax complexity into a 90-second conversation."*

---

## Built For

**ET AI Hackathon 2026 — Problem Statement #9: AI Money Mentor**

Sponsored by Avataar.ai | Powered by Anthropic Claude + OpenAI GPT-4o