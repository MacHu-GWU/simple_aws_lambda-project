Data Model
==============================================================================
Data models convert boto3 client responses to Pythonic object interfaces that provide stable, property-based access to AWS Lambda resources. These models follow the Raw Data Storage, Property-Based Access, and Core Data Extraction patterns to ensure resilience against API changes while maintaining clean interfaces.

Below are the full list of available data models:

**Base Classes:**

- :class:`~simple_aws_lambda.model.Base`: Base class for all data models providing common functionality

**Layer Models:**

- :class:`~simple_aws_lambda.model.Layer`: Represents a Lambda layer with its metadata and latest version information
- :class:`~simple_aws_lambda.model.LayerVersion`: Represents a specific version of a Lambda layer with detailed version information
- :class:`~simple_aws_lambda.model.LayerContent`: Represents the content information of a layer version including location and code SHA

**Helper Models:**

- :class:`~simple_aws_lambda.model.LatestMatchingLayerVersion`: Represents the latest layer version matching specific criteria

**Iterator Proxies:**

- :class:`~simple_aws_lambda.model.LayerIterproxy`: Iterator proxy for collections of Layer objects with enhanced iteration capabilities
- :class:`~simple_aws_lambda.model.LayerVersionIterproxy`: Iterator proxy for collections of LayerVersion objects with enhanced iteration capabilities