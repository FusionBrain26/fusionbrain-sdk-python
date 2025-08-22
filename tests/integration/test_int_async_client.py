import pytest
import pytest_asyncio

from fusionbrain_sdk_python.models import (
    Pipeline,
    PipelineResultStatus,
    PipelineStatus,
    PipelineStatusResult,
    PipelineType,
    RunPipelineResult,
    Style,
)


@pytest_asyncio.fixture(scope='module')
async def pipeline(async_client):
    return await async_client.get_pipelines()


@pytest.mark.int
@pytest.mark.asyncio
async def test_get_pipelines(async_client):
    got = await async_client.get_pipelines()
    assert isinstance(got, list)
    assert all(isinstance(pipe, Pipeline) for pipe in got)


@pytest.mark.int
@pytest.mark.asyncio
async def test_get_pipelines_by_type(async_client):
    got = await async_client.get_pipelines_by_type(pipe_type=PipelineType.TEXT2IMAGE)
    assert isinstance(got, list)
    assert all(isinstance(pipe, Pipeline) for pipe in got)
    assert all(pipe.type == 'TEXT2IMAGE' for pipe in got)


@pytest.mark.int
@pytest.mark.asyncio
async def test_get_pipeline_availability(async_client, pipeline):
    pipeline_id = pipeline[0].id
    got = await async_client.get_pipeline_availability(pipeline_id=pipeline_id)
    assert isinstance(got, PipelineStatus)
    assert got == PipelineStatus.ACTIVE


@pytest.mark.int
@pytest.mark.asyncio
async def test_run_pipeline(async_client, pipeline):
    pipeline_id = pipeline[0].id
    got = await async_client.run_pipeline(pipeline_id=pipeline_id, prompt='Море')
    assert isinstance(got, RunPipelineResult)


@pytest.mark.int
@pytest.mark.asyncio
async def test_get_status(async_client, pipeline):
    pipeline_id = pipeline[0].id
    request = await async_client.run_pipeline(pipeline_id=pipeline_id, prompt='Море')
    got = await async_client.get_status(request.uuid)
    assert isinstance(got, PipelineStatusResult)


@pytest.mark.int
@pytest.mark.asyncio
async def test_wait_for_completion(async_client, pipeline):
    pipeline_id = pipeline[0].id
    request = await async_client.run_pipeline(pipeline_id=pipeline_id, prompt='Море')
    got = await async_client.wait_for_completion(
        request_id=request.uuid,
        initial_delay=request.status_time,
        sleep_interval=5,
    )
    assert isinstance(got, PipelineStatusResult)
    assert got.status == PipelineResultStatus.DONE


@pytest.mark.int
@pytest.mark.asyncio
async def test_get_styles(async_client):
    got = await async_client.get_styles()
    assert isinstance(got, list)
    assert got
    assert all(isinstance(style, Style) for style in got)
