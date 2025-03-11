"""Tests for the api module."""

import unittest
from unittest.mock import patch, MagicMock
import json
from io import StringIO

from pubmed_company_papers.api import PubMedAPI

class TestPubMedAPI(unittest.TestCase):
    """Test cases for the PubMedAPI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = PubMedAPI(email="test@example.com", tool="TestTool")
    
    @patch("pubmed_company_papers.api.Entrez.esearch")
    @patch("pubmed_company_papers.api.Entrez.read")
    def test_search(self, mock_read, mock_esearch):
        """Test the search method."""
        # Mock the response
        mock_handle = MagicMock()
        mock_esearch.return_value = mock_handle
        
        mock_read.return_value = {
            "Count": "2",
            "RetMax": "2",
            "IdList": ["12345", "67890"]
        }
        
        # Call the method
        result = self.api.search("cancer", retmax=10)
        
        # Verify the result
        self.assertEqual(result, ["12345", "67890"])
        
        # Verify the API call
        mock_esearch.assert_called_once_with(db="pubmed", term="cancer", retmax=10)
        mock_read.assert_called_once_with(mock_handle)
        mock_handle.close.assert_called_once()
    
    @patch("pubmed_company_papers.api.Entrez.efetch")
    @patch("pubmed_company_papers.api.Entrez.read")
    def test_fetch_details(self, mock_read, mock_efetch):
        """Test the fetch_details method."""
        # Mock the response
        mock_handle = MagicMock()
        mock_efetch.return_value = mock_handle
        
        mock_read.return_value = {"PubmedArticle": [{"MedlineCitation": {"PMID": "12345"}}]}
        
        # Call the method
        result = self.api.fetch_details(["12345", "67890"])
        
        # Verify the result
        self.assertEqual(result, {"PubmedArticle": [{"MedlineCitation": {"PMID": "12345"}}]})
        
        # Verify the API call
        mock_efetch.assert_called_once_with(db="pubmed", id="12345,67890", retmode="xml")
        mock_read.assert_called_once_with(mock_handle)
        mock_handle.close.assert_called_once()
    
    @patch("pubmed_company_papers.api.Entrez.efetch")
    @patch("pubmed_company_papers.api.Entrez.read")
    @patch("pubmed_company_papers.api.time.sleep")
    def test_fetch_articles_batch(self, mock_sleep, mock_read, mock_efetch):
        """Test the fetch_articles_batch method."""
        # Mock the response
        mock_handle = MagicMock()
        mock_efetch.return_value = mock_handle
        
        mock_read.return_value = {
            "PubmedArticle": [
                {"MedlineCitation": {"PMID": "12345"}},
                {"MedlineCitation": {"PMID": "67890"}}
            ]
        }
        
        # Call the method with a batch size of 2
        result = self.api.fetch_articles_batch(["12345", "67890", "13579"], batch_size=2)
        
        # Verify the result
        self.assertEqual(len(result), 4)  # 2 articles per batch, 2 batches
        
        # Verify the API calls
        self.assertEqual(mock_efetch.call_count, 2)
        mock_efetch.assert_any_call(db="pubmed", id="12345,67890", retmode="xml")
        mock_efetch.assert_any_call(db="pubmed", id="13579", retmode="xml")
        
        # Verify sleep was called between batches
        mock_sleep.assert_called_once()

if __name__ == "__main__":
    unittest.main()