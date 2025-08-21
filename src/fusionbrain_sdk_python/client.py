import json
import os
import time
from http import HTTPStatus
from typing import List, Optional, Union
from uuid import UUID

from dotenv import load_dotenv
from requests.exceptions import HTTPError

from fusionbrain_sdk_python.abstract_client import SyncClientProtocol
from fusionbrain_sdk_python.exceptions import ConfigError
from fusionbrain_sdk_python.models import (
    Pipeline,
    PipelineAvailabilityResult,
    PipelineCodeStatusResult,
    PipelineResultStatus,
    PipelineStatus,
    PipelineStatusResult,
    PipelineType,
    RunPipelineBlockedResult,
    RunPipelineResult,
    Style,
)
from fusionbrain_sdk_python.session import Session

load_dotenv()


class FBClient(SyncClientProtocol):
    def __init__(self, x_key: Optional[str] = None, x_secret: Optional[str] = None) -> None:
        _FB_API_KEY = os.getenv('FB_API_KEY') or x_key
        _FB_API_SECRET = os.getenv('FB_API_SECRET') or x_secret
        if not _FB_API_KEY or not _FB_API_SECRET:
            raise ConfigError(
                'Please set `FB_API_KEY` and `FB_API_SECRET` tokens in initial method or environment variables.',
            )
        self.AUTH_HEADERS = {
            'X-Key': f'Key {_FB_API_KEY}',
            'X-Secret': f'Secret {_FB_API_SECRET}',
        }
        self.session = Session().get_session()

    def get_pipelines(self) -> List[Pipeline]:
        response = self.session.get(self.API_HOST + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        if response.status_code != HTTPStatus.OK:
            msg = (
                f'In response to {response.request.url} returned status'
                f'code {response.status_code}. Reason: {response.content.decode()}'
            )
            raise HTTPError(msg)
        return [Pipeline.model_validate(pipe) for pipe in response.json()]

    def get_pipelines_by_type(self, pipe_type: PipelineType) -> List[Pipeline]:
        response = self.session.get(
            self.API_HOST + 'key/api/v1/pipelines',
            headers=self.AUTH_HEADERS,
            params={'type': pipe_type.value},
        )
        if response.status_code != HTTPStatus.OK:
            msg = (
                f'In response to {response.request.url} returned status'
                f'code {response.status_code}. Reason: {response.content.decode()}'
            )
            raise HTTPError(msg)
        
        return [Pipeline.model_validate(pipe) for pipe in response.json()]

    def get_pipeline_availability(self, pipeline_id: UUID) -> PipelineStatus:
        response = self.session.get(
            self.API_HOST + f'key/api/v1/pipeline/{str(pipeline_id)}/availability',
            headers=self.AUTH_HEADERS,
        )
        if response.status_code != HTTPStatus.OK:
            msg = (
                f'In response to {response.request.url} returned status'
                f'code {response.status_code}. Reason: {response.content.decode()}'
            )
            raise HTTPError(msg)
        result = PipelineAvailabilityResult.model_validate(response.json())
        return result.status

    def run_pipeline(
        self,
        pipeline_id: UUID,
        prompt: str,
        negative_prompt: Optional[str] = None,
        style: Optional[Union[str, Style]] = None,
        height: int = 1024,
        width: int = 1024,
        num_images: int = 1,
    ) -> Union[RunPipelineResult, RunPipelineBlockedResult]: 
        optional = {
            **({'negativePromptDecoder': negative_prompt} if negative_prompt else {}),
            **({'style': style.name if isinstance(style, Style) else style} if style else {}),
        }
        params = {
            'type': 'GENERATE',
            'numImages': num_images,
            'width': width,
            'height': height,
            'generateParams': {
                'query': prompt,
            },
            **optional,
        }

        data = {
            'pipeline_id': (None, str(pipeline_id)),
            'params': (None, json.dumps(params), 'application/json'),
        }
        response = self.session.post(
            self.API_HOST + 'key/api/v1/pipeline/run',
            headers=self.AUTH_HEADERS,
            files=data,  # type: ignore
        )
        if response.status_code != HTTPStatus.CREATED:
            msg = (
                f'In response to {response.request.url} returned status'
                f'code {response.status_code}. Reason: {response.content.decode()}'
            )
            raise HTTPError(msg)

        if response.json().get('model_status'):
            return RunPipelineBlockedResult.model_validate(response.json())
        return RunPipelineResult.model_validate(response.json())

    def get_styles(self) -> List[Style]:
        response = self.session.get(
            self.STYLES_URL,
            headers=self.AUTH_HEADERS,
        )
        if response.status_code != HTTPStatus.OK:
            msg = (
                f'In response to {response.request.url} returned status'
                f'code {response.status_code}. Reason: {response.content.decode()}'
            )
            raise HTTPError(msg)
        return [Style.model_validate(res) for res in response.json()]

    def get_status(self, request_id: UUID) -> PipelineStatusResult:
        response = self.session.get(
            self.API_HOST + f'key/api/v1/pipeline/status/{request_id}',
            headers=self.AUTH_HEADERS,
        )
        if response.status_code != HTTPStatus.OK:
            status = HTTPStatus(response.status_code)
            status_name = status.name
            msg_custom = (
                PipelineCodeStatusResult[status_name].value if status_name in PipelineCodeStatusResult.__members__
                else response.reason
            )
            msg = (
                f'In response to {response.request.url} returned status {status_name} '
                f'code {response.status_code}, reason: {msg_custom}.'
            )
            raise HTTPError(msg)
        
        return PipelineStatusResult.model_validate(response.json())

    def wait_for_completion(
        self,
        request_id: UUID,
        initial_delay: int,
        sleep_interval: int = 1,
        max_retries: int = 5,
    ) -> PipelineStatusResult:
        time.sleep(initial_delay)
        for _ in range(max_retries):
            status_result = self.get_status(request_id)
            if status_result.status in [PipelineResultStatus.DONE, PipelineResultStatus.FAIL]:
                return status_result
            time.sleep(sleep_interval)
        raise TimeoutError(f'Failed to get result for request {request_id} after {max_retries} retries.')
