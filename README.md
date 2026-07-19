# PDFWebsiteDownloader
## Installation
### macOS
Clone Git Repository:
- Open a terminal in your desired folder and run the following command to clone this repository in the folder
```Terminal
git clone https://github.com/mcChicken811/PDFWebsiteDownloader.git
```

Setup python virtual environment:
- In the same terminal run the following command:
- Note: use python if you are in Windows, python3 for macOS / Linux, otherwise use whatever that works
```Terminal
cd PDFWebsiteDownloader
python3 -m venv .venv
source .venv/bin/activate
```

Install required packages:
- Make sure you are in the virtual environment and then run:
```Terminal
pip install -r requirements.txt
playwright install
```

### Windows
Clone Git Repository:
- Open a terminal in your desired folder and run the following command to clone this repository in the folder
```Terminal
git clone https://github.com/mcChicken811/PDFWebsiteDownloader.git
```

Setup python virtual environment:
- In the same terminal run the following command:
- Note: use python if you are in Windows, python3 for macOS / Linux, otherwise use whatever that works
```Powershell
cd PDFWebsiteDownloader
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install required packages:
- Make sure you are in the virtual environment and then run:
```Powershell
pip install -r requirements.txt
playwright install
```

## Basic Guide
Currently the downloader does not provide user interface, all configuration must be done through python script in src/main.py (recommended, but you can use it in any python script you want)

To crawl the website from a given root url, make a LinkCrawler instance and give it the root url. The max_depth parameter refers to the "maximum depth - 1" of which the crawler look for urls by travelling through hyperlinks starting from the root url
```Python
crawler: LinkCrawler = LinkCrawler("https://example.com", max_depth=0)
```

To save the found urls in to a text file, use: (which provides the path to the text file you want to save to)
```Python
crawler.save_found_urls_to("output/example/urls.txt")
```

To save the found urls into pdf files in the chosen directory use: (which provides the directory which you want to save all the pdfs each representing one webpage to)
```Python
crawler.save_url_to_pdfs("output/example")
```

To run the downloader, simply run the python file in the virtual environment, if you use src/main.py do:
```Terminal
python3 src/main.py
```
