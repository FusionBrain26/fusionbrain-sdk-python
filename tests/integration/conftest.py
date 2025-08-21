
import pytest
import pytest_asyncio
from dotenv import load_dotenv

from fusionbrain_sdk_python.async_client import AsyncFBClient
from fusionbrain_sdk_python.client import FBClient


@pytest.fixture(scope='module')
def client():
    load_dotenv(override=True)
    return FBClient()


@pytest_asyncio.fixture(scope='module')
def async_client():
    load_dotenv(override=True)
    return AsyncFBClient()
