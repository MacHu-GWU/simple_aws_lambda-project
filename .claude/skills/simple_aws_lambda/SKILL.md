---
name: simple_aws_lambda
description: Python library simple_aws_lambda (v0.3.1), an object oriented wrapper over the boto3 Lambda client for Lambda layers. Lists layers and layer versions as typed objects, gets the latest layer version, deletes old layer versions with a retention policy, and grants or revokes cross account layer access idempotently. Public API: list_layers, list_layer_versions, get_layer_version, get_latest_layer_version, cleanup_old_layer_versions, grant_/revoke_aws_account_or_aws_organization_lambda_layer_version_access, Layer, LayerVersion, LayerContent.
---

# simple_aws_lambda

Wraps a boto3 Lambda client (you pass it in; the library never creates sessions) and returns frozen dataclass objects instead of dicts. Every model keeps the raw boto3 response in `_data` and exposes fields as read-only properties. Pagination is handled for you; list functions return lazy iterators. Focus is Lambda **layers**. Python 3.11+.

## Import

```python
from simple_aws_lambda.api import list_layers
import simple_aws_lambda.api as simple_aws_lambda  # then simple_aws_lambda.list_layers
```

`lambda_client` below is always `boto3.Session(...).client("lambda")`.

## Public API

**Client functions** (one boto3 call each, paginated)

- `list_layers(lambda_client, compatible_runtime: str = OPT, compatible_architecture: str = OPT, max_items: int = 9999, page_size: int = 50) -> LayerIterproxy`: all layers in the account/region.
- `list_layer_versions(lambda_client, layer_name: str, compatible_runtime: str = OPT, compatible_architecture: str = OPT, max_items: int = 9999, page_size: int = 50) -> LayerVersionIterproxy`: versions of one layer, newest first.
- `get_layer_version(lambda_client, layer_name: str, version_number: int) -> LayerVersion | None`: one version with content details; `None` if it does not exist.

`OPT` means "not sent to AWS"; just omit the argument.

**Recipes**

- `get_latest_layer_version(lambda_client, layer_name: str, compatible_runtime: str = OPT, compatible_architecture: str = OPT) -> LayerVersion | None`: newest version; `None` if never published.
- `cleanup_old_layer_versions(lambda_client, layer_name: str, keep_last_n_versions: int = 5, keep_versions_newer_than_seconds: int = 7776000, real_run: bool = False) -> list[int]`: deletes versions that are neither among the last N nor newer than the age limit (default 90 days). Returns deleted version numbers, newest first. **Dry run by default**: pass `real_run=True` to delete.
- `grant_aws_account_or_aws_organization_lambda_layer_version_access(lambda_client, layer_name: str, version_number: int, principal: str) -> None`: grants `lambda:GetLayerVersion`. `principal` is a 12 digit account id, an org id `o-...`, or `"*"` (public). Idempotent.
- `revoke_aws_account_or_aws_organization_lambda_layer_version_access(lambda_client, layer_name: str, version_number: int, principal: str) -> None`: removes that grant. Idempotent.

**Models** (frozen dataclasses, one field `_data: dict`, everything else is a property)

- `Layer`: `layer_name`, `layer_arn`, `latest_matching_version -> LatestMatchingLayerVersion | None`, `has_latest_version`, `core_data`.
- `LatestMatchingLayerVersion`: `layer_version_arn`, `version`, `description`, `created_date`, `compatible_runtimes`, `license_info`, `compatible_architectures`, `has_python_runtime`, `has_nodejs_runtime`, `supports_arm64`, `supports_x86_64`, `core_data`.
- `LayerVersion`: same fields as above plus `layer_arn`, `layer_name` (parsed from ARN), `content -> LayerContent | None`, `created_datetime -> datetime` (tz aware, UTC if none), `has_content_details`, `has_java_runtime`, `has_dotnet_runtime`, `has_go_runtime`, `has_ruby_runtime`, `has_provided_runtime`, `supports_multi_arch`, `runtime_count`, `architecture_count`.
- `LayerContent`: `location`, `code_sha256`, `code_size`, `signing_profile_version_arn`, `signing_job_arn`, `core_data`.
- `LayerIterproxy`, `LayerVersionIterproxy`: lazy iterators (iterproxy). `.all() -> list`, `.one()` (raises `StopIteration` if empty), `.one_or_none()`, `.many(k)`, `.skip(k)`, `.filter(func)`, `.iter_chunks(k)`, or plain `for`.

`content` is only filled by `get_layer_version`; list results have `content is None`. `core_data` is a short dict for logging.

## Common tasks

```python
import boto3
import simple_aws_lambda.api as sal

lambda_client = boto3.Session(region_name="us-east-1").client("lambda")

latest = sal.get_latest_layer_version(lambda_client=lambda_client, layer_name="my_layer")
if latest is not None:
    print(latest.version, latest.layer_version_arn)

versions = sal.list_layer_versions(lambda_client=lambda_client, layer_name="my_layer").all()

# preview, then delete
sal.cleanup_old_layer_versions(lambda_client=lambda_client, layer_name="my_layer", keep_last_n_versions=3)
sal.cleanup_old_layer_versions(lambda_client=lambda_client, layer_name="my_layer", keep_last_n_versions=3, real_run=True)

sal.grant_aws_account_or_aws_organization_lambda_layer_version_access(
    lambda_client=lambda_client, layer_name="my_layer", version_number=latest.version, principal="111122223333",
)
```

Testing: works with `moto.mock_aws()`; no AWS account needed.

## More detail

For full API docs see `ref/public-api.md`.
