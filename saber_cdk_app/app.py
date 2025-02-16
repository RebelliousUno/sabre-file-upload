"""Python FastAPI script"""

from aws_cdk import (aws_lambda as _lambda, Stack, BundlingOptions, aws_apigateway as apigw, aws_dynamodb as dynamodb,
                     aws_s3 as s3, Duration)
from constructs import Construct


class SaberCdkAppStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        url_table = dynamodb.Table(
            self,
            "saber-url-shortener",
            partition_key=dynamodb.Attribute(
                name="user_id", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="url", type=dynamodb.AttributeType.STRING
            ),
        )

        s3_bucket = s3.Bucket(
            self,
            "saber-file-upload",
            bucket_name="saber-tech-test-file-upload",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS
        )

        api_function = _lambda.Function(
            self,
            "ApiFunction",
            code=_lambda.Code.from_asset(
                "api",
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_11.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        (
                            "pip install --no-deps --platform manylinux2014_x86_64 -r requirements.txt -t"
                            "/asset-output && cp -au . /asset-output"
                        ),
                    ],
                ),
            ),
            handler="main.handler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            timeout=Duration.seconds(60),
            memory_size=512,
            # Increase from default for file upload - could split into 2 lambda if this is a problem down the line
            environment={"DYNAMODB_TABLE_NAME": url_table.table_name, "S3_BUCKET_NAME": s3_bucket.bucket_name},
        )

        apigw.LambdaRestApi(
            self,
            "ApiGatewayEndpoint",
            handler=api_function,  # type: ignore
            default_cors_preflight_options={
                "allow_origins": apigw.Cors.ALL_ORIGINS,
                "allow_methods": apigw.Cors.ALL_METHODS,
                "allow_headers": ["*"]
            },
            binary_media_types=["image/jpeg", "image/png", "application/pdf", "application/octet-stream", "multipart/form-data"]
        )

        s3_bucket.grant_read_write(api_function)
        url_table.grant_read_write_data(api_function)
