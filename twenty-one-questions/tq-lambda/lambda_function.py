import json


def lambda_handler(event, context):
    """
    AWS Lambda handler that accepts a session key as input.

    Args:
        event: Lambda event object containing the input data
        context: Lambda context object

    Returns:
        dict: Response containing status code and body
    """
    try:
        # Extract session key from event
        # Support Lambda Function URL (HTTP) and direct invocation formats
        if isinstance(event, dict):
            # Check if it's a Lambda Function URL HTTP event
            if "body" in event:
                # POST request with body
                body = (
                    json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
                )
                session_key = body.get("sessionKey") or body.get("session_key")
            elif "queryStringParameters" in event and event["queryStringParameters"]:
                # GET request with query parameters
                session_key = event["queryStringParameters"].get("sessionKey") or event[
                    "queryStringParameters"
                ].get("session_key")
            else:
                # Direct invocation
                session_key = event.get("sessionKey") or event.get("session_key")
        else:
            session_key = None

        if not session_key:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "error": "Missing session key",
                        "message": "Please provide a sessionKey or session_key in the request",
                    }
                ),
            }

        # Process the session key (add your business logic here)
        # For now, just return a success response
        response_data = {
            "status": "success",
            "sessionKey": session_key,
            "message": "Session key received successfully",
        }

        return {
            "statusCode": 200,
            "body": json.dumps(response_data),
            "headers": {"Content-Type": "application/json"},
        }

    except json.JSONDecodeError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON", "message": str(e)}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error", "message": str(e)}),
        }
