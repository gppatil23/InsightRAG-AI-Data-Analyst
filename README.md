# InsightRAG — AI Data Analyst Copilot

Local-first Streamlit app to upload CSV/Excel files, inspect data quality and statistics, and ask questions with Gemini.

## Setup (Windows)
```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```
Add your Gemini API key to `.env`. Never commit it.

This is the starter milestone. Next we will add controlled Pandas analysis tools, local embeddings + FAISS retrieval, chart generation, and answer evaluation. The initial Q&A uses a dataset profile and sample rows; it does not yet execute exact calculations for arbitrary questions.
