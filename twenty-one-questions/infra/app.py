#!/usr/bin/env python3
"""
CDK app entry point for TQ Lambda infrastructure.
"""

import os
import aws_cdk as cdk
from lib.infra_stack import TQLambdaStack

app = cdk.App()
TQLambdaStack(
    app,
    "TQLambdaStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION", "us-east-1"),
    ),
)

app.synth()
