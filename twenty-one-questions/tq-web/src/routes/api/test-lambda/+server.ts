import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

// Lambda Function URL
const LAMBDA_FUNCTION_URL = env.LAMBDA_FUNCTION_URL;

export const GET: RequestHandler = async () => {
	try {
		if (!LAMBDA_FUNCTION_URL) {
			return json(
				{
					success: false,
					error: 'LAMBDA_FUNCTION_URL not configured',
					help: 'Set LAMBDA_FUNCTION_URL in Amplify Console → Environment Variables. ' +
						'Get the URL by running: cd twenty-one-questions/infra && cdktf output',
				},
				{ status: 500 }
			);
		}

		// Test with a simple session key
		const lambdaResponse = await fetch(LAMBDA_FUNCTION_URL, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				sessionKey: 'test-session-' + Date.now(),
			}),
		});

		if (!lambdaResponse.ok) {
			const errorText = await lambdaResponse.text();
			return json(
				{
					success: false,
					error: 'Lambda function error',
					details: {
						status: lambdaResponse.status,
						response: errorText,
					},
				},
				{ status: 500 }
			);
		}

		const payload = await lambdaResponse.json();

		return json({
			success: true,
			message: 'Lambda function invoked successfully',
			response: payload,
			config: {
				functionUrl: LAMBDA_FUNCTION_URL,
			},
		});
	} catch (error: any) {
		console.error('Lambda test error:', error);

		return json(
			{
				success: false,
				error: 'Failed to invoke Lambda function',
				details: {
					message: error.message || String(error),
					name: error.name,
				},
			},
			{ status: 500 }
		);
	}
};

