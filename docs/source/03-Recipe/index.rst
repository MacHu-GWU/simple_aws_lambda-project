Recipe
==============================================================================
Recipes provide commonly used high-level operations for working with AWS Lambda services. These functions combine multiple client calls and implement best practices for complex Lambda layer management tasks.

Below are the full list of available recipe functions:

**Layer Version Management:**

- :func:`~simple_aws_lambda.recipe.get_latest_layer_version`: Get the latest deployed layer version with compatibility filtering support
- :func:`~simple_aws_lambda.recipe.cleanup_old_layer_versions`: Delete old layer versions based on retention policy (keep last N versions or versions newer than N seconds)

**Cross-Account Access Management:**

- :func:`~simple_aws_lambda.recipe.grant_aws_account_or_aws_organization_lambda_layer_version_access`: Grant other AWS accounts Lambda layer access to a specific layer version
- :func:`~simple_aws_lambda.recipe.revoke_aws_account_or_aws_organization_lambda_layer_version_access`: Revoke AWS accounts Lambda layer access from a specific layer version

**Utility Functions:**

- :func:`~simple_aws_lambda.recipe.identify_principal_type`: Identify the type of principal (public, AWS account, or AWS organization)
- :func:`~simple_aws_lambda.recipe.get_layer_permission_statement_id`: Generate statement ID for layer permissions