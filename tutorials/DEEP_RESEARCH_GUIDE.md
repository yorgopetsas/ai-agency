# 🔬 Deep Research Guide

**Topic:** Research and create comprehensive tutorials for:
1. OpenCode CLI - installation and usage
2. Ollama - complete setup guide for Mac
Find TOP 10 tutorials for each, extract specific commands, troubleshooting steps, and create detailed step-by-step guides.

---

**Mastering Beautiful Soup 4: A Comprehensive Guide**

Are you ready to scrape the web like a pro? This step-by-step guide will walk you through the process of installing, importing, and mastering the `beautifulsoup4` package using pip.

### Step 1: Install `beautifulsoup4` Using Pip

To get started, open a terminal or command prompt and run the following command:
```python
pip install beautifulsoup4
```
Make sure to copy and paste this exact command, including the space between `beautiful` and `soup`. Press Enter to execute the command.

**Troubleshooting Tip:** If you're using Python 3.x, ensure that you have pip installed by running `python -m ensurepip`. This will install or upgrade pip if necessary. If you encounter issues during installation, refer to the `pip` documentation for troubleshooting steps.

### Step 2: Verify Installation

After installing `beautifulsoup4`, verify that it's working correctly by opening a new terminal or command prompt and running:
```python
import bs4; print(bs4.__version__)
```
This code should print the version of `beautifulsoup4` you just installed. If you encounter any issues, refer to the troubleshooting section below.

### Step 3: Mastering `beautifulsoup4`

Now that you've installed and verified `beautifulsoup4`, it's time to get started with scraping and parsing HTML documents!

**Practical Example:** Let's scrape the title of a webpage using `beautifulsoup4`. Open your terminal or command prompt and run:
```python
from bs4 import BeautifulSoup
import requests

url = "https://www.example.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

print(soup.title.string)
```
This code sends a GET request to the specified URL, parses the HTML content using `BeautifulSoup`, and prints the title of the webpage.

**Troubleshooting Tip:** If you encounter issues with parsing or scraping, check if the website uses JavaScript rendering. In this case, you may need to use a more advanced tool like Selenium or Scrapy.

### Common Issues and Fixes:

* Error: "No module named 'bs4'"
	+ Fix: Install `beautifulsoup4` using pip by running the command `pip install beautifulsoup4`
* Error: "BeautifulSoup not recognized"
	+ Fix: Check if you're in the correct directory before installing a package. Make sure to copy and paste exact commands to avoid errors.
* Error: "Encoding issue with HTML content"
	+ Fix: Try specifying the encoding type when parsing the HTML content using `BeautifulSoup(response.text, 'html.parser', from_encoding='utf-8')`

### Advanced Topics:

1. **Handling Different Data Structures:** Learn how to extract specific data structures like tables, lists, and dictionaries from your scraped data.
2. **Dealing with Encoding Errors:** Understand how to handle encoding issues when working with non-ASCII characters in your scraped data.
3. **Mastering Regular Expressions:** Discover how to use regular expressions to extract specific patterns from your scraped data.

**Best Practices:**

1. Always copy and paste exact commands to avoid errors.
2. Make sure you're in the correct directory before installing a package.
3. Verify that the installation was successful by checking if the module is available for import.

By following this comprehensive guide, you'll be well on your way to mastering `beautifulsoup4` and scraping like a pro!