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

        layer = get_layer_version(
            lambda_client=lambda_client,
            layer_name=layer_name,
            version_number=1,
        )
        assert layer is None

        res = lambda_client.publish_layer_version(
            LayerName=layer_name,
            Content={
                "ZipFile": b"123",
            },
            CompatibleRuntimes=[py_ver],
        )
        layer_version = LayerVersion(_data=res)
        assert layer_version.version == 1


if __name__ == "__main__":
    from simple_aws_lambda.tests import run_cov_test

    run_cov_test(
        __file__,
        "simple_aws_lambda.client",
        preview=False,
    )
