import pytest

from fusionbrain_sdk_python.models import (
    Pipeline,
    PipelineResultStatus,
    PipelineStatus,
    PipelineStatusResult,
    PipelineType,
    RunPipelineResult,
    Style,
)


@pytest.fixture(scope='module')
def pipeline(client):
    return client.get_pipelines_by_type(PipelineType.TEXT2IMAGE)


@pytest.mark.int
def test_get_pipelines(client):
    got = client.get_pipelines()
    assert isinstance(got, list)
    assert all(isinstance(pipe, Pipeline) for pipe in got)


@pytest.mark.int
def test_get_pipelines_by_type(client):
    got = client.get_pipelines_by_type(pipe_type=PipelineType.TEXT2IMAGE)
    assert isinstance(got, list)
    assert all(isinstance(pipe, Pipeline) for pipe in got)
    assert all(pipe.type == 'TEXT2IMAGE' for pipe in got)


@pytest.mark.int
def test_get_pipeline_availability(client, pipeline):
    pipeline_id = pipeline[0].id
    got = client.get_pipeline_availability(pipeline_id=pipeline_id)
    assert isinstance(got, PipelineStatus)
    assert got == PipelineStatus.ACTIVE


@pytest.mark.int
def test_run_pipeline(client, pipeline):
    pipeline_id = pipeline[0].id
    got = client.run_pipeline(pipeline_id=pipeline_id, prompt='Море')
    assert isinstance(got, RunPipelineResult)


@pytest.mark.int
def test_get_status(client, pipeline):
    pipeline_id = pipeline[0].id
    request = client.run_pipeline(pipeline_id=pipeline_id, prompt='Море')
    got = client.get_status(request.uuid)
    assert isinstance(got, PipelineStatusResult)


@pytest.mark.int
def test_wait_for_completion(client, pipeline):
    pipeline_id = pipeline[0].id
    request = client.run_pipeline(pipeline_id=pipeline_id, prompt='Море')
    got = client.wait_for_completion(
        request_id=request.uuid,
        initial_delay=request.status_time,
        sleep_interval=5,
    )
    assert isinstance(got, PipelineStatusResult)
    assert got.status == PipelineResultStatus.DONE


@pytest.mark.int
def test_get_styles(client):
    got = client.get_styles()
    assert isinstance(got, list)
    assert got
    assert all(isinstance(style, Style) for style in got)
