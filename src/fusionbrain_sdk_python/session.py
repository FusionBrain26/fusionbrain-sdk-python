import asyncio
from types import TracebackType
from typing import Any, Optional, Type, Union

import aiohttp
import async_timeout
import requests  # type: ignore
from requests.adapters import HTTPAdapter  # type: ignore
from urllib3.util.retry import Retry  # type: ignore


class Session:
    def __init__(self, retries: int = 5, backoff_factor: float = 0.3) -> None:
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.session = self._create_retry_session()

    def _create_retry_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=self.retries,
            read=self.retries,
            connect=self.retries,
            backoff_factor=self.backoff_factor,
            allowed_methods=None,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        return session

    def get_session(self) -> requests.Session:
        return self.session


class AsyncSession:
    def __init__(self, retries: int = 5, backoff_factor: float = 0.3, timeout: float = 10.0) -> None:
        self.retries: int = retries
        self.backoff_factor: float = backoff_factor
        self.timeout: float = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> 'AsyncSession':
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> Optional[bool]:
        if self.session:
            await self.session.close()
        return None

    async def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> aiohttp.ClientResponse:
        last_exc: Optional[Union[aiohttp.ClientError, asyncio.TimeoutError]] = None
        for attempt in range(1, self.retries + 1):
            try:
                async with async_timeout.timeout(self.timeout):
                    if self.session is None:
                        raise RuntimeError(
                            "Session is not initialized. Use 'async with AsyncSession()' or call __aenter__ manually.",
                        )
                    async with self.session.request(method, url, **kwargs) as response:
                        response.raise_for_status()
                        return response
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                last_exc = exc
                if attempt == self.retries:
                    raise
                await asyncio.sleep(self.backoff_factor * (2 ** (attempt - 1)))
        if last_exc is not None:
            raise last_exc
        raise RuntimeError('Unexpected error in request method')

    async def get(self, url: str, **kwargs: Any) -> aiohttp.ClientResponse:
        return await self.request('GET', url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> aiohttp.ClientResponse:
        return await self.request('POST', url, **kwargs)
