import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

// AWS Lambda configuration
const LAMBDA_FUNCTION_NAME = env.LAMBDA_FUNCTION_NAME || 'tq-lambda';
const AWS_REGION = env.AWS_REGION || 'us-east-1';

export const GET: RequestHandler = async () => {
	try {
		const { LambdaClient, InvokeCommand } = await import('@aws-sdk/client-lambda');

		const lambdaClient = new LambdaClient({ region: AWS_REGION });

		// Test with a simple session key
		const command = new InvokeCommand({
			FunctionName: LAMBDA_FUNCTION_NAME,
			Payload: JSON.stringify({
				sessionKey: 'test-session-' + Date.now(),
			}),
		});

		const lambdaResponse = await lambdaClient.send(command);

		if (lambdaResponse.FunctionError) {
			const errorPayload = lambdaResponse.Payload 
				? JSON.parse(new TextDecoder().decode(lambdaResponse.Payload))
				: {};
			return json(
				{
					success: false,
					error: 'Lambda function error',
					details: {
						functionError: lambdaResponse.FunctionError,
						errorPayload,
					},
				},
				{ status: 500 }
			);
		}

		if (!lambdaResponse.Payload) {
			return json(
				{
					success: false,
					error: 'Lambda returned empty response',
				},
				{ status: 500 }
			);
		}

		const payload = JSON.parse(new TextDecoder().decode(lambdaResponse.Payload));

		return json({
			success: true,
			message: 'Lambda function invoked successfully',
			response: payload,
			config: {
				functionName: LAMBDA_FUNCTION_NAME,
				region: AWS_REGION,
			},
		});
	} catch (error: any) {
		console.error('Lambda test error:', error);

		let errorDetails: any = {
			message: error.message || String(error),
			name: error.name,
		};

		// Provide helpful error messages for common AWS issues
		if (error.name === 'CredentialsProviderError' || error.message?.includes('credentials')) {
			errorDetails.help = 'AWS credentials not configured. Please run `aws configure` or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.';
		} else if (error.name === 'ResourceNotFoundException' || error.message?.includes('not found')) {
			errorDetails.help = `Lambda function '${LAMBDA_FUNCTION_NAME}' not found in region '${AWS_REGION}'. Please check the function name and region.`;
		} else if (error.name === 'AccessDeniedException' || error.message?.includes('AccessDenied')) {
			errorDetails.help = `Access denied to Lambda function '${LAMBDA_FUNCTION_NAME}'. Please check your IAM permissions.`;
		}

		return json(
			{
				success: false,
				error: 'Failed to invoke Lambda function',
				details: errorDetails,
			},
			{ status: 500 }
		);
	}
};

