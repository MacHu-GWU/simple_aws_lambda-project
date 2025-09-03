.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.2.1 (2025-09-03)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add ``simple_aws_lambda.api.get_latest_layer_version`` - Get the latest deployed layer version
- Add ``simple_aws_lambda.api.cleanup_old_layer_versions`` - Delete old layer versions based on retention policy (keep last N versions or versions newer than N seconds)
- Add ``simple_aws_lambda.api.grant_aws_account_or_aws_organization_lambda_layer_version_access`` - Grant other AWS accounts Lambda layer access
- Add ``simple_aws_lambda.api.revoke_aws_account_or_aws_organization_lambda_layer_version_access`` - Revoke AWS accounts Lambda layer access

**Minor Improvements**

- Improve layer version sorting and cleanup logic in recipe module


0.1.1 (2025-08-23)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- First release
- Add the following public APIs:
    - ``simple_aws_lambda.api.LatestMatchingLayerVersion``
    - ``simple_aws_lambda.api.Layer``
    - ``simple_aws_lambda.api.LayerIterproxy``
    - ``simple_aws_lambda.api.LayerContent``
    - ``simple_aws_lambda.api.LayerVersion``
    - ``simple_aws_lambda.api.LayerVersionIterproxy``
    - ``simple_aws_lambda.api.list_layers``
    - ``simple_aws_lambda.api.list_layer_versions``
    - ``simple_aws_lambda.api.get_layer_version``
