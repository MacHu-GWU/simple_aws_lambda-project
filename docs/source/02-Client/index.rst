Better Boto3 Client
==============================================================================
This library provides a more Pythonic interface to AWS Lambda by wrapping the standard boto3 client. It adds idempotence, returns :ref:`data-model` objects instead of raw dictionaries, and provides better error handling with enhanced pagination support.

Below are the full list of available client functions:

**Layer Discovery:**

- :func:`~simple_aws_lambda.client.list_layers`: List available AWS Lambda layers in the account with filtering and pagination support
- :func:`~simple_aws_lambda.client.list_layer_versions`: List all versions of Lambda layers in the account with compatibility filtering

**Layer Retrieval:**

- :func:`~simple_aws_lambda.client.get_layer_version`: Retrieve details for a specific Lambda layer version, returns None if not found