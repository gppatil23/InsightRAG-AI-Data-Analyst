
# InsightRAG — AI Data Analyst

InsightRAG is an AI-powered data analysis assistant that helps users explore and understand CSV and Excel datasets using natural-language questions. It combines Large Language Models (LLMs) with controlled Pandas analysis tools to generate insights based on actual data calculations.

Unlike domain-specific analytics applications, InsightRAG is designed to work with **different types of datasets** — including student, employee, customer, healthcare, sports, and other tabular data.

The goal is to make data analysis more accessible by allowing users to interact with their datasets through a conversational interface.

## Features

- **CSV and Excel Upload:** Upload datasets in CSV, XLSX, and XLS formats.
- **Automatic Dataset Profiling:** Identify column names, data types, unique values, sample values, and missing data.
- **Data Quality Analysis:** Detect missing values and duplicate records.
- **Dataset Preview:** Explore uploaded data through an interactive table.
- **Descriptive Statistics:** View statistical summaries of numeric columns.
- **Natural Language Querying:** Ask questions about datasets using plain English.
- **LangChain Tool Calling:** Allow the LLM to select appropriate analysis tools based on the user's question.
- **Pandas-Powered Analysis:** Perform aggregations, filtering, sorting, and correlation calculations using actual dataset values.
- **Dynamic Column Handling:** Analyze datasets without hardcoding domain-specific column names.
- **Conversational Interface:** Ask follow-up questions within the current Streamlit session.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web interface |
| Pandas | Data loading and analysis |
| NumPy | Numerical computations |
| LangChain | LLM orchestration and tool calling |
| Google Gemini | Natural-language understanding and response generation |
| python-dotenv | Environment variable management |

## How It Works

1. The user uploads a CSV or Excel dataset.
2. InsightRAG loads the data into a Pandas DataFrame.
3. The dataset analyzer generates a profile containing column names, data types, sample values, and data quality information.
4. The user asks a question in natural language.
5. LangChain provides the LLM with the dataset profile and available analysis tools.
6. The LLM selects a suitable tool and provides its arguments.
7. The selected tool performs calculations directly on the uploaded dataset.
8. The LLM explains the calculated result in a clear, human-readable response.

For numerical questions, InsightRAG uses controlled analytical functions instead of relying on the LLM to guess values or execute arbitrary Python code.

## Available Analysis Tools

### Group-by Analysis
Aggregate a numeric column by another column using operations such as:
- Sum
- Mean
- Count
- Minimum
- Maximum

### Dataset Filtering
Filter records using supported conditions such as:
- Equals
- Not equals
- Greater than
- Less than
- Contains

### Dataset Sorting
Sort records by a selected column to identify highest, lowest, or relevant entries.

### Correlation Analysis
Calculate correlations between numeric columns to explore relationships within the dataset.

### Column Summary
Inspect a column's data type, missing values, unique values, and frequently occurring values.

These tools use dynamic column names, allowing InsightRAG to adapt to different datasets.

## Example Questions

InsightRAG can answer questions based on the columns available in the uploaded dataset.

Examples:

- Which department has the highest average marks?
- Show records where a numeric value is greater than a given threshold.
- Which category has the highest average value?
- Sort the dataset by a selected column.
- Which numeric columns are correlated?
- What are the most frequent values in a column?
- How many missing values are present in the dataset?

## Project Structure

```text
InsightRAG/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── services/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── dataset_analyzer.py
│   ├── analysis_tools.py
│   └── llm_analyst.py
└── test_analysis.py
```

*The project structure may evolve as new features are added.*

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/gppatil23/InsightRAG.git
cd InsightRAG
```

### 2. Create a Virtual Environment

For Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file using the provided `.env.example` template.

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Replace the placeholder with your Gemini API key.

**Important:** Never commit your `.env` file or expose your API key on GitHub.

### 5. Run the Application

```bash
streamlit run app.py
```

The application will start locally and provide a URL to open InsightRAG in your browser.

## Current Scope and Limitations

- InsightRAG analyzes the dataset currently uploaded in the application.
- The available analysis tools support a defined set of operations.
- Questions requiring unsupported operations may need to be rephrased.
- Column type detection may require refinement for unusual or ambiguous datasets.
- LLM responses depend on the configured Gemini model and API availability.
- The complete RAG pipeline with embeddings and vector-based retrieval is still under development.
- Interactive visualization charts are planned but are not implemented yet.

## Roadmap

- [ ] Implement a complete RAG pipeline using embeddings and vector search.
- [ ] Add local embedding models to reduce dependence on embedding API quotas.
- [ ] Add interactive charts and data visualizations.
- [ ] Improve date detection and time-based analysis.
- [ ] Add answer verification and supporting evidence.
- [ ] Evaluate tool selection and answer correctness using a test dataset.
- [ ] Improve performance for larger datasets.
- [ ] Add export options for analysis results.

## Security and Responsible Use

InsightRAG uses predefined analysis tools rather than allowing the LLM to execute arbitrary Python code. This provides a more controlled approach to data analysis.

However, uploaded datasets should still be handled carefully. Avoid uploading confidential, personally identifiable, or sensitive information when dataset context may be sent to an external LLM API.

## Learning Outcomes

This project demonstrates practical experience with:

- LLM application development
- LangChain tool calling
- Data profiling and exploratory data analysis
- Data manipulation using Pandas and NumPy
- Prompt engineering and structured tool execution
- Building interactive applications with Streamlit
- Designing a foundation for Retrieval-Augmented Generation (RAG)

## Author

**Gaurav Patil**

- Portfolio: [gauravpatil23.netlify.app](https://gauravpatil23.netlify.app)
- GitHub: [gppatil23](https://github.com/gppatil23)

---

*InsightRAG is an evolving project. Features listed in the roadmap are planned enhancements and are not yet part of the current implementation.*
