# -*- coding: utf-8 -*-

from simple_aws_lambda.client import (
    list_layers,
    list_layer_versions,
    get_layer_version,
)

import sys
from simple_aws_lambda.model import (
    Layer,
    LayerVersion,
)
from simple_aws_lambda.tests.mock_aws import BaseMockAwsTest

py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"


class Test(BaseMockAwsTest):
    use_mock = True

    def test_layer(self):
        lambda_client = self.bsm.lambda_client
        layer_name = "my_app"

        # Test get_layer_version with non-existent layer
        layer_version = get_layer_version(
            lambda_client=lambda_client,
            layer_name=layer_name,
            version_number=1,
        )
        assert layer_version is None

        # Test list_layers when empty
        layers = list_layers(lambda_client=lambda_client)
        layer_list = list(layers)
        assert len(layer_list) == 0

        # Test list_layer_versions when empty
        layer_versions = list_layer_versions(
            lambda_client=lambda_client,
            layer_name=layer_name,
        )
        layer_version_list = list(layer_versions)
        assert len(layer_version_list) == 0

        # Create first layer version
        res = lambda_client.publish_layer_version(
            LayerName=layer_name,
            Content={
                "ZipFile": b"123",
            },
            CompatibleRuntimes=[py_ver],
        )
        layer_version = LayerVersion(_data=res)
        assert layer_version.version == 1

        # Test get_layer_version with existing layer
        layer_version = get_layer_version(
            lambda_client=lambda_client,
            layer_name=layer_name,
            version_number=1,
        )
        assert layer_version is not None
        assert layer_version.version == 1

        # Test list_layers with one layer
        layers = list_layers(lambda_client=lambda_client)
        layer_list = list(layers)
        assert len(layer_list) == 1
        assert layer_list[0].layer_name == layer_name

        # Test list_layer_versions with one version
        layer_versions = list_layer_versions(
            lambda_client=lambda_client,
            layer_name=layer_name,
        )
        layer_version_list = list(layer_versions)
        assert len(layer_version_list) == 1
        assert layer_version_list[0].version == 1

        # Create second layer version
        res2 = lambda_client.publish_layer_version(
            LayerName=layer_name,
            Content={
                "ZipFile": b"456",
            },
            CompatibleRuntimes=[py_ver],
        )
        layer_version2 = LayerVersion(_data=res2)
        assert layer_version2.version == 2

        # Test get_layer_version with second version
        layer_version2 = get_layer_version(
            lambda_client=lambda_client,
            layer_name=layer_name,
            version_number=2,
        )
        assert layer_version2 is not None
        assert layer_version2.version == 2

        # Test list_layer_versions with two versions
        layer_versions = list_layer_versions(
            lambda_client=lambda_client,
            layer_name=layer_name,
        )
        layer_version_list = list(layer_versions)
        assert len(layer_version_list) == 2

        # Test list_layers still shows one layer
        layers = list_layers(lambda_client=lambda_client)
        layer_list = list(layers)
        assert len(layer_list) == 1

        # Test max_items parameter for list_layers
        layers_limited = list_layers(lambda_client=lambda_client, max_items=1)
        layer_list_limited = list(layers_limited)
        assert len(layer_list_limited) == 1

        # Test max_items parameter for list_layer_versions
        layer_versions_limited = list_layer_versions(
            lambda_client=lambda_client,
            layer_name=layer_name,
            max_items=1,
        )
        layer_version_list_limited = list(layer_versions_limited)
        assert len(layer_version_list_limited) == 1


if __name__ == "__main__":
    from simple_aws_lambda.tests import run_cov_test

    run_cov_test(
        __file__,
        "simple_aws_lambda.client",
        preview=False,
    )
