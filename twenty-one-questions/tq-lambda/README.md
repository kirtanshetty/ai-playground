# TQ Lambda Function

AWS Lambda function that accepts a session key as input.

## Function Details

- **Runtime**: Python 3.11
- **Handler**: `lambda_function.lambda_handler`
- **Input**: Session key (via `sessionKey` or `session_key` parameter)

## Input Formats

The function accepts session keys in multiple formats:

1. **API Gateway POST request** (JSON body):
```json
{
  "sessionKey": "your-session-key-here"
}
```

2. **API Gateway GET request** (query parameter):
```
?sessionKey=your-session-key-here
```

3. **Direct Lambda invocation**:
```json
{
  "sessionKey": "your-session-key-here"
}
```

## Response Format

### Success Response (200)
```json
{
  "status": "success",
  "sessionKey": "your-session-key-here",
  "message": "Session key received successfully"
}
```

### Error Response (400)
```json
{
  "error": "Missing session key",
  "message": "Please provide a sessionKey or session_key in the request"
}
```

## Local Testing

You can test the function locally using the AWS SAM CLI or by invoking it directly:

```python
# test_event.json
{
  "sessionKey": "test-session-123"
}
```

```bash
# Using AWS SAM
sam local invoke -e test_event.json

# Or using Python directly
python -c "from lambda_function import lambda_handler; import json; print(json.dumps(lambda_handler({'sessionKey': 'test'}, None), indent=2))"
```

## Deployment

This function is deployed via the infrastructure code in the `../infra` folder using AWS CDK.

