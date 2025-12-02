#!/usr/bin/env python3
"""
CDKTF app entry point for common infrastructure (RDS database).
"""

import os
from cdktf import App
from lib.rds_stack import RDSStack

app = App()
RDSStack(
    app,
    "RDSStack",
)

app.synth()
