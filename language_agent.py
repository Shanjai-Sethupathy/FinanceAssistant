import logging
from langchain.llms import BaseLLM  # Abstract class for LLMs
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageAgent:
    

    def __init__(self, llm: BaseLLM):
        
        self.llm = llm
        self.memory = ConversationBufferMemory(memory_key="chat_history")  # Initialize memory

    def generate_market_brief(self, analysis_results: dict, earnings_surprises: dict) -> str:
        
        try:
            # Define a prompt template
            prompt_template = PromptTemplate(
                input_variables=["analysis_results", "earnings_surprises", "chat_history"],
                template="""
                    You are a financial analyst providing a morning market brief.
                    Here are the market analysis results:
                    {analysis_results}

                    Here are the earnings surprises:
                    {earnings_surprises}

                    Previous conversation:
                    {chat_history}

                    Synthesize a concise and informative narrative market brief, no more than 200 words.
                    Focus on the risk exposure in Asia tech stocks and any significant earnings surprises.
                    Use a neutral tone, but highlight any potential concerns or positive developments.
                    """
            )
            # Create a RetrievalQA chain (even if not strictly RAG here, useful structure)
            qa_chain = RetrievalQA.from_llm(
                llm=self.llm,
                prompt=prompt_template,
                memory=self.memory,  # Use the memory here
                verbose=True,  # Keep verbose for debugging
            )

            # Run the chain to generate the response
            result = qa_chain({"analysis_results": analysis_results, "earnings_surprises": earnings_surprises})
            return result["result"]
        except Exception as e:
            logger.error(f"Error generating market brief: {e}")
            return "I am unable to generate a market brief at this time."


if __name__ == "__main__":
    # Example Usage
    from langchain.llms import OpenAI
    llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0.7)  # Example: Use OpenAI

    language_agent = LanguageAgent(llm)
    market_brief = language_agent.generate_market_brief({}, {})
    print("\nMarket Brief:")
    print(market_brief)

    # Example of a second turn in the conversation
    market_brief2 = language_agent.generate_market_brief({}, {})
    print("\nMarket Brief - Second Turn:")
    print(market_brief2)
