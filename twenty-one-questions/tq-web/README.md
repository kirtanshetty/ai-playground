# TQ Web - 21 Questions Game Frontend

A SvelteKit web application for the 21 Questions game.

## Modes

The application supports two modes:

### Default Mode: AWS Lambda (Local & Deployed)

**By default, the application calls the AWS Lambda function directly**, whether running locally or deployed. This works for both local development and production.

**Setup:**
1. Ensure AWS credentials are configured (via AWS CLI, environment variables, or IAM role)
2. Set environment variables (optional, defaults provided):
   - `LAMBDA_FUNCTION_NAME=tq-lambda` (default)
   - `AWS_REGION=us-east-1` (default)

**For Local Development:**
- Make sure your AWS credentials are configured (run `aws configure` or set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`)
- The application will call the deployed Lambda function in AWS

**For AWS Amplify Deployment:**
- Set environment variables in Amplify Console
- Ensure the deployment role has IAM permissions to invoke Lambda

### Debug Mode: Local Python Server

To use a local Python server instead of AWS Lambda (for testing lambda code locally):

**Setup:**
1. Install Python dependencies (see Prerequisites)
2. Set environment variable: `USE_DEBUG_SERVER=true`
3. Start the debug server:
   ```bash
   npm run debug-server
   ```
   Or use the combined command:
   ```bash
   npm run dev:debug
   ```

**Environment Variables:**
- `USE_DEBUG_SERVER=true` (enables local debug server)
- `DEBUG_SERVER_URL=http://localhost:8000` (default)

## Development

### Prerequisites

1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Install Python dependencies for the debug server:**
   ```bash
   # From tq-web directory
   pip install -r ../tq-lambda/requirements.txt
   pip install -r ../../common-lib/llm/requirements.txt
   ```

   Or check if dependencies are installed:
   ```bash
   python3 check_dependencies.py
   ```

### Running the Application

```bash
# Run in debug mode (with debug server)
npm run dev:debug

# Or run separately:
# Terminal 1: Start debug server
npm run debug-server

# Terminal 2: Start dev server
npm run dev
```

## Building

```bash
npm run build
```

## Testing

### Test Lambda Connection

To test if your AWS Lambda connection is working, visit:
```
http://localhost:5173/api/test-lambda
```

This will show you:
- Whether AWS credentials are configured
- Whether the Lambda function exists and is accessible
- Any error messages with helpful troubleshooting tips

### Troubleshooting 500 Errors

If you get a 500 Internal Server Error:

1. **Check the browser console** (F12 → Console) for the error message
2. **Check the terminal** running `npm run dev` for server-side logs
3. **Test Lambda connection**: Visit `/api/test-lambda` to see detailed error information
4. **Common issues**:
   - AWS credentials not configured → Run `aws configure`
   - Lambda function not found → Check function name and region
   - IAM permissions → Ensure your AWS user/role can invoke Lambda functions

## Environment Configuration

Copy `.env.example` to `.env` and configure as needed for your environment.
