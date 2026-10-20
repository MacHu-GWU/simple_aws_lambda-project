# simple_aws_lambda public API reference (v0.3.1)

All names import from `simple_aws_lambda.api`. Every function takes a boto3 Lambda client as `lambda_client` (type `mypy_boto3_lambda.client.LambdaClient`); create it yourself:

```python
import boto3
import simple_aws_lambda.api as sal

lambda_client = boto3.Session(region_name="us-east-1").client("lambda")
```

Arguments defaulting to `OPT` (from `func_args`) are left out of the AWS request when you omit them. Pass all arguments by keyword.

---

## Client functions

### `list_layers`

```python
list_layers(
    lambda_client: LambdaClient,
    compatible_runtime: str = OPT,
    compatible_architecture: str = OPT,
    max_items: int = 9999,
    page_size: int = 50,
) -> LayerIterproxy
```

Lists the layers of the account in the client's region, via the `list_layers` paginator. Each item is a `Layer` whose `latest_matching_version` is the newest version matching the runtime/architecture filters. `max_items` caps the total read; `page_size` is the AWS page size. Lazy: no API call until you iterate.

```python
layers = sal.list_layers(lambda_client=lambda_client).all()
layers[0].layer_name
layers[0].latest_matching_version.version
```

### `list_layer_versions`

```python
list_layer_versions(
    lambda_client: LambdaClient,
    layer_name: str,
    compatible_runtime: str = OPT,
    compatible_architecture: str = OPT,
    max_items: int = 9999,
    page_size: int = 50,
) -> LayerVersionIterproxy
```

Lists the versions of one layer as `LayerVersion` objects, newest first (AWS order). An unknown layer yields nothing (no error). Items have no `content` (use `get_layer_version` for that).

```python
versions = sal.list_layer_versions(
    lambda_client=lambda_client,
    layer_name="my_layer",
    compatible_runtime="python3.12",
    max_items=2,
).all()
[v.version for v in versions]  # e.g. [3, 2]
```

### `get_layer_version`

```python
get_layer_version(
    lambda_client: LambdaClient,
    layer_name: str,
    version_number: int,
) -> LayerVersion | None
```

Fetches one version, including `content` (`LayerContent`). Returns `None` on `ResourceNotFoundException`; any other `ClientError` is raised.

```python
lv = sal.get_layer_version(lambda_client=lambda_client, layer_name="my_layer", version_number=2)
if lv is None:
    ...
lv.content.code_sha256
```

---

## Recipes

### `get_latest_layer_version`

```python
get_latest_layer_version(
    lambda_client: LambdaClient,
    layer_name: str,
    compatible_runtime: str = OPT,
    compatible_architecture: str = OPT,
) -> LayerVersion | None
```

The newest version of the layer (optionally among those matching the filters), or `None` if the layer has no version. Typical use in deploy scripts: "what version did I publish last?". The result comes from `list_layer_versions`, so `content` is `None`.

```python
latest = sal.get_latest_layer_version(lambda_client=lambda_client, layer_name="my_layer")
latest.version if latest else None
```

### `cleanup_old_layer_versions`

```python
cleanup_old_layer_versions(
    lambda_client: LambdaClient,
    layer_name: str,
    keep_last_n_versions: int = 5,
    keep_versions_newer_than_seconds: int = 90 * 24 * 60 * 60,
    real_run: bool = False,
) -> list[int]
```

Retention policy. A version is **kept** if ANY holds:

- it is among the newest `keep_last_n_versions` versions, or
- it was created less than `keep_versions_newer_than_seconds` ago.

All others are deleted. Returns the version numbers deleted (or that would be, when `real_run=False`), newest first. Unknown layer or nothing to delete returns `[]`.

Gotchas:

- `real_run=False` is the default: nothing is deleted until you pass `real_run=True`.
- With the default 90 day age rule, freshly published versions are always kept. Pass `keep_versions_newer_than_seconds=0` to retain by count only.
- A `ClientError` on one delete is swallowed and the rest continue; the failed number is still in the returned list.
- Deletion is permanent. Functions already using a deleted version keep working, but it can no longer be attached to functions.
- Safe to run after every deployment: a second run deletes nothing new.

```python
# 7 versions exist, all just created
sal.cleanup_old_layer_versions(lambda_client=lambda_client, layer_name="my_layer", keep_last_n_versions=3)
# -> []  (age rule keeps them)
sal.cleanup_old_layer_versions(
    lambda_client=lambda_client,
    layer_name="my_layer",
    keep_last_n_versions=3,
    keep_versions_newer_than_seconds=0,
    real_run=True,
)
# -> [4, 3, 2, 1]; versions 7, 6, 5 remain
```

### `grant_aws_account_or_aws_organization_lambda_layer_version_access`

```python
grant_aws_account_or_aws_organization_lambda_layer_version_access(
    lambda_client: LambdaClient,
    layer_name: str,
    version_number: int,
    principal: str,
) -> None
```

Adds a `lambda:GetLayerVersion` statement to the layer version policy so another account can use the layer. `principal`:

| Value | Meaning | Statement written | Statement id |
| :--- | :--- | :--- | :--- |
| `"111122223333"` (12 digits) | one AWS account | `Principal=<account>` | `allow-111122223333-GetLayerVersion` |
| `"o-1a2b3c"` | every account in an AWS organization | `Principal="*"`, `OrganizationId=<org>` | `allow-o-1a2b3c-GetLayerVersion` |
| `"*"` | public, every AWS account | `Principal="*"` | `allow-public-GetLayerVersion` |

Any other format raises `ValueError`. Idempotent: the statement id is deterministic, and the `ResourceConflictException` from a repeated grant is ignored. Only `GetLayerVersion` is granted (that is what a function in another account needs). Grants are per version: grant again after publishing a new version.

```python
sal.grant_aws_account_or_aws_organization_lambda_layer_version_access(
    lambda_client=lambda_client,
    layer_name="my_layer",
    version_number=3,
    principal="o-1a2b3c",
)
```

### `revoke_aws_account_or_aws_organization_lambda_layer_version_access`

```python
revoke_aws_account_or_aws_organization_lambda_layer_version_access(
    lambda_client: LambdaClient,
    layer_name: str,
    version_number: int,
    principal: str,
) -> None
```

Removes the statement that the grant above created for the same `principal`. Idempotent: `ResourceNotFoundException` (no such statement) is ignored. When the last statement is removed, AWS deletes the policy, so `get_layer_version_policy` then raises `ResourceNotFoundException`.

```python
sal.revoke_aws_account_or_aws_organization_lambda_layer_version_access(
    lambda_client=lambda_client,
    layer_name="my_layer",
    version_number=3,
    principal="111122223333",
)
```

---

## Models

All are `@dataclasses.dataclass(frozen=True)` with one field, `_data`, the raw boto3 dict. Construct them yourself only to wrap a response you got from boto3 directly, e.g. `LayerVersion(_data=lambda_client.publish_layer_version(...))`. Required keys are read with `_data["Key"]` (a missing one raises `KeyError`), optional ones with `.get()` (missing gives `None`). Fields the library has no property for are still in `_data`.

Every model has `core_data -> dict`, a short dict of its essential fields for logging.

### `Layer`

From `list_layers`.

| Property | Type | Note |
| :--- | :--- | :--- |
| `layer_name` | `str` | |
| `layer_arn` | `str` | ARN without version |
| `latest_matching_version` | `LatestMatchingLayerVersion \| None` | |
| `has_latest_version` | `bool` | |
| `core_data` | `dict` | `layer_name`, `layer_arn` |

### `LatestMatchingLayerVersion`

The `LatestMatchingVersion` part of a `Layer`.

| Property | Type |
| :--- | :--- |
| `layer_version_arn` | `str` |
| `version` | `int` |
| `description` | `str \| None` |
| `created_date` | `str \| None` (ISO 8601, e.g. `2026-10-20T17:53:56.552+0000`) |
| `compatible_runtimes` | `list[str] \| None` |
| `license_info` | `str \| None` |
| `compatible_architectures` | `list[str] \| None` |
| `has_python_runtime`, `has_nodejs_runtime` | `bool` |
| `supports_arm64`, `supports_x86_64` | `bool` |
| `core_data` | `dict` |

### `LayerVersion`

From `list_layer_versions`, `get_layer_version`, `get_latest_layer_version`, or `publish_layer_version` responses.

| Property | Type | Note |
| :--- | :--- | :--- |
| `layer_version_arn` | `str` | |
| `version` | `int` | |
| `description`, `created_date`, `license_info` | `str \| None` | |
| `compatible_runtimes`, `compatible_architectures` | `list[str] \| None` | |
| `layer_arn` | `str \| None` | only from `get_layer_version` |
| `layer_name` | `str` | parsed from `layer_version_arn` |
| `content` | `LayerContent \| None` | only from `get_layer_version` |
| `has_content_details` | `bool` | `content is not None` |
| `created_datetime` | `datetime` | tz aware; UTC assumed if none. Fails if `created_date` is missing |
| `has_python_runtime`, `has_nodejs_runtime`, `has_java_runtime`, `has_dotnet_runtime`, `has_go_runtime`, `has_ruby_runtime`, `has_provided_runtime` | `bool` | prefix match on runtime names |
| `supports_arm64`, `supports_x86_64`, `supports_multi_arch` | `bool` | |
| `runtime_count`, `architecture_count` | `int` | 0 when absent |
| `core_data` | `dict` | arn, layer_arn, version, description, created_date, runtimes, architectures |

```python
lv = sal.get_layer_version(lambda_client=lambda_client, layer_name="my_layer", version_number=1)
lv.layer_name            # "my_layer"
lv.created_datetime      # datetime(..., tzinfo=timezone.utc)
lv.has_python_runtime    # True
lv._data["LicenseInfo"]  # raw access
```

### `LayerContent`

`LayerVersion.content`.

| Property | Type |
| :--- | :--- |
| `location` | `str \| None` (S3 URL, valid 10 minutes) |
| `code_sha256` | `str \| None` |
| `code_size` | `int \| None` (bytes) |
| `signing_profile_version_arn`, `signing_job_arn` | `str \| None` |
| `core_data` | `dict` (location, code_sha256, code_size) |

### `LayerIterproxy`, `LayerVersionIterproxy`

`iterproxy.IterProxy[Layer]` / `IterProxy[LayerVersion]`. Pages are fetched as you iterate, so stopping early stops API calls.

| Method | Returns | Note |
| :--- | :--- | :--- |
| `all()` | `list` | remaining items |
| `one()` | item | raises `StopIteration` if empty |
| `one_or_none()` | item or `None` | |
| `many(k)` | `list` | next k items |
| `skip(k)` | the proxy | skip next k |
| `filter(*funcs)` | the proxy | keep items where every func returns true |
| `iter_chunks(k)` | iterator of lists | |

The iterator is single use: once consumed, call the function again.

---

## Testing with moto

```python
import boto3
import moto

with moto.mock_aws():
    lambda_client = boto3.Session(region_name="us-east-1").client("lambda")
    lambda_client.publish_layer_version(LayerName="my_layer", Content={"ZipFile": b"x"})
    assert sal.get_latest_layer_version(lambda_client=lambda_client, layer_name="my_layer").version == 1
```

moto differs from AWS in one place: a repeated grant with the same statement id adds a duplicate statement instead of raising `ResourceConflictException`.
