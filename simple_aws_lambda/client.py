# -*- coding: utf-8 -*-

import typing as T

import botocore.exceptions
from func_args.api import OPT, remove_optional

from .model import (
    LatestMatchingLayerVersion,
    Layer,
    LayerContent,
    LayerVersion,
    LayerIterproxy,
    LayerVersionIterproxy,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_lambda.client import LambdaClient


def list_layers(
    lambda_client: "LambdaClient",
    compatible_runtime: str = OPT,
    compatible_architecture: str = OPT,
    max_items: int = 9999,
) -> LayerIterproxy:
    """
    Ref:

    - `list_layers <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/list_layers.html>`_
    """

    def func():
        paginator = lambda_client.get_paginator("list_layers")
        response_iterator = paginator.paginate(
            **remove_optional(
                CompatibleRuntime=compatible_runtime,
                CompatibleArchitecture=compatible_architecture,
                PaginationConfig={
                    "MaxItems": max_items,
                    "PageSize": 100,
                },
            )
        )
        for response in response_iterator:
            for _data in response.get("Layers", []):
                yield Layer(_data=_data)

    return LayerIterproxy(func())


def list_layer_versions(
    lambda_client: "LambdaClient",
    compatible_runtime: str = OPT,
    compatible_architecture: str = OPT,
    max_items: int = 9999,
):
    """
    Ref:

    - `list_layer_versions <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/list_layer_versions.html>`_
    """

    def func():
        paginator = lambda_client.get_paginator("list_layer_versions")
        response_iterator = paginator.paginate(
            **remove_optional(
                CompatibleRuntime=compatible_runtime,
                CompatibleArchitecture=compatible_architecture,
                PaginationConfig={
                    "MaxItems": max_items,
                    "PageSize": 100,
                },
            )
        )
        for response in response_iterator:
            for _data in response.get("LayerVersions", []):
                yield LayerVersion(_data=_data)

    return LayerVersionIterproxy(func())


def get_layer_version(
    lambda_client: "LambdaClient",
    layer_name: str,
    version_number: int,
) -> LayerVersion | None:
    """
    Ref:

    - `get_layer_version <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/get_layer_version.html>`_
    """
    try:
        response = lambda_client.get_layer_version(
            LayerName=layer_name,
            VersionNumber=version_number,
        )
        return LayerVersion(_data=response)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return None
        else:
            raise e
