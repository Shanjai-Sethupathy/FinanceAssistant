import requests
from bs4 import BeautifulSoup
import PyPDF2
import logging
from typing import List, Optional
import io


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingAgent:
    def __init__(self, user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"):
        self.user_agent = user_agent

    def _fetch_document(self, url: str) -> Optional[bytes]:
        try:
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching document from {url}: {e}")
            return None

    def _parse_html(self, html_content: bytes) -> Optional[BeautifulSoup]:
        try:
            return BeautifulSoup(html_content, "html.parser")
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return None

    def _extract_text_from_pdf(self, pdf_content: bytes) -> Optional[str]:
        try:
            # Use PyPDF2 first
            pdf_file = io.BytesIO(pdf_content)
            reader = PyPDF2.PdfReader(pdf_file)
            text = "".join(page.extract_text() or "" for page in reader.pages)
            if text.strip():
                return text.strip()

            # Fallback to unstructured if installed
            try:
                from unstructured.partition.pdf import partition_pdf
                elements = partition_pdf(file=pdf_file)
                text = "\n\n".join(str(el) for el in elements)
                return text.strip()
            except ImportError:
                logger.error("Unstructured is not installed. Please install it for better PDF extraction.")
                return None
            except Exception as e:
                logger.error(f"Error extracting text from PDF with Unstructured: {e}")
                return None
        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"Error reading PDF with PyPDF2: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error extracting text from PDF: {e}")
            return None

    def _extract_data_from_html(self, soup: BeautifulSoup) -> dict:
        try:
            title = soup.title.string.strip() if soup.title else "Untitled Document"
            paragraphs = "\n".join([p.text.strip() for p in soup.find_all("p")])
            return {"title": title, "content": paragraphs}
        except Exception as e:
            logger.error(f"Error extracting data from HTML: {e}")
            return {"title": "Error", "content": str(e)}

    def _extract_data_from_text(self, text: str) -> dict:
        try:
            return {"text_data": text.strip()}
        except Exception as e:
            logger.error(f"Error extracting data from text: {e}")
            return {"text_data": str(e)}

    def scrape_filing(self, url: str) -> Optional[dict]:
        document_content = self._fetch_document(url)
        if document_content is None:
            return None

        if url.lower().endswith(".html") or url.lower().endswith(".htm"):
            soup = self._parse_html(document_content)
            if soup is None:
                return None
            return self._extract_data_from_html(soup)
        elif url.lower().endswith(".pdf"):
            text = self._extract_text_from_pdf(document_content)
            if text is None:
                return None
            return self._extract_data_from_text(text)
        else:
            logger.warning(f"Unsupported file type for URL: {url}")
            return None

    def scrape_filings(self, urls: List[str]) -> List[Optional[dict]]:
        return [self.scrape_filing(url) for url in urls]

# Example Usage
if __name__ == "__main__":
    agent = ScrapingAgent()
    filing_urls = [
    "https://www.sec.gov/Archives/edgar/data/320193/000032019323000010/aapl-20230930.htm",  # Apple 10-K
    "https://www.sec.gov/Archives/edgar/data/789019/000078901923000010/msft-20230630.htm",  # Microsoft 10-Q
    "https://www.sec.gov/Archives/edgar/data/1318605/000131860523000024/tsla-20221231.pdf",  # Tesla 10-K
    "https://www.sec.gov/Archives/edgar/data/1652044/000165204423000032/googl-20230930.pdf",  # Alphabet 10-Q
    "https://www.sec.gov/Archives/edgar/data/1018724/000101872423000004/amzn-20221231.htm",  # Amazon 10-K
]

# Add more URLs for market news or API requests as needed.

    extracted_data = agent.scrape_filings(filing_urls)
    for i, data in enumerate(extracted_data):
        print(f"\nData from {filing_urls[i]}:")
        if data:
            print(data)
        else:
            print("Failed to scrape.")
