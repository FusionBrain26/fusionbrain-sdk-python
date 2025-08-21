import pytest
import pytest_asyncio
from polyfactory.factories.pydantic_factory import ModelFactory

from fusionbrain_sdk_python.async_client import AsyncFBClient
from fusionbrain_sdk_python.client import FBClient
from fusionbrain_sdk_python.models import Pipeline, PipelineResult, PipelineStatusResult, Style


@pytest.fixture
def client():
    return FBClient()


@pytest_asyncio.fixture
def async_client():
    return AsyncFBClient()


@pytest.fixture
def pipelines():
    class PipelineFactory(ModelFactory[Pipeline]): ...

    _pipelines = PipelineFactory.batch(
        2,
        name='Kandinsky',
        name_en='Kandinsky',
        version=3.1,
        type='TEXT2IMAGE'
    )
    return [pipe.model_dump(mode='json') for pipe in _pipelines]


@pytest.fixture
def pipeline_status_result():
    class PipelineStatusResultFactory(ModelFactory[PipelineStatusResult]):
        class ResultFactory(ModelFactory[PipelineResult]):
            censored = False
        result = ResultFactory
    return PipelineStatusResultFactory


@pytest.fixture
def styles():
    class StyleFactory(ModelFactory[Style]): ...

    _styles = StyleFactory.batch(2)
    return [style.model_dump(mode='json') for style in _styles]
