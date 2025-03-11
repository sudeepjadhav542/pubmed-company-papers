"""Module for interacting with the PubMed API."""

from typing import Dict, List, Optional, Union
import time
import logging
from Bio import Entrez

# Configure logging
logger = logging.getLogger(__name__)

class PubMedAPI:
    """Class to handle interactions with the PubMed API."""
    
    def __init__(self, email: str, tool: str = "PubMedCompanyPapers", api_key: Optional[str] = None):
        """
        Initialize the PubMed API handler.
        
        Args:
            email: Email address to identify yourself to NCBI
            tool: Name of the tool/application
            api_key: Optional NCBI API key for higher request limits
        """
        self.email = email
        self.tool = tool
        self.api_key = api_key
        
        # Set up Entrez
        Entrez.email = email
        Entrez.tool = tool
        if api_key:
            Entrez.api_key = api_key
            
        logger.debug(f"Initialized PubMed API with email: {email}")
    
    def search(self, query: str, retmax: int = 100, debug: bool = False) -> List[str]:
        """
        Search PubMed for articles matching the query.
        
        Args:
            query: PubMed search query
            retmax: Maximum number of results to return
            debug: Whether to print debug information
            
        Returns:
            List of PubMed IDs matching the query
        """
        if debug:
            logger.debug(f"Searching PubMed with query: {query}")
        
        try:
            # Search for articles
            handle = Entrez.esearch(db="pubmed", term=query, retmax=retmax)
            record = Entrez.read(handle)
            handle.close()
            
            pmids = record["IdList"]
            
            if debug:
                logger.debug(f"Found {len(pmids)} articles")
                
            return pmids
        
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            raise
    
    def fetch_details(self, pmids: List[str], debug: bool = False) -> Dict:
        """
        Fetch detailed information for a list of PubMed IDs.
        
        Args:
            pmids: List of PubMed IDs
            debug: Whether to print debug information
            
        Returns:
            Dictionary containing the fetched article details
        """
        if not pmids:
            logger.warning("No PubMed IDs provided to fetch_details")
            return {}
        
        if debug:
            logger.debug(f"Fetching details for {len(pmids)} articles")
        
        try:
            # Fetch article details
            handle = Entrez.efetch(db="pubmed", id=",".join(pmids), retmode="xml")
            articles = Entrez.read(handle)
            handle.close()
            
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching article details: {e}")
            raise
    
    def fetch_articles_batch(self, pmids: List[str], batch_size: int = 50, 
                            sleep_time: float = 0.5, debug: bool = False) -> List[Dict]:
        """
        Fetch article details in batches to avoid overloading the API.
        
        Args:
            pmids: List of PubMed IDs
            batch_size: Number of articles to fetch in each batch
            sleep_time: Time to sleep between batches (seconds)
            debug: Whether to print debug information
            
        Returns:
            List of article details
        """
        all_articles = []
        
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i+batch_size]
            
            if debug:
                logger.debug(f"Fetching batch {i//batch_size + 1}/{(len(pmids)-1)//batch_size + 1}")
            
            try:
                handle = Entrez.efetch(db="pubmed", id=",".join(batch), retmode="xml")
                record = Entrez.read(handle)
                handle.close()
                
                # Extract articles from the response
                if "PubmedArticle" in record:
                    all_articles.extend(record["PubmedArticle"])
                
                # Sleep to avoid overloading the API
                if i + batch_size < len(pmids):
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"Error fetching batch {i//batch_size + 1}: {e}")
                # Continue with the next batch instead of failing completely
                continue
        
        if debug:
            logger.debug(f"Fetched details for {len(all_articles)} articles")
            
        return all_articles