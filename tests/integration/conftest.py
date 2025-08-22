import pytest
import pytest_asyncio

from fusionbrain_sdk_python.async_client import AsyncFBClient
from fusionbrain_sdk_python.client import FBClient


@pytest.fixture(scope='module')
def client():
    return FBClient()


@pytest_asyncio.fixture(scope='module')
def async_client():
    return AsyncFBClient()
