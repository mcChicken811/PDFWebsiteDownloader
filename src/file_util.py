from multi_thread_web_pdf_saver import MultiThreadWebPDFSaver
from url_util import URLUtil

class FileUtil:
    @staticmethod
    def save_url_to_pdfs(urls: set[str], save_dir: str="", max_concurrent_web_pages: int=30):
        with MultiThreadWebPDFSaver(max_concurrent_web_pages) as saver:
            for url in urls:
                saver.request_save(url, URLUtil.get_pdf_save_path_from_url(url, save_dir))

    @staticmethod
    def save_urls(urls: set[str], path: str):
        print(f"Saving urls to: {path}")
        sorted_urls = sorted(urls)
        with open(path, "w", encoding="utf-8") as file:
            for url in sorted_urls:
                file.write(url + "\n")