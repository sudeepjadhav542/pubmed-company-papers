"""Tests for the affiliations module."""

import unittest
from pubmed_company_papers.affiliations import AffiliationAnalyzer

class TestAffiliationAnalyzer(unittest.TestCase):
    """Test cases for the AffiliationAnalyzer class."""
    
    def test_is_company_affiliation(self):
        """Test the is_company_affiliation method."""
        # Test company affiliations
        self.assertTrue(AffiliationAnalyzer.is_company_affiliation("Pfizer Inc., New York, NY, USA"))
        self.assertTrue(AffiliationAnalyzer.is_company_affiliation("Genentech, Inc., South San Francisco, CA 94080, USA"))
        self.assertTrue(AffiliationAnalyzer.is_company_affiliation("AstraZeneca Pharmaceuticals, Cambridge, UK"))
        self.assertTrue(AffiliationAnalyzer.is_company_affiliation("Novartis Institutes for BioMedical Research, Basel, Switzerland"))
        self.assertTrue(AffiliationAnalyzer.is_company_affiliation("john.  Basel, Switzerland"))
        self.assertTrue(AffiliationAnalyzer.is_company_affiliation("john.doe@pharma.com"))
        
        # Test academic affiliations
        self.assertFalse(AffiliationAnalyzer.is_company_affiliation("Harvard University, Boston, MA, USA"))
        self.assertFalse(AffiliationAnalyzer.is_company_affiliation("Department of Biology, Stanford University, CA, USA"))
        self.assertFalse(AffiliationAnalyzer.is_company_affiliation("National Institutes of Health, Bethesda, MD, USA"))
        self.assertFalse(AffiliationAnalyzer.is_company_affiliation("john.doe@university.edu"))
    
    def test_extract_company_name(self):
        """Test the extract_company_name method."""
        self.assertEqual(
            "Pfizer Inc.", 
            AffiliationAnalyzer.extract_company_name("Pfizer Inc., New York, NY, USA")
        )
        self.assertEqual(
            "Genentech, Inc.", 
            AffiliationAnalyzer.extract_company_name("Genentech, Inc., South San Francisco, CA 94080, USA")
        )
        self.assertEqual(
            "AstraZeneca Pharmaceuticals", 
            AffiliationAnalyzer.extract_company_name("AstraZeneca Pharmaceuticals, Cambridge, UK")
        )
    
    def test_identify_company_authors(self):
        """Test the identify_company_authors method."""
        authors = [
            {
                "name": "Smith, John",
                "affiliations": ["Harvard University, Boston, MA, USA"],
                "email": "john.smith@harvard.edu",
                "is_corresponding": True
            },
            {
                "name": "Doe, Jane",
                "affiliations": ["Pfizer Inc., New York, NY, USA"],
                "email": "jane.doe@pfizer.com",
                "is_corresponding": False
            },
            {
                "name": "Johnson, Bob",
                "affiliations": ["Stanford University, CA, USA", "Genentech, Inc., South San Francisco, CA, USA"],
                "email": "bob.johnson@stanford.edu",
                "is_corresponding": False
            }
        ]
        
        company_authors, company_names = AffiliationAnalyzer.identify_company_authors(authors)
        
        self.assertEqual(len(company_authors), 2)
        self.assertIn("Doe, Jane", company_authors)
        self.assertIn("Johnson, Bob", company_authors)
        
        self.assertEqual(len(company_names), 2)
        self.assertIn("Pfizer Inc.", company_names)
        self.assertIn("Genentech, Inc.", company_names)

if __name__ == "__main__":
    unittest.main()