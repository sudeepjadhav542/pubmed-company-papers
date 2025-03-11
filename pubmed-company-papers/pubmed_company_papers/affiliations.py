"""Module for analyzing author affiliations to identify company affiliations."""

from typing import Dict, List, Set, Tuple, Any
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)

class AffiliationAnalyzer:
    """Class to analyze author affiliations and identify company affiliations."""
    
    # Keywords that indicate academic institutions
    ACADEMIC_KEYWORDS = {
        'university', 'college', 'institute', 'school', 'academy', 'faculty',
        'department', 'dept', 'laboratory', 'lab', 'center', 'centre',
        'hospital', 'clinic', 'medical center', 'research center',
        'national', 'federal', 'government', 'ministry'
    }
    
    # Keywords that indicate commercial/company affiliations
    COMPANY_KEYWORDS = {
        'inc', 'inc.', 'incorporated', 'corp', 'corp.', 'corporation',
        'llc', 'ltd', 'limited', 'co', 'co.', 'company', 'gmbh', 'ag', 'sa',
        'bv', 'holdings', 'pharmaceuticals', 'pharma', 'biotech',
        'therapeutics', 'biosciences', 'laboratories', 'labs', 'diagnostics'
    }
    
    # Email domains that typically indicate academic institutions
    ACADEMIC_EMAIL_DOMAINS = {
        'edu', 'ac.uk', 'ac.jp', 'edu.au', 'ac.nz', 'edu.cn', 'edu.sg',
        'edu.hk', 'ac.ir', 'ac.kr', 'edu.tw', 'edu.in', 'ac.za'
    }
    
    @classmethod
    def is_company_affiliation(cls, affiliation: str) -> bool:
        """
        Determine if an affiliation is likely to be a company.
        
        Args:
            affiliation: Affiliation string
            
        Returns:
            True if the affiliation is likely a company, False otherwise
        """
        if not affiliation:
            return False
        
        # Convert to lowercase for case-insensitive matching
        affiliation_lower = affiliation.lower()
        
        # Check for company keywords
        for keyword in cls.COMPANY_KEYWORDS:
            # Use word boundaries to avoid partial matches
            if re.search(r'\b' + re.escape(keyword) + r'\b', affiliation_lower):
                return True
        
        # Check for academic keywords (negative indicator)
        for keyword in cls.ACADEMIC_KEYWORDS:
            if re.search(r'\b' + re.escape(keyword) + r'\b', affiliation_lower):
                return False
        
        # Check for email domains
        email_match = re.search(r'[\w\.-]+@([\w\.-]+)', affiliation_lower)
        if email_match:
            domain = email_match.group(1)
            
            # Check if it's an academic domain
            for academic_domain in cls.ACADEMIC_EMAIL_DOMAINS:
                if domain.endswith(academic_domain):
                    return False
            
            # If it has a commercial TLD and not an academic domain, it might be a company
            if domain.endswith('.com') or domain.endswith('.co'):
                return True
        
        # Default to False if no clear indicators
        return False
    
    @classmethod
    def extract_company_name(cls, affiliation: str) -> str:
        """
        Extract the company name from an affiliation string.
        
        Args:
            affiliation: Affiliation string
            
        Returns:
            Extracted company name or the original affiliation if extraction fails
        """
        if not affiliation:
            return ""
        
        # Try to extract company name using common patterns
        
        # Pattern 1: Company name followed by Inc./Corp./etc.
        company_suffix_pattern = r'([\w\s\-&]+)\s+(Inc\.|Corp\.|LLC|Ltd\.|GmbH|AG|SA|BV|Holdings|Pharmaceuticals|Pharma|Biotech)'
        match = re.search(company_suffix_pattern, affiliation, re.IGNORECASE)
        if match:
            return match.group(0).strip()
        
        # Pattern 2: Email domain might indicate company name
        email_match = re.search(r'[\w\.-]+@([\w\.-]+)\.com', affiliation, re.IGNORECASE)
        if email_match:
            domain = email_match.group(1)
            # Convert domain to a readable company name
            company_name = domain.replace('-', ' ').replace('.', ' ')
            return f"{company_name.title()} Inc."
        
        # If no patterns match, return a cleaned version of the affiliation
        # Remove email addresses
        cleaned = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', affiliation)
        # Remove postal addresses
        cleaned = re.sub(r'\b\d{5}\b|\b\d{5}-\d{4}\b', '', cleaned)
        
        return cleaned.strip()
    
    @classmethod
    def identify_company_authors(cls, authors: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """
        Identify authors affiliated with companies.
        
        Args:
            authors: List of author dictionaries with affiliations
            
        Returns:
            Tuple containing (list of company-affiliated author names, list of company names)
        """
        company_authors = []
        company_names = set()
        
        for author in authors:
            has_company_affiliation = False
            
            for affiliation in author.get("affiliations", []):
                if cls.is_company_affiliation(affiliation):
                    has_company_affiliation = True
                    company_name = cls.extract_company_name(affiliation)
                    if company_name:
                        company_names.add(company_name)
            
            if has_company_affiliation:
                company_authors.append(author["name"])
        
        return company_authors, list(company_names)