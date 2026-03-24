"""
RAG Knowledge Base - Tax Rules & Regulations
"""

from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
from config import settings


class TaxKnowledgeBase:
    """
    RAG-based knowledge base for Indian tax rules
    """
    
    def __init__(self, persist_directory: str = "./data/vectorstore"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " "]
        )
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize or load existing vectorstore"""
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            # Create new vectorstore with tax knowledge
            self._create_knowledge_base()
    
    def _create_knowledge_base(self):
        """Create knowledge base from tax documents"""
        documents = self._load_tax_documents()
        splits = self.text_splitter.split_documents(documents)
        
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
    
    def _load_tax_documents(self) -> List[Document]:
        """Load tax knowledge documents"""
        documents = []
        
        # Tax Rules 2024-25
        tax_rules = """
## Indian Income Tax Rules FY 2024-25 (AY 2025-26)

### Tax Slabs - New Regime
| Income Range | Tax Rate |
|--------------|----------|
| Up to ₹3,00,000 | Nil |
| ₹3,00,001 - ₹7,00,000 | 5% |
| ₹7,00,001 - ₹10,00,000 | 10% |
| ₹10,00,001 - ₹12,00,000 | 15% |
| ₹12,00,001 - ₹15,00,000 | 20% |
| Above ₹15,00,000 | 30% |

### Tax Slabs - Old Regime (Below 60 years)
| Income Range | Tax Rate |
|--------------|----------|
| Up to ₹2,50,000 | Nil |
| ₹2,50,001 - ₹5,00,000 | 5% |
| ₹5,00,001 - ₹10,00,000 | 20% |
| Above ₹10,00,000 | 30% |

### Standard Deduction
- Old Regime: ₹50,000
- New Regime: ₹75,000 (increased from FY 2024-25)

### Section 87A Rebate
- New Regime: Full tax rebate if taxable income ≤ ₹7,00,000
- Old Regime: Rebate up to ₹12,500 if taxable income ≤ ₹5,00,000

### Health & Education Cess
- 4% on total tax + surcharge

### Surcharge (for high incomes)
- ₹50L - ₹1Cr: 10%
- ₹1Cr - ₹2Cr: 15%
- ₹2Cr - ₹5Cr: 25%
- Above ₹5Cr: 37% (capped at 25% for salary income in new regime)
"""
        documents.append(Document(
            page_content=tax_rules,
            metadata={"source": "tax_slabs", "year": "2024-25"}
        ))
        
        # Deductions
        deductions = """
## Section 80C Deductions (Max ₹1,50,000)

### Eligible Investments & Expenses:
1. **PPF (Public Provident Fund)**
   - Interest rate: 7.1% (Q1 FY25)
   - Lock-in: 15 years
   - Tax-free returns

2. **ELSS (Equity Linked Saving Scheme)**
   - Shortest lock-in: 3 years
   - Market-linked returns
   - Best for wealth creation

3. **Life Insurance Premium**
   - Premium up to 10% of sum assured
   - Must be in taxpayer's name or spouse/children

4. **NSC (National Savings Certificate)**
   - Interest rate: 7.7%
   - Lock-in: 5 years
   - Interest is taxable but qualifies for 80C

5. **Tax-Saving Fixed Deposit**
   - Lock-in: 5 years
   - Interest is taxable
   - Safe, guaranteed returns

6. **SCSS (Senior Citizen Savings Scheme)**
   - For 60+ years
   - Interest rate: 8.2%
   - Quarterly interest payout

7. **Sukanya Samriddhi Yojana**
   - For girl child (up to age 10)
   - Interest rate: 8.2%
   - Fully tax-free

8. **Home Loan Principal Repayment**
   - Part of EMI towards principal

9. **Children's Tuition Fees**
   - Max 2 children
   - Full-time education in India

10. **Stamp Duty & Registration**
    - On property purchase
    - One-time deduction

## Section 80CCD(1B) - NPS (Additional ₹50,000)

- Over and above ₹1.5 lakh of 80C
- Only for NPS Tier-1 account
- Total NPS benefit: ₹2 lakh (80C + 80CCD1B)

## Section 80D - Health Insurance

| Category | Limit |
|----------|-------|
| Self/Family (below 60) | ₹25,000 |
| Self/Family (above 60) | ₹50,000 |
| Parents (below 60) | ₹25,000 |
| Parents (above 60) | ₹50,000 |
| Preventive Health Checkup | ₹5,000 (within above limits) |

**Maximum 80D Deduction:**
- All below 60: ₹50,000
- Self senior + Parents senior: ₹1,00,000

## Section 80E - Education Loan Interest

- No upper limit
- Interest on loan for higher education
- Self, spouse, or children
- Deduction for 8 years or until interest paid

## Section 24(b) - Home Loan Interest

- Self-occupied: Max ₹2,00,000
- Let-out property: No limit (but loss from house property capped at ₹2L)

## Section 80G - Donations

- 100% deduction: PM Relief Fund, National Defence Fund
- 50% deduction: Most charitable organizations
- Limit: 10% of adjusted gross total income for most

## Section 80TTA/80TTB - Savings Interest

- 80TTA (below 60): Up to ₹10,000 on savings account interest
- 80TTB (60+): Up to ₹50,000 on all deposit interest

## HRA Exemption

Minimum of:
1. Actual HRA received
2. 50% of (Basic + DA) for metro / 40% for non-metro
3. Rent paid minus 10% of (Basic + DA)
"""
        documents.append(Document(
            page_content=deductions,
            metadata={"source": "deductions", "year": "2024-25"}
        ))
        
        # Investment Guide
        investments = """
## Tax-Saving Investment Guide FY 2024-25

### By Risk Profile

#### Low Risk (Conservative)
1. **PPF** - 7.1% guaranteed, 15-year lock-in
2. **SCSS** - 8.2% for seniors, 5-year term
3. **NSC** - 7.7% guaranteed, 5-year lock-in
4. **Tax-Saving FD** - 6-7%, 5-year lock-in

#### Medium Risk (Balanced)
1. **NPS** - Market-linked, 10-12% historical returns
2. **ELSS (Hybrid)** - Equity + Debt mix

#### High Risk (Aggressive)
1. **ELSS (Pure Equity)** - 12-15% historical returns
2. **Unit Linked Insurance Plans** - Market-linked

### By Liquidity Need

#### Need Money Within 3 Years
- ELSS (3-year lock-in) - ⭐ Best choice

#### Can Lock for 5 Years
- Tax-Saving FD
- NSC
- SCSS (for seniors)

#### Can Lock for 15+ Years
- PPF - Best risk-adjusted returns

### By Tax Efficiency

#### Fully Tax-Free (EEE)
- PPF
- ELSS (if held > 1 year, gains up to ₹1.25L tax-free)
- Sukanya Samriddhi

#### Taxable Interest
- NSC
- Tax-Saving FD
- SCSS

### Quick Recommendations by Salary

| Annual Salary | Recommended Mix |
|---------------|-----------------|
| Up to ₹5L | PPF only (₹1.5L) |
| ₹5L - ₹10L | PPF (₹1L) + ELSS (₹50K) + NPS (₹50K) |
| ₹10L - ₹20L | ELSS (₹1L) + NPS (₹50K) + PPF (₹50K) + 80D (₹25K) |
| Above ₹20L | Max all sections + Home loan if possible |
"""
        documents.append(Document(
            page_content=investments,
            metadata={"source": "investments", "year": "2024-25"}
        ))
        
        return documents
    
    async def search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Search knowledge base
        """
        if filter_metadata:
            results = self.vectorstore.similarity_search(
                query=query,
                k=k,
                filter=filter_metadata
            )
        else:
            results = self.vectorstore.similarity_search(
                query=query,
                k=k
            )
        return results
    
    async def get_relevant_context(
        self,
        query: str,
        k: int = 3
    ) -> str:
        """
        Get relevant context as string for prompts
        """
        docs = await self.search(query, k=k)
        context = "\n\n---\n\n".join([doc.page_content for doc in docs])
        return context


# Singleton
knowledge_base = TaxKnowledgeBase()