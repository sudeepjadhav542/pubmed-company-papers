"""Module for parsing PubMed API responses."""

from typing import Dict, List, Optional, Tuple, Any
import logging
import re
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class PubMedParser:
    """Class to parse PubMed API responses."""
    
    @staticmethod
    def extract_publication_date(article: Dict[str, Any]) -> str:
        """
        Extract the publication date from a PubMed article.
        
        Args:
            article: PubMed article dictionary
            
        Returns:
            Publication date as a string (YYYY-MM-DD)
        """
        try:
            pub_date_info = article["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"]
            
            # Handle different date formats
            if "Year" in pub_date_info:
                year = pub_date_info.get("Year", "")
                month = pub_date_info.get("Month", "01")
                day = pub_date_info.get("Day", "01")
                
                # Convert month names to numbers
                if month.isalpha():
                    try:
                        month = datetime.strptime(month, "%b").month
                    except ValueError:
                        try:
                            month = datetime.strptime(month, "%B").month
                        except ValueError:
                            month = "01"
                
                # Ensure month and day are two digits
                month = str(month).zfill(2)
                day = str(day).zfill(2)
                
                return f"{year}-{month}-{day}"
            else:
                # Handle MedlineDate format (e.g., "2020 Jan-Feb")
                medline_date = pub_date_info.get("MedlineDate", "")
                if medline_date:
                    # Extract year
                    year_match = re.search(r'\d{4}', medline_date)
                    if year_match:
                        return f"{year_match.group(0)}-01-01"
            
            return "Unknown"
            
        except (KeyError, TypeError) as e:
            logger.warning(f"Error extracting publication date: {e}")
            return "Unknown"
    
    @staticmethod
    def extract_title(article: Dict[str, Any]) -> str:
        """
        Extract the title from a PubMed article.
        
        Args:
            article: PubMed article dictionary
            
        Returns:
            Article title
        """
        try:
            return article["MedlineCitation"]["Article"]["ArticleTitle"]
        except (KeyError, TypeError) as e:
            logger.warning(f"Error extracting title: {e}")
            return "Unknown"
    
    @staticmethod
    def extract_pubmed_id(article: Dict[str, Any]) -> str:
        """
        Extract the PubMed ID from a PubMed article.
        
        Args:
            article: PubMed article dictionary
            
        Returns:
            PubMed ID
        """
        try:
            return article["MedlineCitation"]["PMID"]
        except (KeyError, TypeError) as e:
            logger.warning(f"Error extracting PubMed ID: {e}")
            return "Unknown"
    
    @staticmethod
    def extract_authors_with_affiliations(article: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract authors and their affiliations from a PubMed article.
        
        Args:
            article: PubMed article dictionary
            
        Returns:
            List of dictionaries containing author information
        """
        authors_info = []
        
        try:
            author_list = article["MedlineCitation"]["Article"]["AuthorList"]
            
            for author in author_list:
                if "Author" in author:
                    author = author["Author"]
                
                # Skip if not a valid author
                if not isinstance(author, dict):
                    continue
                
                # Extract author name
                last_name = author.get("LastName", "")
                fore_name = author.get("ForeName", "")
                initials = author.get("Initials", "")
                
                full_name = f"{last_name}, {fore_name}" if fore_name else last_name
                if not full_name and initials:
                    full_name = initials
                
                # Extract affiliations
                affiliations = []
                
                # Handle different affiliation formats
                if "AffiliationInfo" in author:
                    for affiliation in author["AffiliationInfo"]:
                        if "Affiliation" in affiliation:
                            affiliations.append(affiliation["Affiliation"])
                elif "Affiliation" in author:
                    if isinstance(author["Affiliation"], list):
                        for affiliation in author["Affiliation"]:
                            if isinstance(affiliation, dict) and "Affiliation" in affiliation:
                                affiliations.append(affiliation["Affiliation"])
                            elif isinstance(affiliation, str):
                                affiliations.append(affiliation)
                    elif isinstance(author["Affiliation"], str):
                        affiliations.append(author["Affiliation"])
                
                # Extract email
                email = ""
                for affiliation in affiliations:
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', affiliation)
                    if email_match:
                        email = email_match.group(0)
                        break
                
                # Check if corresponding author
                is_corresponding = False
                if "ValidYN" in author and author["ValidYN"] == "Y":
                    if "EqualContrib" in author and author["EqualContrib"] == "Y":
                        is_corresponding = True
                
                authors_info.append({
                    "name": full_name,
                    "affiliations": affiliations,
                    "email": email,
                    "is_corresponding": is_corresponding
                })
            
            return authors_info
            
        except (KeyError, TypeError) as e:
            logger.warning(f"Error extracting authors: {e}")
            return []
    
    @staticmethod
    def extract_corresponding_author_email(article: Dict[str, Any]) -> str:
        """
        Extract the corresponding author's email from a PubMed article.
        
        Args:
            article: PubMed article dictionary
            
        Returns:
            Corresponding author's email
        """
        authors = PubMedParser.extract_authors_with_affiliations(article)
        
        # First check for explicitly marked corresponding authors
        for author in authors:
            if author["is_corresponding"] and author["email"]:
                return author["email"]
        
        # If no corresponding author is marked, return the first email found
        for author in authors:
            if author["email"]:
                return author["email"]
        
        return "Unknown"