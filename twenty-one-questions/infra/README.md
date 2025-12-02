# TQ Lambda Infrastructure

This directory contains the AWS CDK infrastructure code for deploying the TQ Lambda function.

## Prerequisites

- Python 3.9 or later
- AWS CLI configured with appropriate credentials
- AWS CDK CLI installed globally: `npm install -g aws-cdk`

## Setup

1. Create a virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Bootstrap CDK (first time only):
```bash
cdk bootstrap
```

## Deployment

1. Synthesize CloudFormation template:
```bash
cdk synth
```

2. Deploy the stack:
```bash
cdk deploy
```

3. View differences before deploying:
```bash
cdk diff
```

## Stack Outputs

After deployment, the stack will output:
- `FunctionUrl`: The Lambda Function URL for internal HTTP access
- `LambdaFunctionArn`: The ARN of the Lambda function

## Lambda Function URL

The Lambda function is exposed via a Function URL for internal HTTP access within the same AWS account. The Function URL uses AWS IAM authentication, so you'll need to sign requests using AWS Signature Version 4.

### Authentication

Since this is for internal use within the same account, requests must be signed with AWS IAM credentials. You can use the AWS SDK or AWS CLI to make authenticated requests.

### Example Request (using AWS SDK - Python with requests-aws4auth)

```python
import requests
from requests_aws4auth import AWS4Auth
import boto3
import json

# Get credentials from boto3 session
session = boto3.Session()
credentials = session.get_credentials()
region = session.region_name or 'us-east-1'

function_url = '<function-url>'

# Create AWS4Auth signer
auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    'lambda'
)

# POST request with session key in body
response = requests.post(
    function_url,
    auth=auth,
    json={'sessionKey': 'your-session-key-here'},
    headers={'Content-Type': 'application/json'}
)

# GET request with session key as query parameter
response = requests.get(
    function_url,
    auth=auth,
    params={'sessionKey': 'your-session-key-here'}
)
```

### Example Request (using AWS SDK - Node.js)

```javascript
const https = require('https');
const { SignatureV4 } = require('@aws-sdk/signature-v4');
const { defaultProvider } = require('@aws-sdk/credential-provider-node');

const functionUrl = '<function-url>';

// POST request
const signer = new SignatureV4({
  credentials: defaultProvider(),
  region: 'us-east-1',
  service: 'lambda',
});

// Use signer to sign the request, then make HTTP call
```

### Direct HTTP Request

For direct HTTP requests, you'll need to sign them with AWS Signature Version 4. The Function URL requires IAM authentication, so all requests must be signed with valid AWS credentials from the same account.

