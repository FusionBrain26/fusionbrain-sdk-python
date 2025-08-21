import uuid
from http import HTTPStatus

import pytest
import requests_mock
from pydantic import ValidationError
from requests import HTTPError

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


def test_get_pipelines(client, pipelines):
    with requests_mock.Mocker() as m:
        m.get('https://api-key.fusionbrain.ai/key/api/v1/pipelines', json=pipelines)
        got = client.get_pipelines()
        assert isinstance(got, list)
        assert all(isinstance(pipe, Pipeline) for pipe in got)
        assert got[0] == Pipeline(**pipelines[0])


def test_get_pipeline_not_OK(client):
    with pytest.raises(HTTPError, match='In response to *'):
        with requests_mock.Mocker() as m:
            m.get(
                'https://api-key.fusionbrain.ai/key/api/v1/pipelines',
                status_code=HTTPStatus.NOT_FOUND,
            )
            client.get_pipelines()


def test_get_pipelines_by_type(client, pipelines):
    with requests_mock.Mocker() as m:
        m.get('https://api-key.fusionbrain.ai/key/api/v1/pipelines', json=pipelines)
        got = client.get_pipelines_by_type(pipe_type=PipelineType.TEXT2IMAGE)
        assert isinstance(got, list)
        assert all(isinstance(pipe, Pipeline) for pipe in got)
        assert all(pipe.type == 'TEXT2IMAGE' for pipe in got)


def test_get_pipelines_by_type_not_OK(client):
    with pytest.raises(HTTPError, match='In response to *'):
        with requests_mock.Mocker() as m:
            m.get(
                'https://api-key.fusionbrain.ai/key/api/v1/pipelines',
                status_code=HTTPStatus.NOT_FOUND,
            )
            client.get_pipelines_by_type(pipe_type=PipelineType.TEXT2IMAGE)


def test_get_pipeline_availability(client, pipelines):
    with requests_mock.Mocker() as m:
        pipeline_id = pipelines[0]['id']
        m.get(
            f'https://api-key.fusionbrain.ai/key/api/v1/pipeline/{str(pipeline_id)}/availability',
            json={'status': 'ACTIVE'}
        )
        got = client.get_pipeline_availability(pipeline_id=pipeline_id)
        assert isinstance(got, PipelineStatus)
        assert got == PipelineStatus.ACTIVE


def test_get_pipeline_availability_not_OK(client, pipelines):
    with pytest.raises(HTTPError, match='In response to *'):
        with requests_mock.Mocker() as m:
            pipeline_id = pipelines[0]['id']
            m.get(
                f'https://api-key.fusionbrain.ai/key/api/v1/pipeline/{str(pipeline_id)}/availability',
                status_code=HTTPStatus.NOT_FOUND,
            )
            client.get_pipeline_availability(pipeline_id=pipeline_id)


def test_get_pipeline_availability_unknown_status(client, pipelines):
    with pytest.raises(ValidationError, match='1 validation error for PipelineAvailabilityResult*'):
        with requests_mock.Mocker() as m:
            pipeline_id = pipelines[0]['id']
            m.get(
                f'https://api-key.fusionbrain.ai/key/api/v1/pipeline/{str(pipeline_id)}/availability',
                json={'status': 'UNKNOWN STATUS'}
            )
            got = client.get_pipeline_availability(pipeline_id=pipeline_id)


def test_run_pipeline(client):
    with requests_mock.Mocker() as m:
        m.post(
            'https://api-key.fusionbrain.ai/key/api/v1/pipeline/run',
            status_code=HTTPStatus.CREATED,
            json={'status': 'INITIAL', 'uuid': 'ffffffff-ffff-4e5e-ab06-ffffffffffff', 'status_time': 17}
        )
        got = client.run_pipeline(pipeline_id='a17740da-e8a0-4816-876a-74326c5c4cef', prompt='Море')
        assert isinstance(got, RunPipelineResult)


def test_run_pipeline_blocked_model(client):
    with requests_mock.Mocker() as m:
        m.post(
            'https://api-key.fusionbrain.ai/key/api/v1/pipeline/run',
            status_code=HTTPStatus.CREATED,
            json={'model_status': 'DISABLED_MANUALLY'}
        )
        got = client.run_pipeline(pipeline_id='a17740da-e8a0-4816-876a-74326c5c4cef', prompt='Море')
        assert isinstance(got, RunPipelineBlockedResult)


def test_run_pipeline_not_OK(client):
    with pytest.raises(HTTPError, match='In response to *'):
        with requests_mock.Mocker() as m:
            m.post(
                'https://api-key.fusionbrain.ai/key/api/v1/pipeline/run',
                status_code=HTTPStatus.NOT_FOUND,
            )
            got = client.run_pipeline(pipeline_id='a17740da-e8a0-4816-876a-74326c5c4cef', prompt='Море')


def test_get_status(client, pipeline_status_result):
    pipeline_status_result = pipeline_status_result.build().model_dump(mode='json')
    with requests_mock.Mocker() as m:
        request_id = pipeline_status_result['uuid']
        m.get(
            f'https://api-key.fusionbrain.ai/key/api/v1/pipeline/status/{request_id}',
            json=pipeline_status_result,
        )
        got = client.get_status(uuid.UUID(request_id))
        assert isinstance(got, PipelineStatusResult)


def test_get_status_not_OK(client, pipeline_status_result):
    with pytest.raises(HTTPError, match='In response to *'):
        pipeline_status_result = pipeline_status_result.build().model_dump(mode='json')
        with requests_mock.Mocker() as m:
            request_id = pipeline_status_result['uuid']
            m.get(
                f'https://api-key.fusionbrain.ai/key/api/v1/pipeline/status/{request_id}',
                status_code=HTTPStatus.NOT_FOUND,
            )
            got = client.get_status(uuid.UUID(request_id))


@pytest.mark.parametrize('status_code, msg', [
    (HTTPStatus.UNAUTHORIZED, 'Ошибка авторизации'),
    (HTTPStatus.NOT_FOUND, 'Ресурс не найден'),
    (HTTPStatus.BAD_REQUEST, 'Неверные параметры запроса или текстовое описание слишком длинное'),
    (HTTPStatus.INTERNAL_SERVER_ERROR, 'Ошибка сервера при выполнении запроса'),
    (HTTPStatus.UNSUPPORTED_MEDIA_TYPE, 'Формат содержимого не поддерживается сервером'),
])
def test_get_status_custom_msgs(client, pipeline_status_result, status_code, msg):
    with pytest.raises(HTTPError, match=msg):
        pipeline_status_result = pipeline_status_result.build().model_dump(mode='json')
        with requests_mock.Mocker() as m:
            request_id = pipeline_status_result['uuid']
            m.get(
                f'https://api-key.fusionbrain.ai/key/api/v1/pipeline/status/{request_id}',
                status_code=status_code,
            )
            got = client.get_status(uuid.UUID(request_id))


def test_wait_for_completion(client, pipeline_status_result, mocker):
    request_id = uuid.uuid4()
    mock_status_results = [
        pipeline_status_result.build(status=PipelineResultStatus.INITIAL),
        pipeline_status_result.build(status=PipelineResultStatus.PROCESSING),
        pipeline_status_result.build(status=PipelineResultStatus.DONE),
    ]

    mocker.patch(
        'fusionbrain_sdk_python.client.FBClient.get_status',
        side_effect=mock_status_results
    )

    got = client.wait_for_completion(request_id=request_id, initial_delay=0.1, sleep_interval=0.01)
    assert isinstance(got, PipelineStatusResult)
    assert got.status == PipelineResultStatus.DONE


def test_get_styles(client, styles):
    with requests_mock.Mocker() as m:
        m.get(
            f'https://cdn.fusionbrain.ai/static/styles/key',
            status_code=HTTPStatus.OK,
            json=styles,
        )
        got = client.get_styles()
        assert isinstance(got, list)
        assert all(isinstance(style, Style) for style in got)
        assert got[0] == Style(**styles[0])

def test_get_styles_not_OK(client):
    with pytest.raises(HTTPError, match='In response to *'):
        with requests_mock.Mocker() as m:
            m.get(
                'https://cdn.fusionbrain.ai/static/styles/key',
                status_code=HTTPStatus.NOT_FOUND,
            )
            client.get_styles()
