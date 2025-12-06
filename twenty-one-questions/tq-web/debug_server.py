#!/usr/bin/env python3
"""
Debug server for tq-web that calls tq-lambda locally.
This server runs locally and invokes the lambda function directly.

Prerequisites:
    Install lambda dependencies:
    pip install -r ../tq-lambda/requirements.txt
    pip install -r ../../common-lib/llm/requirements.txt
"""

import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import threading

# Add project paths
# debug_server.py is in tq-web/, so go up one level to twenty-one-questions/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
lambda_dir = os.path.join(project_root, "tq-lambda")

# Add lambda directory to path
if lambda_dir not in sys.path:
    sys.path.insert(0, lambda_dir)

# Add common-lib to path
# From twenty-one-questions/, go up one level to ai-playground/, then into common-lib
ai_playground_root = os.path.abspath(os.path.join(project_root, "../"))
common_lib_path = os.path.join(ai_playground_root, "common-lib")
if common_lib_path not in sys.path:
    sys.path.insert(0, common_lib_path)

# Import lambda handler
try:
    from lambda_function import lambda_handler
except ImportError as e:
    print("=" * 60, file=sys.stderr)
    print("ERROR: Missing required dependencies!", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"\nImport error: {e}", file=sys.stderr)
    print("\nPlease install the required dependencies:", file=sys.stderr)
    print("  pip install -r ../tq-lambda/requirements.txt", file=sys.stderr)
    print("  pip install -r ../../common-lib/llm/requirements.txt", file=sys.stderr)
    print("\nOr run the dependency checker:", file=sys.stderr)
    print("  python3 check_dependencies.py", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    sys.exit(1)


class LambdaRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler that invokes the lambda function locally."""

    def do_POST(self):
        """Handle POST requests to /invoke endpoint."""
        if self.path == "/invoke":
            try:
                # Read request body
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                event = json.loads(body.decode("utf-8"))

                # Create a mock context object (lambda function may not use it)
                class MockContext:
                    def __init__(self):
                        self.function_name = "tq-lambda"
                        self.function_version = "$LATEST"
                        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:tq-lambda"
                        self.memory_limit_in_mb = 256
                        self.aws_request_id = "test-request-id"
                        self.log_group_name = "/aws/lambda/tq-lambda"
                        self.log_stream_name = "test-stream"

                context = MockContext()

                # Invoke lambda handler
                result = lambda_handler(event, context)

                # Send response
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode("utf-8"))

            except Exception as e:
                # Send error response
                error_response = {
                    "error": "Internal server error",
                    "message": str(e),
                }
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode("utf-8"))
                print(f"Error: {e}", file=sys.stderr)
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"[{self.address_string()}] {format % args}")


def run_server(port=8000):
    """Run the debug server."""
    server_address = ("", port)
    httpd = HTTPServer(server_address, LambdaRequestHandler)
    print(f"Debug server running on http://localhost:{port}")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    port = int(os.getenv("DEBUG_SERVER_PORT", "8000"))
    run_server(port)

