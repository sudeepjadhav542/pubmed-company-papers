"""Command-line interface for the PubMed Company Papers tool."""

import argparse
import logging
import sys
from typing import List, Dict, Any, Optional
from tqdm import tqdm

from pubmed_company_papers.api import PubMedAPI
from pubmed_company_papers.parser import PubMedParser
from pubmed_company_papers.affiliations import AffiliationAnalyzer
from pubmed_company_papers.output import OutputHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Fetch research papers from PubMed with authors affiliated with pharmaceutical or biotech companies."
    )
    
    parser.add_argument(
        "query",
        help="PubMed search query"
    )
    
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Print debug information during execution"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="Specify the filename to save the results (if not provided, print to console)"
    )
    
    parser.add_argument(
        "-m", "--max-results",
        type=int,
        default=100,
        help="Maximum number of results to fetch (default: 100)"
    )
    
    parser.add_argument(
        "-e", "--email",
        default="user@example.com",
        help="Email address to identify yourself to NCBI (required by their API)"
    )
    
    parser.add_argument(
        "-k", "--api-key",
        help="NCBI API key for higher request limits"
    )
    
    return parser.parse_args()

def process_articles(articles: List[Dict[str, Any]], debug: bool = False) -> List[Dict[str, Any]]:
    """
    Process PubMed articles to extract relevant information.
    
    Args:
        articles: List of PubMed articles
        debug: Whether to print debug information
        
    Returns:
        List of processed article data
    """
    results = []
    
    for article in tqdm(articles, desc="Processing articles", disable=not debug):
        # Extract basic information
        pubmed_id = PubMedParser.extract_pubmed_id(article)
        title = PubMedParser.extract_title(article)
        publication_date = PubMedParser.extract_publication_date(article)
        
        # Extract authors and affiliations
        authors = PubMedParser.extract_authors_with_affiliations(article)
        
        # Identify company-affiliated authors
        company_authors, company_names = AffiliationAnalyzer.identify_company_authors(authors)
        
        # Only include papers with at least one company-affiliated author
        if company_authors:
            # Extract corresponding author email
            corresponding_email = PubMedParser.extract_corresponding_author_email(article)
            
            # Format data for CSV
            result = OutputHandler.format_data_for_csv(
                pubmed_id=pubmed_id,
                title=title,
                publication_date=publication_date,
                company_authors=company_authors,
                company_names=company_names,
                corresponding_email=corresponding_email
            )
            
            results.append(result)
    
    return results

def main() -> None:
    """Main function to run the command-line tool."""
    # Parse arguments
    args = parse_arguments()
    
    # Set up logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    try:
        # Initialize PubMed API
        pubmed_api = PubMedAPI(
            email=args.email,
            api_key=args.api_key
        )
        
        # Search PubMed
        logger.info(f"Searching PubMed for: {args.query}")
        pmids = pubmed_api.search(args.query, retmax=args.max_results, debug=args.debug)
        
        if not pmids:
            logger.warning("No results found for the query")
            sys.exit(0)
        
        logger.info(f"Found {len(pmids)} articles, fetching details...")
        
        # Fetch article details
        articles = pubmed_api.fetch_articles_batch(pmids, debug=args.debug)
        
        # Process articles
        logger.info("Processing articles to identify company affiliations...")
        results = process_articles(articles, debug=args.debug)
        
        # Output results
        if results:
            logger.info(f"Found {len(results)} articles with company-affiliated authors")
            OutputHandler.create_csv(results, args.file, args.debug)
            logger.info("Done!")
        else:
            logger.warning("No articles with company-affiliated authors found")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()