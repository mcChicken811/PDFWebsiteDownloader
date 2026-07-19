from typing import Callable
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
from recur_thread_pool_executor import RecurThreadPoolExecutor
import threading
from url_util import URLUtil

class LinkCrawler:
    # max_depth = 0 symbolise only crawling the root url, 1 symbolise crawling root url and url found in root url
    def __init__(self, root_url: str, ft: Callable[[str], bool] = lambda url: True, max_depth: int = 0, default_header=URLUtil.fake_request_header, max_workers=30):
        self._root_url = URLUtil.formalise_url(root_url)
        self._host = URLUtil.get_url_host(self._root_url)
        self._filter = ft
        self._max_depth = max_depth
        self._default_header = default_header

        if not self._host:
            raise ValueError("root_url has no host, root_url must be the full url including host")
        self._found_urls: set[str] = set()
        self._bad_respond_urls: set[str] = set()

        # starts crawling 
        self._executor = RecurThreadPoolExecutor(max_workers)
        self._found_urls_lock = threading.Lock()
        self._bad_respond_urls_lock = threading.Lock()

        with self._found_urls_lock:
            self._found_urls.add(self._root_url)

        self._executor.submit(self.crawl_html_url, self._root_url, 0)
        self._executor.wait()

        num_of_found_urls = len(self._found_urls)
        num_of_failed_urls = len(self._bad_respond_urls)
        num_of_success_urls = num_of_found_urls - num_of_failed_urls

        print(f"Finished crawling from root: {self._root_url}, success: {num_of_success_urls}, failed: {num_of_failed_urls}, total(found): {num_of_found_urls}")

        self._found_urls = self._found_urls - self._bad_respond_urls

    @property
    def result(self) -> set[str]:
        return self._found_urls
    
    # assuming the given url is an html, crawl all the hyperlinks of the html
    # that is in the root url host if the url is not already in the _found_urls
    def crawl_html_url(self, url: str, depth: int):
        response = requests.get(url, headers=self._default_header)
        if response.ok and ("text/html" in response.headers.get("Content-Type", "")):

            # discontinue when the depth reaches the max_depth meaning leaf is reached
            if depth >= self._max_depth:
                print(f"Success crawling leaf url: {url}")
                return

            found_urls: set[str] = self._collect_html_urls_from_html(response.text, url)

            total_count: int = len(found_urls)
            count: int = 0
            for found_url in found_urls:
                count = count + 1
                
                if not found_url in self._found_urls:
                    # add the url to found to prevent repeating crawling
                    with self._found_urls_lock:
                        self._found_urls.add(found_url)
                    # submit crawling task
                    print(f"crawling No.{count}/{total_count} found url from: {url}, URL: {found_url}")
                    self._executor.submit(self.crawl_html_url, found_url, depth+1)

            print(f"Success crawling url: {url}")

        else:
            # crawling task failed, add the url to the set of found but no respond urls
            with self._bad_respond_urls_lock:
                self._bad_respond_urls.add(url)
            print(f"Failed crawling url: {url}, respond is not text/html or respond failed, skipping")

    # note LinkCrawler always filter the link to only links in the host 
    # and such filter cannot be override by passing predicates to the filter argument
    # and note LinkCrawler only collects html pages
    # ft refers to the filter function that takes in a full url
    def _collect_html_urls_from_html(self, html: str, url: str) -> set[str]:
        soup = BeautifulSoup(html, "html.parser")
        hrefs: set[str] = set()
        
        for a in soup.find_all("a", href=True):
            href: str = str(a["href"])

            if not URLUtil.is_url_vaild(href):
                continue

            # url has no host (assume it is relative URL and thus gave it the root_url origin)
            if not URLUtil.get_url_host(href):
                href = urljoin(url, href)
            
            if not (URLUtil.is_URL_host(href, self._host) and URLUtil.is_url_html_file(href) and self._filter(href)):
                continue

            hrefs.add(URLUtil.formalise_url(href))

        return hrefs
