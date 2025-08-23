# -*- coding: utf-8 -*-

import typing as T
import dataclasses

import moto
import boto3
import botocore.exceptions
from s3pathlib import S3Path, context
from boto_session_manager import BotoSesManager

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client


@dataclasses.dataclass(frozen=True)
class MockAwsTestConfig:
    use_mock: bool = dataclasses.field()
    aws_region: str = dataclasses.field()
    aws_profile: T.Optional[str] = dataclasses.field(default=None)


class BaseMockAwsTest:
    use_mock: bool = True

    @classmethod
    def create_s3_bucket(cls, bucket_name: str, enable_versioning: bool = False):
        try:
            cls.s3_client.create_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "BucketAlreadyExists":
                pass
            else:
                raise e

        if enable_versioning:
            cls.bsm.s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={"Status": "Enabled"},
            )

    @classmethod
    def setup_mock(cls, mock_aws_test_config: MockAwsTestConfig):
        cls.mock_aws_test_config = mock_aws_test_config
        if mock_aws_test_config.use_mock:
            cls.mock_aws = moto.mock_aws()
            cls.mock_aws.start()

        if mock_aws_test_config.use_mock:
            cls.bsm: "BotoSesManager" = BotoSesManager(
                region_name=mock_aws_test_config.aws_region
            )
        else:
            cls.bsm: "BotoSesManager" = BotoSesManager(
                profile_name=mock_aws_test_config.aws_profile,
                region_name=mock_aws_test_config.aws_region,
            )

        cls.boto_ses: "boto3.Session" = cls.bsm.boto_ses
        context.attach_boto_session(cls.boto_ses)
        cls.s3_client: "S3Client" = cls.boto_ses.client("s3")

    @classmethod
    def setup_class_post_hook(cls):
        pass

    @classmethod
    def setup_class(cls):
        mock_aws_test_config = MockAwsTestConfig(
            use_mock=cls.use_mock,
            aws_region="us-east-1",
            aws_profile="bmt_app_dev_us_east_1",  # Use default profile
        )
        cls.setup_mock(mock_aws_test_config)
        cls.setup_class_post_hook()

    @classmethod
    def teardown_class(cls):
        if cls.mock_aws_test_config.use_mock:
            cls.mock_aws.stop()
