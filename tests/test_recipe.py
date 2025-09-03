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
        layer_name = "recipe_get_latest_layer_version"


if __name__ == "__main__":
    from simple_aws_lambda.tests import run_cov_test

    run_cov_test(
        __file__,
        "simple_aws_lambda.recipe",
        preview=False,
    )
