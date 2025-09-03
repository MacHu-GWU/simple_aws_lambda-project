# -*- coding: utf-8 -*-

import typing as T
from datetime import datetime, timezone, timedelta

import botocore.exceptions
from func_args.api import OPT

from .model import (
    LayerVersion,
)
from .client import (
    list_layer_versions,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_lambda.client import LambdaClient


def get_latest_layer_version(
    lambda_client: "LambdaClient",
    layer_name: str,
    compatible_runtime: str = OPT,
    compatible_architecture: str = OPT,
    _sort_descending: bool = False,
) -> LayerVersion | None:
    """
    Call the AWS Lambda Layer API to retrieve the latest deployed layer version.
    If it returns ``None``, it indicates that no layer has been deployed yet.

    Example: if layer has version 1, 2, 3, then this function return 3.
    If there's no layer version created yet, then this function returns None.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.list_layer_versions
    """
    if _sort_descending:
        max_items = 10
    else:
        max_items = 1
    layer_versions = list_layer_versions(
        lambda_client=lambda_client,
        layer_name=layer_name,
        compatible_runtime=compatible_runtime,
        compatible_architecture=compatible_architecture,
        max_items=max_items,
        _sort_descending=_sort_descending,
    ).all()
    if len(layer_versions) == 0:
        return None
    else:
        return layer_versions[0]


def cleanup_old_layer_versions(
    lambda_client: "LambdaClient",
    layer_name: str,
    keep_last_n_versions: int = 5,
    keep_versions_newer_than_seconds: int = 90 * 24 * 60 * 60,
    real_run: bool = False,
    _sort_descending: bool = False,
) -> list[int]:
    """
    Delete old Lambda layer versions based on retention policy.

    Keeps layer versions if they meet ANY of these conditions:

    - Among the last N versions (most recent)
    - Created within the last N seconds

    :param lambda_client: AWS Lambda client
    :param layer_name: Name of the Lambda layer
    :param keep_last_n_versions: Number of most recent versions to keep
    :param keep_versions_newer_than_seconds: Keep versions newer than this many seconds
    :param real_run: If True, actually delete versions. If False, only return what would be deleted

    :returns: List of version numbers that were deleted (or would be deleted in simulation mode)

    Ref:

    - `delete_layer_version <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/delete_layer_version.html>`_
    """
    # Get all layer versions
    all_versions = list_layer_versions(
        lambda_client=lambda_client,
        layer_name=layer_name,
        max_items=9999,
        _sort_descending=True,
    ).all()

    # Only exam versions beyond the last N to keep
    other_versions = all_versions[keep_last_n_versions:]

    if len(other_versions) == 0:
        return []

    # Calculate cutoff date
    delta = timedelta(seconds=keep_versions_newer_than_seconds)
    cutoff_date = datetime.now(timezone.utc) - delta

    versions_to_delete = []

    for version in other_versions:
        # Keep if it's newer than cutoff date
        if version.created_datetime > cutoff_date:  # pragma: no cover
            continue

        # This version should be deleted
        versions_to_delete.append(version.version)

    # Delete the versions (if real_run is True)
    deleted_versions = []
    for version_number in versions_to_delete:
        deleted_versions.append(version_number)
        if real_run:
            try:
                lambda_client.delete_layer_version(
                    LayerName=layer_name,
                    VersionNumber=version_number,
                )
            except botocore.exceptions.ClientError:  # pragma: no cover
                # Continue with other versions even if one fails
                pass

    return deleted_versions
