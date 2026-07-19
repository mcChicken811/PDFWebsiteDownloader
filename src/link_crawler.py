from typing import Callable
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import requests
from pathlib import PurePosixPath, Path
from multi_thread_web_pdf_saver import MultiThreadWebPDFSaver
from recur_thread_pool_executor import RecurThreadPoolExecutor
import threading

class LinkCrawler:
    # max_depth = 0 symbolise only crawling the root url, 1 symbolise crawling root url and url found in root url
    def __init__(self, root_url: str, ft: Callable[[str], bool] = lambda url: True, max_depth: int = 0, default_header={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            )
        }):
        self._root_url = self.formalise_url(root_url)
        self._host = urlparse(self._root_url).netloc
        self._filter = ft
        self._max_depth = max_depth
        self._default_header = default_header
        self.HTML_EXTENTIONS = {
            "",
            ".html",
            ".htm",
            ".xhtml",
            ".php",
            ".asp",
            ".aspx",
            ".jsp",
            ".cgi",
        }
        if not self._host:
            raise ValueError("root_url has no host, root_url must be the full url including host")
        self._found_urls: set[str] = set()
        self._bad_respond_urls: set[str] = set()

        self._PDF_saver = MultiThreadWebPDFSaver()

        # starts crawling 
        self._executor = RecurThreadPoolExecutor(100)
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
        
    def save_url_to_pdfs(self, save_dir: str=""):
        with self._PDF_saver as saver:
            for url in self._found_urls:
                saver.request_save(url, self.get_pdf_save_path_from_url(url, save_dir))

    def get_pdf_save_path_from_url(self, url, save_dir):
        url_path = urlparse(url).path

        if url_path.lstrip("/") == "":
            url_path = "index.html"
        dir_path = (str(PurePosixPath(url_path).parent / PurePosixPath(url_path).stem) + ".pdf").lstrip("/")

        path = str(Path(save_dir) / dir_path)
        return path

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


        

    def save_found_urls_to(self, path: str):
        print(f"Saving found urls to: {path}")
        sorted_urls = sorted(self._found_urls)
        with open(path, "w", encoding="utf-8") as file:
            for url in sorted_urls:
                file.write(url + "\n")

    # note LinkCrawler always filter the link to only links in the host 
    # and such filter cannot be override by passing predicates to the filter argument
    # and note LinkCrawler only collects html pages
    # ft refers to the filter function that takes in a full url
    def _collect_html_urls_from_html(self, html: str, url: str) -> set[str]:
        soup = BeautifulSoup(html, "html.parser")
        hrefs: set[str] = set()
        
        for a in soup.find_all("a", href=True):
            href: str = str(a["href"])


            # url has no host (assume it is relative URL and thus gave it the root_url origin)
            if not urlparse(href).netloc:
                href = urljoin(url, href)

            
            # discard url with different host
            if not self._is_URL_from_root_host(href):
                continue

            if not self._is_url_html_file(href):
                continue

            

            if not self._filter(href):
                continue

            hrefs.add(self.formalise_url(href))

        return hrefs

    # make the url in the standard format that only includes scheme, netloc and path
    def formalise_url(self, url: str):
        url_data = urlparse(url)
        return url_data.scheme + "://" + url_data.netloc + "/" + url_data.path.lstrip("/")
        
     # return if the given URL follows the same host as the root url
    def _is_URL_from_root_host(self, url: str) -> bool:
        return urlparse(url).netloc == self._host


    def _is_url_html_file(self, url: str) -> bool:
        path = urlparse(url).path
        suffix = PurePosixPath(path).suffix
        return suffix in self.HTML_EXTENTIONS



    