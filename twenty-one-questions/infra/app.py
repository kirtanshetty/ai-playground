#!/usr/bin/env python3
"""
CDKTF app entry point for TQ Lambda infrastructure.
"""

import os
from cdktf import App
from lib.infra_stack import TQLambdaStack

app = App()
TQLambdaStack(
    app,
    "TQLambdaStack",
)

app.synth()
