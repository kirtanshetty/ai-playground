"""
CDKTF stack for TQ Lambda function.
"""

import os
import hashlib
import base64
from cdktf import TerraformStack, TerraformOutput, S3Backend, DataTerraformRemoteStateS3
from constructs import Construct
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.data_aws_secretsmanager_secret import DataAwsSecretsmanagerSecret
from cdktf_cdktf_provider_aws.data_aws_secretsmanager_secret_version import DataAwsSecretsmanagerSecretVersion
from cdktf_cdktf_provider_aws.data_aws_security_group import DataAwsSecurityGroup
from cdktf_cdktf_provider_aws.iam_role import IamRole
from cdktf_cdktf_provider_aws.iam_role_policy import IamRolePolicy
from cdktf_cdktf_provider_aws.lambda_function import LambdaFunction
from cdktf_cdktf_provider_aws.lambda_function_url import LambdaFunctionUrl


class TQLambdaStack(TerraformStack):
    """Stack that defines the TQ Lambda function infrastructure."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id)

        # Configure AWS provider
        region = os.getenv("CDKTF_DEFAULT_REGION", "us-east-1")
        AwsProvider(self, "aws", region=region)

        # Configure S3 backend for Terraform state
        S3Backend(
            self,
            bucket="ai-playground-tf-state",
            key="twenty-one-questions/infra/terraform.tfstate",
            region=region,
            encrypt=True,
        )

        # Get RDS stack outputs using remote state
        rds_remote_state = DataTerraformRemoteStateS3(
            self,
            "rds_remote_state",
            bucket="ai-playground-tf-state",
            key="common-infra/terraform.tfstate",
            region=region,
        )

        # Extract RDS stack outputs
        db_secret_arn = rds_remote_state.get_string("database_secret_arn")
        db_endpoint = rds_remote_state.get_string("database_endpoint")
        db_port = rds_remote_state.get_string("database_port")
        # Use the actual database name (aiplaygrounddb) - matches RDS cluster database_name
        # Note: The remote state may have the old value, so we use the correct value directly
        db_name = "aiplaygrounddb"
        db_security_group_id = rds_remote_state.get_string("rds_security_group_id")

        # Get the OpenAI API key from Secrets Manager
        openai_secret = DataAwsSecretsmanagerSecret(
            self,
            "openai_secret",
            name="openai-api-key",
        )

        # Get OpenAI secret value (needed for environment variable)
        openai_secret_version = DataAwsSecretsmanagerSecretVersion(
            self,
            "openai_secret_version",
            secret_id=openai_secret.id,
        )

        # Get RDS database secret
        db_secret = DataAwsSecretsmanagerSecret(
            self,
            "rds_secret",
            arn=db_secret_arn,
        )

        # Get RDS security group (for reference, rule is already created in RDS stack)
        db_security_group = DataAwsSecurityGroup(
            self,
            "rds_security_group",
            id=db_security_group_id,
        )

        # Note: Security group ingress rule for port 5432 is already created in the RDS stack
        # No need to create it here to avoid conflicts

        # Create IAM role for Lambda
        lambda_role = IamRole(
            self,
            "lambda_role",
            name="tq-lambda-role",
            assume_role_policy="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}""",
        )

        # Create IAM policy for Lambda to read secrets
        lambda_policy = IamRolePolicy(
            self,
            "lambda_policy",
            name="tq-lambda-policy",
            role=lambda_role.id,
            policy=f"""{{
  "Version": "2012-10-17",
  "Statement": [
    {{
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": [
        "{openai_secret.arn}",
        "{db_secret_arn}"
      ]
    }},
    {{
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }}
  ]
}}""",
        )

        # Get the Lambda deployment package path (absolute path)
        lambda_code_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../lambda-deployment.zip")
        )

        # Compute hash of the zip file to force updates when code changes
        # Terraform expects base64-encoded SHA256 hash
        source_code_hash = None
        if os.path.exists(lambda_code_path):
            with open(lambda_code_path, "rb") as f:
                file_hash = hashlib.sha256()
                file_hash.update(f.read())
                source_code_hash = base64.b64encode(file_hash.digest()).decode("utf-8")

        # Lambda function
        # Note: For OPENAI_API_KEY, we use the secret string directly
        # If the secret is stored as JSON, you may need to parse it in the Lambda code
        tq_lambda = LambdaFunction(
            self,
            "tq_lambda",
            function_name="tq-lambda",
            runtime="python3.11",
            handler="lambda_function.lambda_handler",
            role=lambda_role.arn,
            filename=lambda_code_path,
            source_code_hash=source_code_hash,
            description="Lambda function that accepts session key as input",
            timeout=30,
            memory_size=256,
            environment={
                "variables": {
                    "OPENAI_API_KEY": openai_secret_version.secret_string,
                    "DB_SECRET_ARN": db_secret_arn,
                    "DB_ENDPOINT": db_endpoint,
                    "DB_PORT": db_port,
                    "DB_NAME": db_name,
                }
            },
        )

        # Lambda Function URL for internal HTTP access
        function_url = LambdaFunctionUrl(
            self,
            "function_url",
            function_name=tq_lambda.function_name,
            authorization_type="AWS_IAM",
            cors={
                "allow_credentials": False,
                "allow_origins": ["*"],
                "allow_methods": ["GET", "POST"],
                "allow_headers": ["Content-Type"],
                "expose_headers": [],
                "max_age": 0,
            },
            depends_on=[tq_lambda],
        )

        # Output the Lambda Function URL
        TerraformOutput(
            self,
            "function_url_output",
            value=function_url.function_url,
            description="Lambda Function URL for internal HTTP access",
        )

        # Output the Lambda function ARN
        TerraformOutput(
            self,
            "lambda_function_arn",
            value=tq_lambda.arn,
            description="Lambda function ARN",
        )
