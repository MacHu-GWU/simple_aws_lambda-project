# -*- coding: utf-8 -*-

from simple_aws_lambda.recipe import (
    get_latest_layer_version,
    cleanup_old_layer_versions,
)

import sys
from simple_aws_lambda.tests.mock_aws import BaseMockAwsTest

py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"


class Test(BaseMockAwsTest):
    use_mock = True

    def test_get_latest_layer_version(self):
        lambda_client = self.bsm.lambda_client
        layer_name = "recipe_get_latest_layer_version"

        # Test get_latest_layer_version with non-existent layer
        latest_layer = get_latest_layer_version(
            lambda_client=lambda_client,
            layer_name=layer_name,
        )
        assert latest_layer is None

        # Create first layer version
        res1 = lambda_client.publish_layer_version(
            LayerName=layer_name,
            Content={
                "ZipFile": b"version1",
            },
        )

        # # Test get_latest_layer_version with one version
        latest_layer = get_latest_layer_version(
            lambda_client=lambda_client,
            layer_name=layer_name,
        )
        assert latest_layer is not None
        assert latest_layer.version == 1
        assert latest_layer.layer_name == layer_name

        # Create second layer version
        res2 = lambda_client.publish_layer_version(
            LayerName=layer_name,
            Content={
                "ZipFile": b"version2",
            },
        )

        # Test get_latest_layer_version returns latest version
        latest_layer = get_latest_layer_version(
            lambda_client=lambda_client,
            layer_name=layer_name,
        )
        assert latest_layer is not None
        assert latest_layer.version == 2

    def test_cleanup_old_layer_versions(self):
        lambda_client = self.bsm.lambda_client
        layer_name = "cleanup_old_layer_versions"



if __name__ == "__main__":
    from simple_aws_lambda.tests import run_cov_test

    run_cov_test(
        __file__,
        "simple_aws_lambda.recipe",
        preview=False,
    )
