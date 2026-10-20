# -*- coding: utf-8 -*-

"""
Base class for tests that call AWS through `moto <https://docs.getmoto.org/>`_.

With ``use_mock = True`` (the default) every AWS call goes to moto's in-memory
backend, so no real AWS account or credentials are needed.
"""

import typing as T
import dataclasses

import boto3
import moto

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_lambda.client import LambdaClient


@dataclasses.dataclass(frozen=True)
class MockAwsTestConfig:
    # fmt: off
    use_mock: bool = dataclasses.field()
    aws_region: str = dataclasses.field()
    aws_profile: str | None = dataclasses.field(default=None)
    # fmt: on


class BaseMockAwsTest:
    use_mock: bool = True

    @classmethod
    def setup_mock(cls, mock_aws_test_config: MockAwsTestConfig):
        cls.mock_aws_test_config = mock_aws_test_config
        if mock_aws_test_config.use_mock:
            cls.mock_aws = moto.mock_aws()
            cls.mock_aws.start()
            cls.boto_ses = boto3.Session(
                region_name=mock_aws_test_config.aws_region,
            )
        else:  # pragma: no cover
            cls.boto_ses = boto3.Session(
                profile_name=mock_aws_test_config.aws_profile,
                region_name=mock_aws_test_config.aws_region,
            )
        cls.lambda_client: "LambdaClient" = cls.boto_ses.client("lambda")

    @classmethod
    def setup_class_post_hook(cls):
        pass

    @classmethod
    def setup_class(cls):
        mock_aws_test_config = MockAwsTestConfig(
            use_mock=cls.use_mock,
            aws_region="us-east-1",
            aws_profile="bmt_app_dev_us_east_1",  # only used when use_mock is False
        )
        cls.setup_mock(mock_aws_test_config)
        cls.setup_class_post_hook()

    @classmethod
    def teardown_class(cls):
        if cls.mock_aws_test_config.use_mock:
            cls.mock_aws.stop()
