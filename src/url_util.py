from urllib.parse import urljoin, urlparse
from pathlib import PurePosixPath, Path


class URLUtil:
    HTML_EXTENTIONS = {
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

    fake_request_header={
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        )
    }

    @staticmethod
    def is_url_html_file(url: str) -> bool:
        path = urlparse(url).path
        suffix = PurePosixPath(path).suffix
        return suffix in URLUtil.HTML_EXTENTIONS
    
    # make the url in the standard format that only includes scheme, netloc and path
    @staticmethod
    def formalise_url(url: str):
        url_data = urlparse(url)
        return url_data.scheme + "://" + url_data.netloc + "/" + url_data.path.lstrip("/")
    
    # return if the given URL follows the same host as the root url
    @staticmethod
    def is_URL_host(url: str, host: str) -> bool:
        return urlparse(url).netloc == host
    
    @staticmethod
    def get_pdf_save_path_from_url(url, save_dir):
        url_path = urlparse(url).path

        if url_path.lstrip("/") == "":
            url_path = "index.html"
        dir_path = (str(PurePosixPath(url_path).parent / PurePosixPath(url_path).stem) + ".pdf").lstrip("/")

        path = str(Path(save_dir) / dir_path)
        return path
    
    @staticmethod
    def get_url_host(url):
        return urlparse(url).netloc
    
    @staticmethod
    def is_url_vaild(url) -> bool:
        try:
            urlparse(url)
            return True
        except:
            return False