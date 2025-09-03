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
) -> LayerVersion | None:
    """
    Call the AWS Lambda Layer API to retrieve the latest deployed layer version.
    If it returns ``None``, it indicates that no layer has been deployed yet.

    Example: if layer has version 1, 2, 3, then this function return 3.
    If there's no layer version created yet, then this function returns None.

    Reference:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.list_layer_versions
    """
    layer_versions = list_layer_versions(
        lambda_client=lambda_client,
        layer_name=layer_name,
        compatible_runtime=compatible_runtime,
        compatible_architecture=compatible_architecture,
        max_items=1,
    ).all()
    if len(layer_versions) == 0:
        return None
    else:
        return layer_versions[0]


def cleanup_old_layer_versions(
    lambda_client: "LambdaClient",
    layer_name: str,
    keep_last_n_versions: int = 5,
    keep_versions_newer_than_days: int = 90,
    dry_run: bool = True,
) -> T.List[int]:
    """
    Delete old Lambda layer versions based on retention policy.

    Keeps layer versions if they meet ANY of these conditions:

    - Among the last N versions (most recent)
    - Created within the last N days

    :param lambda_client: AWS Lambda client
    :param layer_name: Name of the Lambda layer
    :param keep_last_n_versions: Number of most recent versions to keep
    :param keep_versions_newer_than_days: Keep versions newer than this many days
    :param dry_run: If True, only return versions that would be deleted without actually deleting

    :returns: List of version numbers that were deleted (or would be deleted in dry run mode)

    Ref:

    - `delete_layer_version <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/delete_layer_version.html>`_
    """
    # Get all layer versions sorted by version number (newest first)
    all_versions = list_layer_versions(
        lambda_client=lambda_client,
        layer_name=layer_name,
        max_items=keep_last_n_versions,
    ).all()

    if not all_versions:
        return []

    # Sort by version number in descending order (newest first)
    all_versions.sort(key=lambda v: v.version, reverse=True)

    # Calculate cutoff date
    cutoff_date = datetime.now(timezone.utc) - timedelta(
        days=keep_versions_newer_than_days
    )

    versions_to_delete = []

    for i, version in enumerate(all_versions):
        # Keep if it's among the last N versions
        if i < keep_last_n_versions:
            continue

        # Keep if it's newer than cutoff date
        if version.created_datetime > cutoff_date:
            continue

        # This version should be deleted
        versions_to_delete.append(version.version)

    # Delete the versions (unless dry run)
    deleted_versions = []
    for version_number in versions_to_delete:
        if not dry_run:
            try:
                lambda_client.delete_layer_version(
                    LayerName=layer_name,
                    VersionNumber=version_number,
                )
                deleted_versions.append(version_number)
            except botocore.exceptions.ClientError as e:
                # Continue with other versions even if one fails
                pass
        else:
            deleted_versions.append(version_number)

    return deleted_versions
