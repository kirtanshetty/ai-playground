import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Use process.env directly for better compatibility with Amplify SSR
// Fallback URL is provided for cases where env var isn't propagated correctly
const LAMBDA_FUNCTION_URL = process.env.LAMBDA_FUNCTION_URL;
const FALLBACK_LAMBDA_URL = 'https://j6pfsyy53ljmwbok5osjxrddwe0hfidq.lambda-url.us-east-1.on.aws/';

export const GET: RequestHandler = async () => {
	try {
		// Try multiple ways to get the URL, with fallback
		const functionUrl = LAMBDA_FUNCTION_URL || 
			process.env.LAMBDA_FUNCTION_URL ||
			process.env.lambda_function_url ||
			FALLBACK_LAMBDA_URL;
		
		// Get all env keys for debugging
		const envKeys = Object.keys(process.env).filter(k => 
			k.includes('LAMBDA') || k.includes('AWS') || k.includes('AMPLIFY') || k.includes('NODE')
		);
		
		// Determine URL source for debugging
		const urlSource = LAMBDA_FUNCTION_URL ? 'env-const' : 
			process.env.LAMBDA_FUNCTION_URL ? 'process.env' :
			process.env.lambda_function_url ? 'process.env-lowercase' : 'fallback';

		// Test with a simple session key
		const lambdaResponse = await fetch(functionUrl, {
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
				functionUrl: functionUrl,
				urlSource: urlSource,
				availableEnvKeys: envKeys,
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

