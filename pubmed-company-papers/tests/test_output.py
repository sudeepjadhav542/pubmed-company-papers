"""Tests for the output module."""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import pandas as pd

from pubmed_company_papers.output import OutputHandler

class TestOutputHandler(unittest.TestCase):
    """Test cases for the OutputHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample data for testing
        self.sample_data = [
            {
                "PubmedID": "12345",
                "Title": "Test Article 1",
                "PublicationDate": "2023-01-15",
                "Non-academicAuthor(s)": "Doe, Jane",
                "CompanyAffiliation(s)": "Pfizer Inc.",
                "CorrespondingAuthorEmail": "jane.doe@pfizer.com"
            },
            {
                "PubmedID": "67890",
                "Title": "Test Article 2",
                "PublicationDate": "2023-02-20",
                "Non-academicAuthor(s)": "Smith, John",
                "CompanyAffiliation(s)": "Genentech, Inc.",
                "CorrespondingAuthorEmail": "john.smith@gene.com"
            }
        ]
    
    @patch("pubmed_company_papers.output.pd.DataFrame")
    def test_create_csv_to_file(self, mock_dataframe):
        """Test creating a CSV file."""
        # Mock DataFrame and to_csv
        mock_df = MagicMock()
        mock_dataframe.return_value = mock_df
        
        # Call the method
        OutputHandler.create_csv(self.sample_data, filename="test.csv")
        
        # Verify DataFrame was created with the correct data
        mock_dataframe.assert_called_once_with(self.sample_data)
        
        # Verify to_csv was called with the correct filename
        mock_df.to_csv.assert_called_once_with("test.csv", index=False)
    
    @patch("pubmed_company_papers.output.pd.DataFrame")
    @patch("builtins.print")
    def test_create_csv_to_console(self, mock_print, mock_dataframe):
        """Test printing CSV to console."""
        # Mock DataFrame and to_csv
        mock_df = MagicMock()
        mock_dataframe.return_value = mock_df
        mock_df.to_csv.return_value = "CSV content"
        
        # Call the method without a filename
        OutputHandler.create_csv(self.sample_data)
        
        # Verify DataFrame was created with the correct data
        mock_dataframe.assert_called_once_with(self.sample_data)
        
        # Verify to_csv was called with index=False
        mock_df.to_csv.assert_called_once_with(index=False)
        
        # Verify print was called with the CSV content
        mock_print.assert_called_once_with("CSV content")
    
    def test_format_data_for_csv(self):
        """Test formatting data for CSV output."""
        # Test data
        pubmed_id = "12345"
        title = "Test Article"
        publication_date = "2023-01-15"
        company_authors = ["Doe, Jane", "Smith, John"]
        company_names = ["Pfizer Inc.", "Genentech, Inc."]
        corresponding_email = "jane.doe@pfizer.com"
        
        # Call the method
        result = OutputHandler.format_data_for_csv(
            pubmed_id=pubmed_id,
            title=title,
            publication_date=publication_date,
            company_authors=company_authors,
            company_names=company_names,
            corresponding_email=corresponding_email
        )
        
        # Verify the result
        expected = {
            "PubmedID": "12345",
            "Title": "Test Article",
            "PublicationDate": "2023-01-15",
            "Non-academicAuthor(s)": "Doe, Jane; Smith, John",
            "CompanyAffiliation(s)": "Pfizer Inc.; Genentech, Inc.",
            "CorrespondingAuthorEmail": "jane.doe@pfizer.com"
        }
        
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()