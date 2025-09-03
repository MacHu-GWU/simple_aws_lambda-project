# -*- coding: utf-8 -*-

from simple_aws_lambda.recipe import (
    get_latest_layer_version,
    cleanup_old_layer_versions,
)
from simple_aws_lambda.client import (
    list_layer_versions,
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
            _sort_descending=True,
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
        print("**********")
        latest_layer = get_latest_layer_version(
            lambda_client=lambda_client,
            layer_name=layer_name,
            _sort_descending=True,
        )
        assert latest_layer is not None
        assert latest_layer.version == 2

    def test_cleanup_old_layer_versions(self):
        lambda_client = self.bsm.lambda_client
        layer_name = "cleanup_old_layer_versions"

        # Test cleanup with non-existent layer
        deleted_versions = cleanup_old_layer_versions(
            lambda_client=lambda_client,
            layer_name=layer_name,
            real_run=True,
        )
        assert deleted_versions == []

        # Create multiple layer versions
        for i in range(1, 8):  # Create versions 1-7
            lambda_client.publish_layer_version(
                LayerName=layer_name,
                Content={
                    "ZipFile": f"version{i}".encode(),
                },
            )

        # Test simulation mode - should identify versions to delete but not actually delete
        deleted_versions = cleanup_old_layer_versions(
            lambda_client=lambda_client,
            layer_name=layer_name,
            keep_last_n_versions=3,
            keep_versions_newer_than_seconds=0,  # Don't keep any based on date
            real_run=False,
            _sort_descending=True,
        )
        # Should identify versions 1-4 for deletion (keeping last 3: versions 5,6,7)
        assert deleted_versions == [4, 3, 2, 1]

        # Verify no versions were actually deleted in simulation mode
        all_versions = list_layer_versions(
            lambda_client=lambda_client,
            layer_name=layer_name,
        ).all()
        assert len(all_versions) == 7

        # Test actual deletion - keep last 2 versions
        deleted_versions = cleanup_old_layer_versions(
            lambda_client=lambda_client,
            layer_name=layer_name,
            keep_last_n_versions=2,
            keep_versions_newer_than_seconds=0,  # Don't keep any based on date
            real_run=True,
            _sort_descending=True,
        )
        # Should delete versions 1-5 (keeping last 2: versions 6,7)
        assert deleted_versions == [5, 4, 3, 2, 1]

        # Verify versions were actually deleted
        remaining_versions = list_layer_versions(
            lambda_client=lambda_client,
            layer_name=layer_name,
            _sort_descending=True,
        ).all()
        assert len(remaining_versions) == 2
        remaining_version_numbers = [v.version for v in remaining_versions]
        assert remaining_version_numbers == [7, 6]


if __name__ == "__main__":
    from simple_aws_lambda.tests import run_cov_test

    run_cov_test(
        __file__,
        "simple_aws_lambda.recipe",
        preview=False,
    )
