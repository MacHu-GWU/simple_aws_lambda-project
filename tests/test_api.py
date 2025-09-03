# -*- coding: utf-8 -*-

from simple_aws_lambda import api


def test():
    _ = api
    _ = api.LatestMatchingLayerVersion
    _ = api.Layer
    _ = api.LayerIterproxy
    _ = api.LayerContent
    _ = api.LayerVersion
    _ = api.LayerVersionIterproxy
    _ = api.list_layers
    _ = api.list_layer_versions
    _ = api.get_layer_version
    _ = api.get_latest_layer_version
    _ = api.cleanup_old_layer_versions
    _ = api.grant_aws_account_or_aws_organization_lambda_layer_version_access
    _ = api.revoke_aws_account_or_aws_organization_lambda_layer_version_access


if __name__ == "__main__":
    from simple_aws_lambda.tests import run_cov_test

    run_cov_test(
        __file__,
        "simple_aws_lambda.api",
        preview=False,
    )
