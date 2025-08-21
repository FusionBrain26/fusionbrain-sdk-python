import uuid
from http import HTTPStatus

import pytest
from aiohttp import ClientResponseError
from aioresponses import aioresponses
from pydantic import ValidationError

from fusionbrain_sdk_python.models import (
    Pipeline,
    PipelineResultStatus,
    PipelineStatus,
    PipelineStatusResult,
    PipelineType,
    RunPipelineBlockedResult,
    RunPipelineResult,
    Style,
)


@pytest.mark.asyncio
async def test_async_get_pipelines(async_client, pipelines):
    with aioresponses() as m:
        m.get('https://api-key.fusionbrain.ai/key/api/v1/pipelines', payload=pipelines)
        got = await async_client.get_pipelines()
        assert isinstance(got, list)
        assert all(isinstance(pipe, Pipeline) for pipe in got)
        assert got[0] == Pipeline(**pipelines[0])


@pytest.mark.asyncio
async def test_get_pipeline_not_OK(async_client):
    with pytest.raises(ClientResponseError, match='In response to *'):
        with aioresponses() as m:
            m.get('https://api-key.fusionbrain.ai/key/api/v1/pipelines', status=HTTPStatus.NOT_FOUND)
            await async_client.get_pipelines()


@pytest.mark.asyncio
async def test_get_pipelines_by_type(async_client, pipelines):
    with aioresponses() as m:
        m.get('https://api-key.fusionbrain.ai/key/api/v1/pipelines?type=TEXT2IMAGE', payload=pipelines)
        got = await async_client.get_pipelines_by_type(pipe_type=PipelineType.TEXT2IMAGE)
        assert isinstance(got, list)
        assert all(isinstance(pipe, Pipeline) for pipe in got)
        assert all(pipe.type == 'TEXT2IMAGE' for pipe in got)


@pytest.mark.asyncio
async def test_get_pipelines_by_type_not_OK(async_client):
    with pytest.raises(ClientResponseError, match='In response to *'):
        with aioresponses() as m:
            m.get('https://api-key.fusionbrain.ai/key/api/v1/pipelines?type=TEXT2IMAGE', status=HTTPStatus.NOT_FOUND)
            await async_client.get_pipelines_by_type(pipe_type=PipelineType.TEXT2IMAGE)


@pytest.mark.asyncio
async def test_get_pipeline_availability(async_client, pipelines):
    with aioresponses() as m:
        pipeline_id = pipelines[0]['id']
        m.get(
            f'https://api-key.fusionbrain.ai/key/api/v1/pipeline/{str(pipeline_id)}/availability',
            payload={'status': 'ACTIVE'}
        )
        got = await async_client.get_pipeline_availability(pipeline_id=pipeline_id)
        assert isinstance(got, PipelineStatus)
        assert got == PipelineStatus.ACTIVE


@pytest.mark.asyncio
async def test_get_pipeline_availability_not_OK(async_client, pipelines):
    with pytest.raises(ClientResponseError, match='In response to *'):
        with aioresponses() as m:
            pipeline_id = pipelines[0]['id']
            m.get(
                f'https://api-key.fusionbrain.ai/key/api/v1/pipeline/{str(pipeline_id)}/availability',
                status=HTTPStatus.NOT_FOUND
            )
            await async_client.get_pipeline_availability(pipeline_id=pipeline_id)


@pytest.mark.asyncio
async def test_get_pipeline_availability_unknown_status(async_client, pipelines):
    with pytest.raises(ValidationError, match='1 validation error for PipelineAvailabilityResult*'):
        with aioresponses() as m:
            pipeline_id = pipelines[0]['id']
            m.get(
                f'https://api-key.fusionbrain.ai/key/api/v1/pipeline/{str(pipeline_id)}/availability',
                payload={'status': 'UNKNOWN STATUS'}
            )
            await async_client.get_pipeline_availability(pipeline_id=pipeline_id)


@pytest.mark.asyncio
async def test_run_pipeline(async_client):
    with aioresponses() as m:
        m.post(
            'https://api-key.fusionbrain.ai/key/api/v1/pipeline/run',
            status=HTTPStatus.CREATED,
            payload={'status': 'INITIAL', 'uuid': 'ffffffff-ffff-4e5e-ab06-ffffffffffff', 'status_time': 17}
        )
        got = await async_client.run_pipeline(pipeline_id='a17740da-e8a0-4816-876a-74326c5c4cef', prompt='Море')
        assert isinstance(got, RunPipelineResult)


@pytest.mark.asyncio
async def test_run_pipeline_blocked_model(async_client):
    with aioresponses() as m:
        m.post(
            'https://api-key.fusionbrain.ai/key/api/v1/pipeline/run',
            status=HTTPStatus.CREATED,
            payload={'model_status': 'DISABLED_MANUALLY'}
        )
        got = await async_client.run_pipeline(pipeline_id='a17740da-e8a0-4816-876a-74326c5c4cef', prompt='Море')
        assert isinstance(got, RunPipelineBlockedResult)


@pytest.mark.asyncio
async def test_run_pipeline_not_OK(async_client):
    with pytest.raises(ClientResponseError, match='In response to *'):
        with aioresponses() as m:
            m.post(
                'https://api-key.fusionbrain.ai/key/api/v1/pipeline/run',
                status=HTTPStatus.NOT_FOUND,
            )
            await async_client.run_pipeline(pipeline_id='a17740da-e8a0-4816-876a-74326c5c4cef', prompt='Море')


@pytest.mark.asyncio
async def test_get_status(async_client, pipeline_status_result):
    pipeline_status_result = pipeline_status_result.build().model_dump(mode='json')
    with aioresponses() as m:
        request_id = pipeline_status_result['uuid']
        m.get(
            f'https://api-key.fusionbrain.ai/key/api/v1/pipeline/status/{request_id}',
            payload=pipeline_status_result,
        )
        got = await async_client.get_status(uuid.UUID(request_id))
        assert isinstance(got, PipelineStatusResult)


@pytest.mark.asyncio
async def test_get_status_not_OK(async_client, pipeline_status_result):
    with pytest.raises(ClientResponseError, match='In response to *'):
        pipeline_status_result = pipeline_status_result.build().model_dump(mode='json')
        with aioresponses() as m:
            request_id = pipeline_status_result['uuid']
            m.get(
                f'https://api-key.fusionbrain.ai/key/api/v1/pipeline/status/{request_id}',
                status=HTTPStatus.NOT_FOUND,
            )
            got = await async_client.get_status(uuid.UUID(request_id))


@pytest.mark.parametrize('status_code, msg', [
    (HTTPStatus.UNAUTHORIZED, 'Ошибка авторизации'),
    (HTTPStatus.NOT_FOUND, 'Ресурс не найден'),
    (HTTPStatus.BAD_REQUEST, 'Неверные параметры запроса или текстовое описание слишком длинное'),
    (HTTPStatus.INTERNAL_SERVER_ERROR, 'Ошибка сервера при выполнении запроса'),
    (HTTPStatus.UNSUPPORTED_MEDIA_TYPE, 'Формат содержимого не поддерживается сервером'),
])
@pytest.mark.asyncio
async def test_get_status_custom_msgs(async_client, pipeline_status_result, status_code, msg):
    with pytest.raises(ClientResponseError, match='In response to *'):
        pipeline_status_result = pipeline_status_result.build().model_dump(mode='json')
        with aioresponses() as m:
            request_id = pipeline_status_result['uuid']
            m.get(
                f'https://api-key.fusionbrain.ai/key/api/v1/pipeline/status/{request_id}',
                status=status_code,
            )
            await async_client.get_status(uuid.UUID(request_id))


@pytest.mark.asyncio
async def test_wait_for_completion(async_client, pipeline_status_result, mocker):
    request_id = uuid.uuid4()
    
    status_results = [
        pipeline_status_result.build(status=PipelineResultStatus.INITIAL),
        pipeline_status_result.build(status=PipelineResultStatus.PROCESSING),
        pipeline_status_result.build(status=PipelineResultStatus.DONE),
    ]
    
    mocker.patch.object(
        async_client, 
        'get_status',
        side_effect=status_results
    )
    
    got = await async_client.wait_for_completion(request_id=request_id, initial_delay=0.1, sleep_interval=0.01)
    assert isinstance(got, PipelineStatusResult)
    assert got.status == PipelineResultStatus.DONE


@pytest.mark.asyncio
async def test_get_styles(async_client, styles):
    with aioresponses() as m:
        m.get(
            f'https://cdn.fusionbrain.ai/static/styles/key',
            status=HTTPStatus.OK,
            payload=styles,
        )
        got = await async_client.get_styles()
        assert isinstance(got, list)
        assert all(isinstance(style, Style) for style in got)
        assert got[0] == Style(**styles[0])


@pytest.mark.asyncio
async def test_get_styles_not_OK(async_client):
    with pytest.raises(ClientResponseError, match='In response to *'):
        with aioresponses() as m:
            m.get(
                'https://cdn.fusionbrain.ai/static/styles/key',
                status=HTTPStatus.NOT_FOUND,
            )
            await async_client.get_styles()

