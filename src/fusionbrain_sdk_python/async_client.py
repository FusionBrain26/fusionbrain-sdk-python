import asyncio
import json
import os
from http import HTTPStatus
from typing import List, Optional, Union
from uuid import UUID

import aiohttp
from dotenv import load_dotenv

from fusionbrain_sdk_python.abstract_client import AsyncClientProtocol
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

load_dotenv()


class AsyncFBClient(AsyncClientProtocol):
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

    async def get_pipelines(self) -> List[Pipeline]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_HOST + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS) as response:
                if response.status != HTTPStatus.OK:
                    msg = (
                        f'In response to {response.request_info.url} returned status'
                        f'code {response.status}. Reason: {await response.text()}'
                    )
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=msg,
                        headers=response.headers,
                    )
                data = await response.json()
                return [Pipeline.model_validate(pipe) for pipe in data]

    async def get_pipelines_by_type(self, pipe_type: PipelineType) -> List[Pipeline]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.API_HOST + 'key/api/v1/pipelines',
                headers=self.AUTH_HEADERS,
                params={'type': pipe_type.value},
            ) as response:
                if response.status != HTTPStatus.OK:
                    msg = (
                        f'In response to {response.request_info.url} returned status'
                        f'code {response.status}. Reason: {await response.text()}'
                    )
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=msg,
                        headers=response.headers,
                    )
                data = await response.json()
                return [Pipeline.model_validate(pipe) for pipe in data]

    async def get_pipeline_availability(self, pipeline_id: UUID) -> PipelineStatus:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.API_HOST + f'key/api/v1/pipeline/{str(pipeline_id)}/availability',
                headers=self.AUTH_HEADERS,
            ) as response:
                if response.status != HTTPStatus.OK:
                    msg = (
                        f'In response to {response.request_info.url} returned status'
                        f'code {response.status}. Reason: {await response.text()}'
                    )
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=msg,
                        headers=response.headers,
                    )
                result = PipelineAvailabilityResult.model_validate(await response.json())
                return result.status

    async def run_pipeline(
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
                'query': f'{prompt}',
            },
            **optional,
        }

        form_data = aiohttp.FormData()
        form_data.add_field('pipeline_id', str(pipeline_id))
        form_data.add_field(
            'params',
            json.dumps(params),
            content_type='application/json',
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.API_HOST + 'key/api/v1/pipeline/run',
                headers=self.AUTH_HEADERS,
                data=form_data,
            ) as response:
                if response.status != HTTPStatus.CREATED:
                    msg = (
                        f'In response to {response.request_info.url} returned status'
                        f'code {response.status}. Reason: {await response.text()}'
                    )
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=msg,
                        headers=response.headers,
                    )
                response_data = await response.json()
                if response_data.get('model_status'):
                    return RunPipelineBlockedResult.model_validate(response_data)
                return RunPipelineResult.model_validate(response_data)

    async def get_styles(self) -> List[Style]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.STYLES_URL,
            ) as response:
                if response.status != HTTPStatus.OK:
                    msg = (
                        f'In response to {response.request_info.url} returned status'
                        f'code {response.status}. Reason: {await response.text()}'
                    )
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=msg,
                        headers=response.headers,
                    )
                return [Style.model_validate(res) for res in await response.json()]

    async def get_status(self, request_id: UUID) -> PipelineStatusResult:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.API_HOST + f'key/api/v1/pipeline/status/{request_id}',
                headers=self.AUTH_HEADERS,
            ) as response:
                if response.status != HTTPStatus.OK:
                    status = HTTPStatus(response.status)
                    status_name = status.name
                    msg_custom = (
                        PipelineCodeStatusResult[status_name].value
                        if status_name in PipelineCodeStatusResult.__members__
                        else response.reason
                    )
                    msg = (
                        f'In response to {response.request_info.url} returned status {status_name} '
                        f'code {response.status}, reason: {msg_custom}.'
                    )
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=msg,
                        headers=response.headers,
                    )
                
                return PipelineStatusResult.model_validate(await response.json())

    async def wait_for_completion(
        self,
        request_id: UUID,
        initial_delay: int,
        sleep_interval: int = 1,
        max_retries: int = 5,
    ) -> PipelineStatusResult:
        await asyncio.sleep(initial_delay)
        for _ in range(max_retries):
            status_result = await self.get_status(request_id)
            if status_result.status in [PipelineResultStatus.DONE, PipelineResultStatus.FAIL]:
                return status_result
            await asyncio.sleep(sleep_interval)
        raise TimeoutError(f'Failed to get result for request {request_id} after {max_retries} retries.')
