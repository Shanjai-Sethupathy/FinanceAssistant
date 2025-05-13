# AI Tool Usage Log

This document provides a log of the AI-tool prompts, code generation steps, and model parameters used in this project.

## 1. Prompt History

### Initial Setup

* Generate a FastAPI orchestrator for a finance assistant application with separate agents for voice, API, retriever, analysis, and language processing.
* Create VoiceAgent for text-to-speech and speech-to-text.
* Implement APIAgent for market data retrieval.
* Develop RetrieverAgent for document retrieval and relevance ranking.
* Build AnalysisAgent for financial data analysis.
* Add LanguageAgent for natural language response generation.

### Refinement Requests

* Add error handling and confidence checks for low-confidence retrievals.
* Enhance logging for orchestrator routing decisions.
* Set minimum confidence threshold for document retrieval.

### Final Optimization

* Simplify code structure and reduce processing latency.
* Streamline dependency injection for agent instantiation.
* Optimize sleep delays to improve response time.

## 2. Code Generation Steps

### Core Files Created

* Create `orchestrator.py`: Main FastAPI entry point for the application.
* Develop `voice_agent.py`: Handles voice input/output.
* Implement `api_agent.py`: Fetches market data.
* Build `retriever_agent.py`: Retrieves and ranks financial filings.
* Design `analysis_agent.py`: Analyzes market and text data.
* Add `language_agent.py`: Generates final text responses.

### Key Implementations

* Design orchestrator with route-specific logic for market data and filings.
* Integrate background tasks for non-blocking voice output.
* Optimize data structures for reduced memory usage.

## 3. Model Parameters

### Whisper Model

* Use OpenAI Whisper (via `whisper` Python package)
* Set Model: `base.en`
* Configure Language: English
* Set Beam Size: 5

### Language Model

* Use GPT-based language model
* Set Model Size: 4.5
* Configure Temperature: 0.7
* Set Top-p: 0.9

### Analysis Logic

* Apply simple statistical summaries and word count analysis.
* Optimize latency through lazy loading and caching.

## 4. Future Improvements

* Incorporate embeddings for more context-aware retrieval.
* Experiment with lightweight models for faster TTS.
* Add memory management for long-running sessions.
