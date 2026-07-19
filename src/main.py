from link_crawler import LinkCrawler
from async_link_crawler import AsyncLinkCrawler


# the goal is to given a root link, crawl all hyper link of the website under the domain of the root link
# and print a list of links for notebooklm to read the entire documentation
# additional features might include filtering the links


crawler = AsyncLinkCrawler("https://mgs.vic.edu.au/", max_depth=3)
crawler.save_found_urls_to("output/mgs/urls.txt")
#crawler.save_url_to_pdfs("output/example")