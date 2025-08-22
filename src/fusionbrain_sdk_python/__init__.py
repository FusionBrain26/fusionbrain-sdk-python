"""FusionBrain SDK for Python.

This SDK provides a client for the FusionBrain API.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _get_version

try:
    __version__ = _get_version('fusionbrain-sdk-python')
except PackageNotFoundError:
    __version__ = '0.0.0'

from fusionbrain_sdk_python.async_client import AsyncFBClient
from fusionbrain_sdk_python.client import FBClient
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

__all__ = [
    'FBClient',
    'AsyncFBClient',
    'Pipeline',
    'PipelineAvailabilityResult',
    'PipelineCodeStatusResult',
    'PipelineResultStatus',
    'PipelineStatus',
    'PipelineStatusResult',
    'PipelineType',
    'RunPipelineResult',
    'RunPipelineBlockedResult',
    'Style',
    'ConfigError',
]
