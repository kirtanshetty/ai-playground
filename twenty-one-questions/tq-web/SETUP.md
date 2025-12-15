# TQ Web Setup Guide

## Overview

The tq-web application has been configured with two modes:

1. **Debug Mode**: Calls tq-lambda locally via a Python debug server
2. **Release Mode**: Calls tq-lambda deployed on AWS Lambda

## Default Setup: AWS Lambda via Function URL

**By default, the application calls AWS Lambda via its Function URL** (HTTP endpoint).

### Prerequisites
- Lambda function deployed to AWS with Function URL enabled
- Lambda Function URL configured in environment variables

### Running Locally with AWS Lambda

1. **Get the Lambda Function URL:**
   ```bash
   cd twenty-one-questions/infra
   cdktf output
   ```
   Look for the `function_url_output` value.

2. **Set the environment variable and start the dev server:**
   ```bash
   cd twenty-one-questions/tq-web
   export LAMBDA_FUNCTION_URL=https://your-function-url.lambda-url.us-east-1.on.aws/
   npm run dev
   ```

### Environment Variables
- `LAMBDA_FUNCTION_URL` - **Required** for production mode. The Lambda Function URL from infrastructure deployment.

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
- tq-lambda function deployed to AWS with Function URL
- AWS Amplify app configured

### Configuration

#### Step 1: Deploy Infrastructure

Deploy the Lambda function and get the Function URL:

```bash
cd twenty-one-questions/infra
cdktf deploy
```

Note the `function_url_output` value from the deployment output. It looks like:
`https://xxxxxxxxxx.lambda-url.us-east-1.on.aws/`

#### Step 2: Set Environment Variables in Amplify

1. Go to **Amplify Console → Your App → Hosting → Environment Variables**
2. Add the following variable:
   - `LAMBDA_FUNCTION_URL` = `https://xxxxxxxxxx.lambda-url.us-east-1.on.aws/` (your Function URL from Step 1)

#### Step 3: Redeploy

Trigger a new deployment in Amplify to pick up the environment variable.

### Troubleshooting

**Error: "LAMBDA_FUNCTION_URL environment variable is not set"**
- Add the `LAMBDA_FUNCTION_URL` environment variable in Amplify Console
- Get the URL by running `cdktf output` in the infra directory
- Redeploy the app after adding the variable

**Error: "Cannot connect to Lambda Function URL"**
- Verify the Lambda function is deployed: `aws lambda get-function --function-name tq-lambda`
- Check the Function URL is correct and accessible
- Test the URL directly: `curl -X POST <function-url> -H "Content-Type: application/json" -d '{"sessionKey":"test"}'`

**Test the Lambda connection:**
Visit `https://your-amplify-app.amplifyapp.com/api/test-lambda` to verify the connection.

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
- In release mode, ensure `LAMBDA_FUNCTION_URL` is set

### Lambda Invocation Errors (Release Mode)
- Verify Lambda function is deployed and accessible
- Check the Function URL is correct (should end with `.lambda-url.<region>.on.aws/`)
- Test the Function URL directly with curl

