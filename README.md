# FusionBrain SDK for Python

This SDK provides a convenient way to interact with the FusionBrain API for generating images and other content. It includes both synchronous and asynchronous clients to suit different programming needs.

## Features

-   Synchronous and Asynchronous clients.
-   Helper methods for checking pipeline status and availability.
-   Built-in mechanism for waiting for task completion with configurable retries.
-   Pydantic models for clear and safe data handling.

## Installation

You can install the SDK using pip:

```bash
pip install fusionbrain-sdk-python
```

## Getting Started

### Authentication

To use the API, you need an API key and a secret. You can provide them in two ways:

1.  **Directly to the client constructor:**

    ```python
    from fusionbrain_sdk_python import FBClient

    client = FBClient(x_key="YOUR_API_KEY", x_secret="YOUR_API_SECRET")
    ```

2.  **Using environment variables:**

    Create a `.env` file in your project root:

    ```
    FB_API_KEY="YOUR_API_KEY"
    FB_API_SECRET="YOUR_API_SECRET"
    ```

    The client will automatically pick up these variables.

### Synchronous Usage Example

This example demonstrates the basic workflow for generating an image.

```python
from fusionbrain_sdk_python import FBClient, PipelineType

# Initialize the client (assumes keys are in .env or passed directly)
client = FBClient()

# 1. Get a text-to-image pipeline
pipelines = client.get_pipelines_by_type(PipelineType.TEXT2IMAGE)
text2image_pipeline = pipelines[0]  # Using the first available pipeline
print(f"Using pipeline: {text2image_pipeline.name}")

# 2. Run the generation
run_result = client.run_pipeline(
    pipeline_id=text2image_pipeline.id,
    prompt="A red cat sitting on a table"
)

# 3. Wait for the final result
print(f"Task started with UUID: {run_result.uuid}")
final_status = client.wait_for_completion(
    request_id=run_result.uuid,
    initial_delay=run_result.status_time
)

if final_status.status == 'DONE':
    print("Generation successful!")
    # The result contains a list of base64-encoded images
    # print(final_status.result.files)
else:
    print(f"Generation failed with status: {final_status.status}")

```

### Asynchronous Usage Example

The asynchronous client offers the same functionality for `asyncio` applications.

```python
import asyncio
from fusionbrain_sdk_python import AsyncFBClient, PipelineType

async def main():
    async_client = AsyncFBClient()

    # 1. Get a text-to-image pipeline
    pipelines = await async_client.get_pipelines_by_type(PipelineType.TEXT2IMAGE)
    text2image_pipeline = pipelines[0]  # Using the first available pipeline
    print(f"Using pipeline: {text2image_pipeline.name}")

    # 2. Run the generation
    run_result = await async_client.run_pipeline(
        pipeline_id=text2image_pipeline.id,
        prompt="A blue bird flying in the sky"
    )

    # 3. Wait for the final result
    print(f"Task started with UUID: {run_result.uuid}")
    final_status = await async_client.wait_for_completion(
        request_id=run_result.uuid,
        initial_delay=run_result.status_time
    )

    if final_status.status == 'DONE':
        print("Generation successful!")
        # The result contains a list of base64-encoded images
        # print(final_status.result.files)
    else:
        print(f"Generation failed with status: {final_status.status}")

if __name__ == "__main__":
    asyncio.run(main())

```
