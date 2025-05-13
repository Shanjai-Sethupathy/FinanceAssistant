from agents.voice_agent import VoiceAgent
from agents.api_agent import AlphaVantageAgent
from agents.retriever_agent import BaseRetriever
from agents.analysis_agent import AnalysisAgent
from agents.scraping_agent import ScrapingAgent
from agents.language_agent import LanguageAgent
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()
alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
load_dotenv()
openai_api = os.getenv("OPENAI_API_KEY")


class Orchestrator:
    def __init__(self):
        self.voice_agent = VoiceAgent()
        self.api_agent = AlphaVantageAgent()
        self.retriever_agent = BaseRetriever()
        self.analysis_agent = AnalysisAgent(alpha_vantage_api_key)
        self.scraping_agent = ScrapingAgent()
        self.language_agent = LanguageAgent()

    def handle_query(self, query):
        if "market data" in query:
            market_data = self.api_agent.get_market_data("AAPL")
            analysis_results = self.analysis_agent.analyze_market_data([market_data])
            response = self.language_agent.generate_response(analysis_results)
        elif "filings" in query:
            filings = self.retriever_agent.get_relevant_filings(query)
            analysis_results = self.analysis_agent.analyze_filings(filings)
            response = self.language_agent.generate_response(analysis_results)
        else:
            response = "Sorry, I couldn't understand your request."
        
        self.voice_agent.tts(response)
        return response
