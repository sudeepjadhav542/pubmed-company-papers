PubMed Company Papers
A Python tool to fetch research papers from PubMed based on user-specified queries, identifying papers with at least one author affiliated with a pharmaceutical or biotech company.

Features
Search PubMed using its full query syntax
Identify papers with authors affiliated with pharmaceutical/biotech companies
Output results as a CSV file with detailed information
Command-line interface with various options
Installation
This project uses Poetry for dependency management. To install:

# Clone the repository
git clone https://github.com/yourusername/pubmed-company-papers.git
cd pubmed-company-papers

# Install dependencies
poetry install


## Tools Used

- [Poetry](https://python-poetry.org/): Dependency management and packaging
- [Biopython](https://biopython.org/): For interacting with the PubMed API via Entrez
- [pandas](https://pandas.pydata.org/): For data manipulation and CSV output
- [tqdm](https://github.com/tqdm/tqdm): For progress bars
- [pytest](https://docs.pytest.org/): For testing
- [black](https://github.com/psf/black) and [isort](https://pycqa.github.io/isort/): For code formatting
- [mypy](https://mypy.readthedocs.io/): For static type checking