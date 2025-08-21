from datetime import datetime
from enum import Enum
from typing import List, Optional, Sequence

from pydantic import UUID4, BaseModel, Field


class PipelineStatus(str, Enum):
    ACTIVE = 'ACTIVE'
    DISABLED_MANUALLY = 'DISABLED_MANUALLY'
    DISABLED_BY_QUEUE = 'DISABLED_BY_QUEUE'


class PipelineType(str, Enum):
    TEXT2IMAGE = 'TEXT2IMAGE'


class Tag(BaseModel):
    name: str = Field(..., description='Name of the tag on russian language')
    name_en: str = Field(..., description='Name of the tag on english language')


class Pipeline(BaseModel):
    id: UUID4 = Field(..., description='Unique identifier of the pipeline')
    name: str = Field(..., description='Name of the pipeline on russian language')
    description: Optional[str] = Field(..., description='Description of the pipeline on russian language')
    tags: Sequence[Tag] = Field(..., description='Tags associated with this pipeline')
    version: float = Field(..., ge=0.1, description='Version of the pipeline')
    status: PipelineStatus = Field(..., description='Status of the pipeline')
    type: PipelineType = Field(..., description='Type of the pipeline')
    createdDate: datetime = Field(..., description='Date when this pipeline was created')
    lastModified: datetime = Field(..., description='Last date when this pipeline was modified')


class PipelineAvailabilityResult(BaseModel):
    status: PipelineStatus = Field(..., description='Status of the pipeline availability')


class PipelineResultStatus(str, Enum):
    INITIAL = 'INITIAL'
    PROCESSING = 'PROCESSING'
    DONE = 'DONE'
    FAIL = 'FAIL'


class ModelStatus(str, Enum):
    DISABLED_MANUALLY = 'DISABLED_MANUALLY'
    DISABLED_BY_QUEUE = 'DISABLED_BY_QUEUE'


class RunPipelineBlockedResult(BaseModel):
    model_status: ModelStatus = Field(...)


class RunPipelineResult(BaseModel):
    uuid: UUID4 = Field(...)
    status: PipelineResultStatus = Field(...)
    status_time: int = Field(...)


class PipelineResult(BaseModel):
    files: List[str] = Field(...)
    censored: bool = Field(...)


class PipelineStatusResult(BaseModel):
    uuid: UUID4 = Field(...)
    status: PipelineResultStatus = Field(...)
    result: Optional[PipelineResult] = Field(default=None)
    generationTime: Optional[int] = Field(default=None)


class Style(BaseModel):
    name: str = Field(...)
    title: str = Field(...)
    titleEn: str = Field(...)
    image: str = Field(...)


class PipelineCodeStatusResult(str, Enum):
    UNAUTHORIZED = 'Ошибка авторизации'
    NOT_FOUND = 'Ресурс не найден'
    BAD_REQUEST = 'Неверные параметры запроса или текстовое описание слишком длинное'
    INTERNAL_SERVER_ERROR = 'Ошибка сервера при выполнении запроса'
    UNSUPPORTED_MEDIA_TYPE = 'Формат содержимого не поддерживается сервером'
