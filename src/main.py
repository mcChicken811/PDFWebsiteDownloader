from link_crawler import LinkCrawler
from async_link_crawler import AsyncLinkCrawler
from file_util import FileUtil

# the goal is to given a root link, crawl all hyper link of the website under the domain of the root link
# and print a list of links for notebooklm to read the entire documentation
# additional features might include filtering the links


crawler = LinkCrawler("https://example.com", max_depth=1)
#FileUtil.save_urls(crawler.result, "output/example/urls.txt")
#FileUtil.save_url_to_pdfs(crawler.result, "output/example", 10)
