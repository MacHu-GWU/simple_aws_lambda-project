# -*- coding: utf-8 -*-

import pytest

from simple_aws_lambda.model import (
    Base,
    LatestMatchingLayerVersion,
    Layer,
    LayerContent,
    LayerVersion,
)


class TestBase:
    def test(self):
        obj = Base(_data={})
        with pytest.raises(NotImplementedError):
            _ = obj.core_data


class TestLatestMatchingLayerVersion:
    def test(self):
        obj = LatestMatchingLayerVersion(
            _data={
                "LayerVersionArn": "arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1",
                "Version": 1,
                "Description": "My test layer",
                "CreatedDate": "2023-01-01T00:00:00.000Z",
                "CompatibleRuntimes": ["python3.9", "nodejs18.x"],
                "LicenseInfo": "MIT",
                "CompatibleArchitectures": ["x86_64", "arm64"],
            }
        )
        assert (
            obj.layer_version_arn
            == "arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1"
        )
        assert obj.version == 1
        _ = obj.description
        _ = obj.created_date
        _ = obj.compatible_runtimes
        _ = obj.license_info
        _ = obj.compatible_architectures
        _ = obj.has_python_runtime
        _ = obj.has_nodejs_runtime
        _ = obj.supports_arm64
        _ = obj.supports_x86_64
        _ = obj.core_data

        # Test with empty runtimes/architectures to cover false branches
        obj_empty = LatestMatchingLayerVersion(
            _data={
                "LayerVersionArn": "arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1",
                "Version": 1,
            }
        )
        _ = obj_empty.has_python_runtime
        _ = obj_empty.has_nodejs_runtime
        _ = obj_empty.supports_arm64
        _ = obj_empty.supports_x86_64


class TestLayer:
    def test(self):
        obj = Layer(
            _data={
                "LayerName": "my-layer",
                "LayerArn": "arn:aws:lambda:us-east-1:123456789012:layer:my-layer",
                "LatestMatchingVersion": {
                    "LayerVersionArn": "arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1",
                    "Version": 1,
                },
            }
        )
        assert obj.layer_name == "my-layer"
        assert obj.layer_arn == "arn:aws:lambda:us-east-1:123456789012:layer:my-layer"
        _ = obj.latest_matching_version
        _ = obj.has_latest_version
        _ = obj.core_data

        # Test without latest version to cover None branch
        obj_no_version = Layer(
            _data={
                "LayerName": "my-layer",
                "LayerArn": "arn:aws:lambda:us-east-1:123456789012:layer:my-layer",
            }
        )
        _ = obj_no_version.latest_matching_version
        _ = obj_no_version.has_latest_version


class TestLayerContent:
    def test(self):
        obj = LayerContent(
            _data={
                "Location": "https://s3.amazonaws.com/bucket/layer.zip",
                "CodeSha256": "abc123",
                "CodeSize": 1024,
                "SigningProfileVersionArn": "arn:aws:signer:us-east-1:123456789012:signing-profile/test",
                "SigningJobArn": "arn:aws:signer:us-east-1:123456789012:signing-job/test",
            }
        )
        _ = obj.location
        _ = obj.code_sha256
        _ = obj.code_size
        _ = obj.signing_profile_version_arn
        _ = obj.signing_job_arn
        _ = obj.core_data


class TestLayerVersion:
    def test(self):
        obj = LayerVersion(
            _data={
                "LayerVersionArn": "arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1",
                "LayerArn": "arn:aws:lambda:us-east-1:123456789012:layer:my-layer",
                "Version": 1,
                "Description": "My test layer",
                "CreatedDate": "2023-01-01T00:00:00.000Z",
                "CompatibleRuntimes": [
                    "python3.9",
                    "nodejs18.x",
                    "java17",
                    "dotnet6",
                    "go1.x",
                    "ruby3.2",
                    "provided.al2",
                ],
                "LicenseInfo": "MIT",
                "CompatibleArchitectures": ["x86_64", "arm64"],
                "Content": {
                    "Location": "https://s3.amazonaws.com/bucket/layer.zip",
                    "CodeSha256": "abc123",
                    "CodeSize": 1024,
                },
            }
        )
        assert (
            obj.layer_version_arn
            == "arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1"
        )
        assert obj.version == 1
        _ = obj.description
        _ = obj.created_date
        _ = obj.compatible_runtimes
        _ = obj.license_info
        _ = obj.compatible_architectures
        _ = obj.layer_arn
        _ = obj.content
        _ = obj.has_content_details
        _ = obj.has_python_runtime
        _ = obj.has_nodejs_runtime
        _ = obj.has_java_runtime
        _ = obj.has_dotnet_runtime
        _ = obj.has_go_runtime
        _ = obj.has_ruby_runtime
        _ = obj.has_provided_runtime
        _ = obj.supports_arm64
        _ = obj.supports_x86_64
        _ = obj.supports_multi_arch
        _ = obj.runtime_count
        _ = obj.architecture_count
        _ = obj.core_data

        # Test with no content and empty runtimes to cover false branches
        obj_empty = LayerVersion(
            _data={
                "LayerVersionArn": "arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1",
                "Version": 1,
            }
        )
        assert obj_empty.layer_name == "my-layer"
        _ = obj_empty.content
        _ = obj_empty.has_content_details
        _ = obj_empty.has_python_runtime
        _ = obj_empty.has_nodejs_runtime
        _ = obj_empty.has_java_runtime
        _ = obj_empty.has_dotnet_runtime
        _ = obj_empty.has_go_runtime
        _ = obj_empty.has_ruby_runtime
        _ = obj_empty.has_provided_runtime
        _ = obj_empty.supports_arm64
        _ = obj_empty.supports_x86_64


if __name__ == "__main__":
    from simple_aws_lambda.tests import run_cov_test

    run_cov_test(
        __file__,
        "simple_aws_lambda.model",
        preview=False,
    )
