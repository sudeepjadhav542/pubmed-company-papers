"""Tests for the parser module."""

import unittest
from unittest.mock import patch, MagicMock
import json

from pubmed_company_papers.parser import PubMedParser

class TestPubMedParser(unittest.TestCase):
    """Test cases for the PubMedParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample article data
        self.article = {
            "MedlineCitation": {
                "PMID": "12345",
                "Article": {
                    "ArticleTitle": "Test Article",
                    "Journal": {
                        "JournalIssue": {
                            "PubDate": {
                                "Year": "2023",
                                "Month": "01",
                                "Day": "15"
                            }
                        }
                    },
                    "AuthorList": [
                        {
                            "Author": {
                                "LastName": "Smith",
                                "ForeName": "John",
                                "Initials": "J",
                                "AffiliationInfo": [
                                    {"Affiliation": "Harvard University, Boston, MA, USA"}
                                ]
                            }
                        },
                        {
                            "Author": {
                                "LastName": "Doe",
                                "ForeName": "Jane",
                                "Initials": "J",
                                "AffiliationInfo": [
                                    {"Affiliation": "Pfizer Inc., New York, NY, USA jane.doe@pfizer.com"}
                                ]
                            }
                        }
                    ]
                }
            }
        }
    
    def test_extract_publication_date(self):
        """Test the extract_publication_date method."""
        # Test with standard date format
        date = PubMedParser.extract_publication_date(self.article)
        self.assertEqual(date, "2023-01-15")
        
        # Test with month name
        article_copy = self.article.copy()
        article_copy["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"] = {
            "Year": "2023",
            "Month": "Jan"
        }
        date = PubMedParser.extract_publication_date(article_copy)
        self.assertEqual(date, "2023-01-01")
        
        # Test with MedlineDate format
        article_copy = self.article.copy()
        article_copy["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"] = {
            "MedlineDate": "2023 Jan-Feb"
        }
        date = PubMedParser.extract_publication_date(article_copy)
        self.assertEqual(date, "2023-01-01")
        
        # Test with missing data
        article_copy = self.article.copy()
        del article_copy["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"]
        date = PubMedParser.extract_publication_date(article_copy)
        self.assertEqual(date, "Unknown")
    
    def test_extract_title(self):
        """Test the extract_title method."""
        title = PubMedParser.extract_title(self.article)
        self.assertEqual(title, "Test Article")
        
        # Test with missing title
        article_copy = self.article.copy()
        del article_copy["MedlineCitation"]["Article"]["ArticleTitle"]
        title = PubMedParser.extract_title(article_copy)
        self.assertEqual(title, "Unknown")
    
    def test_extract_pubmed_id(self):
        """Test the extract_pubmed_id method."""
        pmid = PubMedParser.extract_pubmed_id(self.article)
        self.assertEqual(pmid, "12345")
        
        # Test with missing PMID
        article_copy = self.article.copy()
        del article_copy["MedlineCitation"]["PMID"]
        pmid = PubMedParser.extract_pubmed_id(article_copy)
        self.assertEqual(pmid, "Unknown")
    
    def test_extract_authors_with_affiliations(self):
        """Test the extract_authors_with_affiliations method."""
        authors = PubMedParser.extract_authors_with_affiliations(self.article)
        
        # Verify the number of authors
        self.assertEqual(len(authors), 2)
        
        # Verify the first author
        self.assertEqual(authors[0]["name"], "Smith, John")
        self.assertEqual(authors[0]["affiliations"], ["Harvard University, Boston, MA, USA"])
        self.assertEqual(authors[0]["email"], "")
        
        # Verify the second author
        self.assertEqual(authors[1]["name"], "Doe, Jane")
        self.assertEqual(authors[1]["affiliations"], ["Pfizer Inc., New York, NY, USA jane.doe@pfizer.com"])
        self.assertEqual(authors[1]["email"], "jane.doe@pfizer.com")
        
        # Test with different affiliation format
        article_copy = self.article.copy()
        article_copy["MedlineCitation"]["Article"]["AuthorList"][0]["Author"]["Affiliation"] = [
            "Harvard University, Boston, MA, USA"
        ]
        del article_copy["MedlineCitation"]["Article"]["AuthorList"][0]["Author"]["AffiliationInfo"]
        
        authors = PubMedParser.extract_authors_with_affiliations(article_copy)
        self.assertEqual(authors[0]["affiliations"], ["Harvard University, Boston, MA, USA"])
    
    def test_extract_corresponding_author_email(self):
        """Test the extract_corresponding_author_email method."""
        # Mark the second author as corresponding
        article_copy = self.article.copy()
        article_copy["MedlineCitation"]["Article"]["AuthorList"][1]["Author"]["ValidYN"] = "Y"
        article_copy["MedlineCitation"]["Article"]["AuthorList"][1]["Author"]["EqualContrib"] = "Y"
        
        email = PubMedParser.extract_corresponding_author_email(article_copy)
        self.assertEqual(email, "jane.doe@pfizer.com")
        
        # Test with no corresponding author marked
        email = PubMedParser.extract_corresponding_author_email(self.article)
        self.assertEqual(email, "jane.doe@pfizer.com")  # Should return the first email found
        
        # Test with no emails
        article_copy = self.article.copy()
        article_copy["MedlineCitation"]["Article"]["AuthorList"][1]["Author"]["AffiliationInfo"][0]["Affiliation"] = "Pfizer Inc., New York, NY, USA"
        
        email = PubMedParser.extract_corresponding_author_email(article_copy)
        self.assertEqual(email, "Unknown")

if __name__ == "__main__":
    unittest.main()