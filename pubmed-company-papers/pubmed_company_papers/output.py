"""Module for handling output of PubMed data to CSV."""

from typing import Dict, List, Optional, Any
import csv
import sys
import logging
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

class OutputHandler:
    """Class to handle output of PubMed data to CSV."""
    
    @staticmethod
    def create_csv(data: List[Dict[str, Any]], filename: Optional[str] = None, debug: bool = False) -> None:
        """
        Create a CSV file from the processed PubMed data.
        
        Args:
            data: List of dictionaries containing paper information
            filename: Optional filename to save the CSV to
            debug: Whether to print debug information
        """
        if not data:
            logger.warning("No data to output")
            return
        
        # Define CSV columns
        columns = [
            "PubmedID", 
            "Title", 
            "PublicationDate", 
            "Non-academicAuthor(s)", 
            "CompanyAffiliation(s)", 
            "CorrespondingAuthorEmail"
        ]
        
        try:
            # Create DataFrame
            df = pd.DataFrame(data)
            
            if debug:
                logger.debug(f"Created DataFrame with {len(df)} rows")
            
            if filename:
                # Save to file
                df.to_csv(filename, index=False)
                if debug:
                    logger.debug(f"Saved CSV to {filename}")
            else:
                # Print to console
                print(df.to_csv(index=False))
                
        except Exception as e:
            logger.error(f"Error creating CSV: {e}")
            raise
    
    @staticmethod
    def format_data_for_csv(
        pubmed_id: str,
        title: str,
        publication_date: str,
        company_authors: List[str],
        company_names: List[str],
        corresponding_email: str
    ) -> Dict[str, str]:
        """
        Format data for CSV output.
        
        Args:
            pubmed_id: PubMed ID
            title: Paper title
            publication_date: Publication date
            company_authors: List of company-affiliated authors
            company_names: List of company names
            corresponding_email: Corresponding author's email
            
        Returns:
            Dictionary with formatted data
        """
        return {
            "PubmedID": pubmed_id,
            "Title": title,
            "PublicationDate": publication_date,
            "Non-academicAuthor(s)": "; ".join(company_authors),
            "CompanyAffiliation(s)": "; ".join(company_names),
            "CorrespondingAuthorEmail": corresponding_email
        }