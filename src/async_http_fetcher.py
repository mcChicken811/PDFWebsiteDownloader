import asyncio
import httpx
from async_timed_lock import AsyncTimedLock
from urllib.parse import urljoin, urlparse
import math

class AsyncHttpFetcher:
    default_too_many_request_retry_duration: float=1.0
    request_timeout: float = 30.0
    default_max_request_times: int = 1000000

    def __init__(self) -> None:
        self._requests_lock = AsyncTimedLock()

    async def __aenter__(self):
        self._client = await httpx.AsyncClient().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    # if 301 status code respond, re-fetch
    # return the final url and response
    async def fetch(self, url, headers, max_request_times=default_max_request_times):
        response = None
        for _ in range(max_request_times):
            response = await self._kind_request(url, headers)

            if response.status_code != 301:
                break
            else:
                new_url = response.headers.get("Location", "")
                try:
                    urlparse(new_url)
                    url = urljoin(url, new_url)
                except:
                    print(f"url {url} responded 301, but new url {new_url} is not a valid url, giving up fetch")
                    break
                
        return (url, response)
    
    # handle http requests kindly to the website, if the host
    # claim Too Many Request then put the whole thing on lock until access is available
    async def _kind_request(self, url, headers):
        async with self._requests_lock:
            response = await self._client.get(url, headers=headers, timeout=AsyncHttpFetcher.request_timeout)

            if response.status_code == 429:
                halt_duration = response.headers.get("Retry-After", AsyncHttpFetcher.default_too_many_request_retry_duration)
                if not isinstance(halt_duration, float | int):
                    halt_duration = AsyncHttpFetcher.default_too_many_request_retry_duration
                
                print(f"Encountered 429, TooManyRequests from host, halting for {halt_duration} seconds")
                
                await self._requests_lock.lock(halt_duration)
                response = await self._kind_request(url, headers)

            return response

