from playwright.async_api import async_playwright, Browser, Page
import asyncio

# to use this saver, you first submit pdf saving requests on the main thread
# then you run wait() to halt the main thread until all saving processes are finished
#
# the multi--thread web pdf saver runs on async, which in with statement you gather all the
# webpages you wanted to save, and then the saver start running async at __exit__()
class MultiThreadWebPDFSaver:
    # max_concurrent_web_pages: the maximum number of pages that the pdf saver will open
    #   at the same time in one chromium instance (virtual browser)
    def __init__(self, max_concurrent_web_pages=30):
        # stores (url, path) tuple
        self._requested_pages_to_save: list[tuple[str, str]] = list()
        self._semaphore = asyncio.Semaphore(max_concurrent_web_pages)
        self._failed_counter: int = 0

    def __enter__(self):
        self._failed_counter = 0
        return self

    
    def __exit__(self, exc_type, exc_value, traceback):
        asyncio.run(self._save_requested())

        num_total_requests = len(self._requested_pages_to_save)
        num_success_requests = num_total_requests - self._failed_counter
        num_failed_requests = self._failed_counter
        print(f"Finished executing saving request, success: {num_success_requests}, failed(skipped): {num_failed_requests}, total: {num_total_requests}")

    # request to save a page
    def request_save(self, url: str, path: str):
        self._requested_pages_to_save.append((url, path))

    async def _save_requested(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            save_couroutine = list()
            for (url, path) in self._requested_pages_to_save:
                save_couroutine.append(self._save_pdf(browser, url, path))

            await asyncio.gather(*save_couroutine)

    async def _save_pdf(self, browser: Browser, url: str, path: str):
        async with self._semaphore:
            page = await browser.new_page()

            try:
                print(f"Saving page: {url} to: {path}")
                await page.goto(url, wait_until="load")
                await page.pdf(
                    path=path,
                    format="A4",
                    print_background=True,
                )
                print(f"Successfully save page: {url} to: {path}")
            except:
                print(f"Failed to save page: {url} to: {path}, skipping")
                self._failed_counter = self._failed_counter + 1
            finally:
                await page.close()