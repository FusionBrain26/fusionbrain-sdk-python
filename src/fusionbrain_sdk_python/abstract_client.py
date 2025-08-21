from typing import List, Optional, Protocol, Union
from uuid import UUID

from fusionbrain_sdk_python.models import (
    Pipeline,
    PipelineStatus,
    PipelineStatusResult,
    PipelineType,
    RunPipelineBlockedResult,
    RunPipelineResult,
    Style,
)


class SyncClientProtocol(Protocol):
    API_HOST: str = 'https://api-key.fusionbrain.ai/'
    STYLES_URL: str = 'https://cdn.fusionbrain.ai/static/styles/key'

    def get_pipelines(self) -> List[Pipeline]: ...
    def get_pipelines_by_type(self, pipe_type: PipelineType) -> List[Pipeline]: ...
    def get_pipeline_availability(self, pipeline_id: UUID) -> PipelineStatus: ...
    def run_pipeline(
        self,
        pipeline_id: UUID,
        prompt: str,
        negative_prompt: Optional[str] = None,
        style: Optional[Union[str, Style]] = None,
        height: int = 1024,
        width: int = 1024,
        num_images: int = 1,
    ) -> Union[RunPipelineResult, RunPipelineBlockedResult]: ...
    def get_styles(self) -> List[Style]: ...
    def get_status(self, request_id: UUID) -> PipelineStatusResult: ...
    def wait_for_completion(
        self,
        request_id: UUID,
        initial_delay: int,
        sleep_interval: int = 1,
        max_retries: int = 30,
    ) -> PipelineStatusResult: ...


class AsyncClientProtocol(Protocol):
    API_HOST: str = 'https://api-key.fusionbrain.ai/'
    STYLES_URL: str = 'https://cdn.fusionbrain.ai/static/styles/key'

    async def get_pipelines(self) -> List[Pipeline]: ...
    async def get_pipelines_by_type(self, pipe_type: PipelineType) -> List[Pipeline]: ...
    async def get_pipeline_availability(self, pipeline_id: UUID) -> PipelineStatus: ...
    async def run_pipeline(
        self,
        pipeline_id: UUID,
        prompt: str,
        negative_prompt: Optional[str] = None,
        style: Optional[Union[str, Style]] = None,
        height: int = 1024,
        width: int = 1024,
        num_images: int = 1,
    ) -> Union[RunPipelineResult, RunPipelineBlockedResult]: ...
    async def get_styles(self) -> List[Style]: ...
    async def get_status(self, request_id: UUID) -> PipelineStatusResult: ...
    async def wait_for_completion(
        self,
        request_id: UUID,
        initial_delay: int,
        sleep_interval: int = 1,
        max_retries: int = 30,
    ) -> PipelineStatusResult: ...
