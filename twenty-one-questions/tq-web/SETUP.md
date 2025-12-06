# TQ Web Setup Guide

## Overview

The tq-web application has been configured with two modes:

1. **Debug Mode**: Calls tq-lambda locally via a Python debug server
2. **Release Mode**: Calls tq-lambda deployed on AWS Lambda

## Default Setup: AWS Lambda (Local & Deployed)

**By default, the application calls AWS Lambda directly**, whether running locally or deployed.

### Prerequisites
- AWS credentials configured (via `aws configure` or environment variables)
- Lambda function deployed to AWS
- IAM permissions to invoke the Lambda function

### Running Locally with AWS Lambda

1. **Configure AWS credentials:**
   ```bash
   aws configure
   ```
   Or set environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your-key
   export AWS_SECRET_ACCESS_KEY=your-secret
   export AWS_REGION=us-east-1
   ```

2. **Start the dev server:**
   ```bash
   cd twenty-one-questions/tq-web
   npm run dev
   ```

### Environment Variables (Optional)
- `LAMBDA_FUNCTION_NAME=tq-lambda` (default)
- `AWS_REGION=us-east-1` (default)

## Debug Mode Setup (Local Python Server)

To use a local Python server instead of AWS Lambda:

### Prerequisites
- Python 3.9+ installed
- All lambda dependencies installed (from `tq-lambda/requirements.txt`)
- Access to the lambda function code locally

### Running in Debug Mode

1. **Set environment variable:**
   ```bash
   export USE_DEBUG_SERVER=true
   ```

2. **Start the debug server** (in one terminal):
   ```bash
   cd twenty-one-questions/tq-web
   python3 debug_server.py
   ```
   The server will run on `http://localhost:8000` by default.

3. **Start the SvelteKit dev server** (in another terminal):
   ```bash
   cd twenty-one-questions/tq-web
   npm run dev
   ```

   Or use the combined command:
   ```bash
   npm run dev:debug
   ```

### Environment Variables for Debug Mode
- `USE_DEBUG_SERVER=true` (enables local debug server)
- `DEBUG_SERVER_URL=http://localhost:8000` (default)

## Release Mode Setup (AWS Amplify)

### Prerequisites
- AWS account with appropriate IAM permissions
- tq-lambda function deployed to AWS
- AWS Amplify app configured

### Configuration

Set the following environment variables in AWS Amplify:

1. **In Amplify Console → App Settings → Environment Variables**:
   - `DEBUG_MODE=false` (or leave unset)
   - `LAMBDA_FUNCTION_NAME=tq-lambda`
   - `AWS_REGION=us-east-1` (or your region)

2. **IAM Permissions**: Ensure your Amplify deployment role has permission to invoke the Lambda function:
   ```json
   {
     "Effect": "Allow",
     "Action": "lambda:InvokeFunction",
     "Resource": "arn:aws:lambda:*:*:function:tq-lambda"
   }
   ```

### Building for Release

```bash
npm run build
```

The build will use release mode automatically when `DEBUG_MODE` is not set to `true`.

## How It Works

### API Route (`/api/game`)

The SvelteKit API route at `src/routes/api/game/+server.ts` handles both modes:

- **Debug Mode**: Makes HTTP request to local Python debug server
- **Release Mode**: Uses AWS SDK to invoke Lambda function directly

### Debug Server

The Python debug server (`debug_server.py`):
- Runs locally on port 8000
- Imports and invokes the lambda handler directly
- Provides HTTP endpoint `/invoke` that accepts POST requests
- Returns the same response format as the AWS Lambda function

### Frontend Integration

The `GameBoard.svelte` component:
- Generates a unique session key when game starts
- Calls `/api/game` endpoint with session key and answers
- Handles responses and updates game state

## Testing

### Test Debug Mode Locally

1. Start debug server: `python3 debug_server.py`
2. Start dev server: `npm run dev`
3. Open browser to `http://localhost:5173` (or your dev server port)
4. Start a game and answer questions

### Test Release Mode

1. Deploy to AWS Amplify with environment variables set
2. Ensure Lambda function is deployed and accessible
3. Test the deployed application

## Troubleshooting

### Debug Server Not Starting
- Check Python version: `python3 --version`
- Install lambda dependencies: `pip install -r ../tq-lambda/requirements.txt`
- Check that lambda function code is accessible

### API Route Errors
- Check console logs for detailed error messages
- Verify environment variables are set correctly
- In release mode, ensure AWS credentials are configured

### Lambda Invocation Errors (Release Mode)
- Verify IAM permissions for Lambda invocation
- Check Lambda function name matches `LAMBDA_FUNCTION_NAME`
- Verify AWS region is correct

