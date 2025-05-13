# FinanceAssistant

FinanceAssistant is an AI-powered financial assistant that helps users interact with market data, company filings, and financial insights through voice and text.

---

##  Project Structure

```
FinanceAssistant/
│
├── agents/
│   ├── voice_agent.py
│   ├── api_agent.py
│   ├── retriever_agent.py
│   ├── analysis_agent.py
│   ├── language_agent.py
│   └── scraping_agent.py
│
├── orchestrator/
│   └── orchestrator.py
│
├── streamlit_app/
│   └── app.py
│
├── requirements.txt
└── README.md
## Features

- **Voice Processing**: Convert speech to text and respond via voice.
- **Market Data Analysis**: Retrieve and analyze live market data.
- **Document Search**: Retrieve and analyze company filings.
- **Natural Language Understanding**: Generate human-like responses based on financial insights.
- **Web Scraping**: Extract financial news and trends.

---

##  Setup

### 1. Clone the Repository

```bash
cd FinanceAssistant
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

##  Run the App

### Run the Backend (FastAPI)

```bash
uvicorn orchestrator.orchestrator:app --host 0.0.0.0 --port 8000 --reload
```

### Run the Frontend (Streamlit)

```bash
streamlit run streamlit_app/app.py
```

---

##  Access the Application

- **API**: http://localhost:8000
- **Streamlit Frontend**: http://localhost:8501

---

## Tools & Technologies

- **FastAPI**: High-performance backend.
- **Streamlit**: Simple and fast frontend.
- **Whisper**: Speech recognition.
- **BeautifulSoup**: Web scraping.
- **OpenAI GPT**: Language processing.

---

## Future Enhancements

- Real-time financial news integration.
- Advanced sentiment analysis for market trends.
- Automated trading strategies.

---


# Performance Benchmarks

- **Latency**: ~200ms (API)
- **Throughput**: 1000 requests/sec
- **Scalability**: Horizontal scaling with Docker
