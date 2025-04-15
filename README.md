# 🚀 SHL Assessment Recommender 🚀

![Status](https://img.shields.io/badge/status-operational-brightgreen)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> **NOTE:** Demo URL of **streamlit** is recommended to open in a **browser where dark mode is enabled for better experience**

## 🔥 AI-Powered Tool for Optimal SHL Test Recommendations

### 💢 Problem
HR teams struggle to match job roles with relevant SHL assessments, causing inefficient hiring processes.

### 💡 Solution
AI-driven recommender that scrapes SHL's catalog, embeds descriptions via NLP, recommends tests through semantic search, and generates HR insights.

## ⚙️ Tech Stack

* **Backend:** FastAPI, Uvicorn
* **AI/ML:** ChromaDB, Sentence-Transformers
* **NLP:** Cohere API
* **Scraping:** BeautifulSoup, Requests
* **Frontend:** Streamlit
* **Deployment:** Render, Streamlit Cloud

## 🔄 Workflow

1. **Data Collection:** Scrape SHL's website → JSON (scraper.py)
2. **Vector DB:** Text to embeddings → ChromaDB (rag.py)
3. **API:** Process job descriptions → Return assessments (api.py)
4. **AI Insights:** Cohere analyzes assessments → Output skills/job fit
5. **UI:** Input job desc → Display ranked results + tips

## ✨ Key Features

- ✅ **Semantic Search:** Vector similarity matching
- ✅ **AI Insights:** Concise skill/fit summaries
- ✅ **Auto-Updates:** One-click catalog refreshing
- ✅ **Deployment-Ready:** Free hosting solution

## 🧠 Challenges & Solutions

* Multi-Level scraping
* Cohere's free-tier limits → Token capping
* ChromaDB path errors → Absolute paths in production

## 🌐 Try It

### API
**Endpoint:** [https://shl-assessment-recommendor.onrender.com/recommend](https://shl-assessment-recommendor.onrender.com/recommend)

**JSON input:**
```json
{"text": "We want to hire python expert !!"}
```

**JSON output:**
```json
{
  "name": "Python (New)",
  "url": "https://www.shl.com/solutions/products/product-catalog/view/python-new/",
  "score": 0.9339699149131775,
  "ai_insights": " 1. Key skills: Programming, databases, libraries\n \n2. Job level fit: Intermediate, experienced \n\n3. Usage tip: Prepare for the assessment ……"
}
```

### UI
**Demo:** [https://shl-assessment-recommendor-v75xtfd7tsh3rxqucbedlk.streamlit.app/](https://shl-assessment-recommendor-v75xtfd7tsh3rxqucbedlk.streamlit.app/)

## Screenshorts
![Screenshot from 2025-04-16 00-52-55](https://github.com/user-attachments/assets/c451f577-0c92-4f63-8fc8-d578cf57d7af)
![Screenshot from 2025-04-16 01-26-29](https://github.com/user-attachments/assets/3082a955-1450-4ed4-9864-752ae01ac6e2)
![Screenshot from 2025-04-16 01-26-34](https://github.com/user-attachments/assets/b308180b-ae17-4785-a5e4-c42703bff32e)
![Screenshot from 2025-04-16 01-26-46](https://github.com/user-attachments/assets/0141aaff-a5ef-44c4-a226-b4757abc4916)

## 💥 Impact
* 80% reduction in HR effort
* Globally scalable
* Revolutionary hiring optimization
