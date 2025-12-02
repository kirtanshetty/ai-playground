"""
CDK stack for TQ Lambda function.
"""

import os
from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    Fn,
)
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class TQLambdaStack(Stack):
    """Stack that defines the TQ Lambda function infrastructure."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get the OpenAI API key from Secrets Manager
        openai_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "OpenAISecret", "openai-api-key"
        )

        # Import RDS database secret from common-infra stack
        db_secret_arn = Fn.import_value("RDSStack-RDSDatabaseSecretArn")
        db_secret = secretsmanager.Secret.from_secret_complete_arn(
            self, "RDSSecret", db_secret_arn
        )

        # Import RDS database endpoint and port from common-infra stack
        db_endpoint = Fn.import_value("RDSStack-RDSDatabaseEndpoint")
        db_port = Fn.import_value("RDSStack-RDSDatabasePort")
        db_name = Fn.import_value("RDSStack-RDSDatabaseName")

        # Import RDS security group from common-infra stack
        db_security_group_id = Fn.import_value("RDSStack-RDSSecurityGroupId")
        db_security_group = ec2.SecurityGroup.from_security_group_id(
            self, "RDSSecurityGroup", db_security_group_id
        )

        # Get default VPC for lambda security group
        vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)

        # Create security group for Lambda (if needed for VPC access)
        # For now, we'll allow Lambda to connect to RDS without VPC
        # If Lambda needs VPC access, uncomment and configure:
        # lambda_security_group = ec2.SecurityGroup(
        #     self,
        #     "LambdaSecurityGroup",
        #     vpc=vpc,
        #     description="Security group for Lambda function",
        #     allow_all_outbound=True,
        # )
        # db_security_group.add_ingress_rule(
        #     lambda_security_group,
        #     ec2.Port.tcp(5432),
        #     "Allow Lambda to connect to RDS"
        # )

        # Allow Lambda to connect to RDS from anywhere (for non-VPC Lambda)
        # Note: In production, restrict this to specific IPs or place Lambda in VPC
        # and use security group rules instead of allowing all IPs
        db_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(5432),
            "Allow Lambda to connect to RDS (minimal config - restrict in production)"
        )

        # Lambda function
        tq_lambda = lambda_.Function(
            self,
            "TQLambdaFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "../../tq-lambda")
            ),
            function_name="tq-lambda",
            description="Lambda function that accepts session key as input",
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "OPENAI_API_KEY": openai_secret.secret_value.unsafe_unwrap(),
                "DB_SECRET_ARN": db_secret_arn,
                "DB_ENDPOINT": db_endpoint,
                "DB_PORT": db_port,
                "DB_NAME": db_name,
            },
        )

        # Grant the Lambda permission to read the secrets
        openai_secret.grant_read(tq_lambda)
        db_secret.grant_read(tq_lambda)

        # Lambda Function URL for internal HTTP access
        function_url = tq_lambda.add_function_url(
            # Requires IAM authentication for internal access
            auth_type=lambda_.FunctionUrlAuthType.AWS_IAM,
            cors=lambda_.FunctionUrlCorsOptions(
                # Adjust as needed for your internal services
                allowed_origins=["*"],
                allowed_methods=[lambda_.HttpMethod.GET, lambda_.HttpMethod.POST],
                allowed_headers=["Content-Type"],
            ),
        )

        # Output the Lambda Function URL
        CfnOutput(
            self,
            "FunctionUrl",
            value=function_url.url,
            description="Lambda Function URL for internal HTTP access",
        )

        # Output the Lambda function ARN
        CfnOutput(
            self,
            "LambdaFunctionArn",
            value=tq_lambda.function_arn,
            description="Lambda function ARN",
        )
