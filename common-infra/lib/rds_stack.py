"""
CDKTF stack for RDS database with minimal configuration.
"""

import json
import os
from pathlib import Path
from cdktf import TerraformStack, TerraformOutput, S3Backend
from constructs import Construct
from cdktf_cdktf_provider_aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.data_aws_vpc import DataAwsVpc
from cdktf_cdktf_provider_aws.data_aws_subnets import DataAwsSubnets
from cdktf_cdktf_provider_aws.db_subnet_group import DbSubnetGroup
from cdktf_cdktf_provider_aws.security_group import SecurityGroup
from cdktf_cdktf_provider_aws.security_group_rule import SecurityGroupRule
from cdktf_cdktf_provider_aws.secretsmanager_secret import SecretsmanagerSecret
from cdktf_cdktf_provider_aws.secretsmanager_secret_version import SecretsmanagerSecretVersion
from cdktf_cdktf_provider_aws.rds_cluster import RdsCluster
from cdktf_cdktf_provider_aws.rds_cluster_instance import RdsClusterInstance


class RDSStack(TerraformStack):
    """Stack that defines the RDS database infrastructure."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id)

        # Configure AWS provider
        region = os.getenv("CDKTF_DEFAULT_REGION", "us-east-1")
        AwsProvider(self, "aws", region=region)

        # Configure S3 backend for Terraform state
        S3Backend(
            self,
            bucket="ai-playground-tf-state",
            key="common-infra/terraform.tfstate",
            region=region,
            encrypt=True,
        )

        # Load database credentials from config file
        config_path = Path(__file__).parent.parent / "config.json"
        with open(config_path, "r") as f:
            config = json.load(f)
        db_username = config["database"]["username"]
        db_password = config["database"]["password"]

        # Get default VPC
        default_vpc = DataAwsVpc(
            self,
            "default_vpc",
            default=True,
        )

        # Get public subnets (for minimal configuration)
        # Note: In production, use private subnets and place Lambda in VPC
        public_subnets = DataAwsSubnets(
            self,
            "public_subnets",
            filter=[
                {
                    "name": "vpc-id",
                    "values": [default_vpc.id],
                },
                {
                    "name": "map-public-ip-on-launch",
                    "values": ["true"],
                },
            ],
        )

        # Create a subnet group for RDS
        subnet_group = DbSubnetGroup(
            self,
            "rds_subnet_group",
            name="rds-subnet-group",
            subnet_ids=public_subnets.ids,
            tags={
                "Name": "rds-subnet-group",
            },
        )

        # Create security group for RDS
        db_security_group = SecurityGroup(
            self,
            "rds_security_group",
            name="rds-security-group",
            description="Security group for RDS database",
            vpc_id=default_vpc.id,
            tags={
                "Name": "rds-security-group",
            },
        )

        # Allow all outbound traffic (egress rule)
        SecurityGroupRule(
            self,
            "rds_egress_rule",
            type="egress",
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
            security_group_id=db_security_group.id,
            description="Allow all outbound traffic",
        )

        # Allow Lambda to connect to RDS from anywhere (for non-VPC Lambda)
        # Note: In production, restrict this to specific IPs or place Lambda in VPC
        SecurityGroupRule(
            self,
            "rds_ingress_rule",
            type="ingress",
            from_port=5432,
            to_port=5432,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
            security_group_id=db_security_group.id,
            description="Allow Lambda to connect to RDS (minimal config - restrict in production)",
        )

        # Create database credentials secret
        db_secret = SecretsmanagerSecret(
            self,
            "rds_secret",
            name="rds-database-credentials",
            description="RDS database credentials",
        )

        # Create secret value with username and password from config
        secret_string = f'{{"username": "{db_username}", "password": "{db_password}"}}'

        SecretsmanagerSecretVersion(
            self,
            "rds_secret_version",
            secret_id=db_secret.id,
            secret_string=secret_string,
        )

        # Create Aurora PostgreSQL cluster with free tier configuration
        # Using engine version 15.6 (15.4 is not available in us-east-1)
        # Note: database_name must be alphanumeric only (no hyphens)
        cluster = RdsCluster(
            self,
            "aurora_cluster",
            cluster_identifier="ai-playground-db",
            engine="aurora-postgresql",
            engine_version="15.6",
            database_name="aiplaygrounddb",
            master_username=db_username,
            master_password=db_password,
            db_subnet_group_name=subnet_group.name,
            vpc_security_group_ids=[db_security_group.id],
            skip_final_snapshot=True,  # For development - change for production
            deletion_protection=False,  # For development
            storage_encrypted=True,
            tags={
                "Name": "ai-playground-db",
            },
        )

        # Create Aurora cluster instance
        # Note: db.t3.small is not available for Aurora PostgreSQL 15.6
        # Using db.t3.medium as the smallest available instance class
        cluster_instance = RdsClusterInstance(
            self,
            "aurora_instance",
            identifier="ai-playground-db-instance-1",
            cluster_identifier=cluster.id,
            instance_class="db.t3.medium",  # Smallest available for Aurora PostgreSQL 15.6
            engine=cluster.engine,
            engine_version="15.6",  # Must match cluster engine version
            publicly_accessible=True,  # For minimal config with non-VPC Lambda
            tags={
                "Name": "ai-playground-db-instance-1",
            },
        )

        # Output database endpoint (Aurora cluster endpoint)
        TerraformOutput(
            self,
            "database_endpoint",
            value=cluster.endpoint,
            description="Aurora cluster endpoint",
        )

        # Output database port
        TerraformOutput(
            self,
            "database_port",
            value=str(cluster.port),
            description="Aurora database port",
        )

        # Output database name (must match the actual database_name in cluster config)
        TerraformOutput(
            self,
            "database_name",
            value=cluster.database_name,
            description="Aurora database name",
        )

        # Output secret ARN
        TerraformOutput(
            self,
            "database_secret_arn",
            value=db_secret.arn,
            description="RDS database credentials secret ARN",
        )

        # Output security group ID for lambda access
        TerraformOutput(
            self,
            "rds_security_group_id",
            value=db_security_group.id,
            description="RDS security group ID",
        )

        # Store references for cross-stack access
        self.cluster = cluster
        self.cluster_instance = cluster_instance
        self.db_secret = db_secret
        self.db_security_group = db_security_group
