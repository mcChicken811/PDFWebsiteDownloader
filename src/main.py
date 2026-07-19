from link_crawler import LinkCrawler


# the goal is to given a root link, crawl all hyper link of the website under the domain of the root link
# and print a list of links for notebooklm to read the entire documentation
# additional features might include filtering the links

crawler: LinkCrawler = LinkCrawler("https://example.com", max_depth=5)
#crawler.save_found_urls_to("output/example/urls.txt")
#crawler.save_url_to_pdfs("output/example")