import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

// Determine mode from environment variable
// Use local debug server only if explicitly enabled
// Otherwise, call AWS Lambda directly (works for both local and deployed)
const USE_DEBUG_SERVER = env.USE_DEBUG_SERVER === 'true' || env.DEBUG_MODE === 'true';
const DEBUG_SERVER_URL = env.DEBUG_SERVER_URL || 'http://localhost:8000';

// AWS Lambda configuration
const LAMBDA_FUNCTION_NAME = env.LAMBDA_FUNCTION_NAME || 'tq-lambda';
const AWS_REGION = env.AWS_REGION || 'us-east-1';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const body = await request.json();
		const { sessionKey, answer, questionNumber } = body;

		if (!sessionKey) {
			return json({ error: 'Missing sessionKey' }, { status: 400 });
		}

		let response;

		if (USE_DEBUG_SERVER) {
			// Debug mode: Call local Python server
			try {
				const debugResponse = await fetch(`${DEBUG_SERVER_URL}/invoke`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						sessionKey,
						answer,
						questionNumber,
					}),
				});

				if (!debugResponse.ok) {
					const errorText = await debugResponse.text();
					throw new Error(`Debug server error (${debugResponse.status}): ${errorText}`);
				}

				response = await debugResponse.json();
			} catch (fetchError) {
				if (fetchError instanceof TypeError && fetchError.message.includes('fetch')) {
					throw new Error(
						`Cannot connect to debug server at ${DEBUG_SERVER_URL}. Make sure the debug server is running (npm run debug-server)`
					);
				}
				throw fetchError;
			}
		} else {
			// Call AWS Lambda directly using AWS SDK
			try {
				const { LambdaClient, InvokeCommand } = await import('@aws-sdk/client-lambda');

				const lambdaClient = new LambdaClient({ region: AWS_REGION });

				const command = new InvokeCommand({
					FunctionName: LAMBDA_FUNCTION_NAME,
					Payload: JSON.stringify({
						sessionKey,
						answer,
						questionNumber,
					}),
				});

				const lambdaResponse = await lambdaClient.send(command);

				if (lambdaResponse.FunctionError) {
					const errorPayload = lambdaResponse.Payload 
						? JSON.parse(new TextDecoder().decode(lambdaResponse.Payload))
						: {};
					throw new Error(
						`Lambda function error: ${lambdaResponse.FunctionError}. ` +
						`Details: ${JSON.stringify(errorPayload)}`
					);
				}

				if (!lambdaResponse.Payload) {
					throw new Error('Lambda returned empty response');
				}

				const payload = JSON.parse(
					new TextDecoder().decode(lambdaResponse.Payload)
				);
				response = payload;
			} catch (awsError: any) {
				// Provide helpful error messages for common AWS issues
				if (awsError.name === 'CredentialsProviderError' || awsError.message?.includes('credentials')) {
					throw new Error(
						'AWS credentials not configured. Please run `aws configure` or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.'
					);
				}
				if (awsError.name === 'ResourceNotFoundException' || awsError.message?.includes('not found')) {
					throw new Error(
						`Lambda function '${LAMBDA_FUNCTION_NAME}' not found in region '${AWS_REGION}'. ` +
						`Please check the function name and region.`
					);
				}
				if (awsError.name === 'AccessDeniedException' || awsError.message?.includes('AccessDenied')) {
					throw new Error(
						`Access denied to Lambda function '${LAMBDA_FUNCTION_NAME}'. ` +
						`Please check your IAM permissions.`
					);
				}
				throw awsError;
			}
		}

		return json(response);
	} catch (error) {
		console.error('Error calling lambda:', error);
		const errorMessage = error instanceof Error ? error.message : String(error);
		const errorStack = error instanceof Error ? error.stack : undefined;
		
		// Log full error details for debugging
		console.error('Full error details:', {
			message: errorMessage,
			stack: errorStack,
			error: error,
		});
		
		return json(
			{
				error: 'Internal server error',
				message: errorMessage,
				// Include stack trace in development mode for debugging
				...(import.meta.env.DEV && errorStack ? { stack: errorStack } : {}),
			},
			{ status: 500 }
		);
	}
};

