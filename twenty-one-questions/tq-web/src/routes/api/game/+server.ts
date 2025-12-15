import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

// Use process.env directly for better compatibility with Amplify SSR
const USE_DEBUG_SERVER = process.env.USE_DEBUG_SERVER === 'true' || process.env.DEBUG_MODE === 'true';
const DEBUG_SERVER_URL = process.env.DEBUG_SERVER_URL || 'http://localhost:8000';

// Lambda Function URL - this is the primary way to call Lambda from Amplify
// Set this in Amplify Console environment variables after deploying infrastructure
// Fallback URL is provided for cases where env var isn't propagated correctly
const LAMBDA_FUNCTION_URL = process.env.LAMBDA_FUNCTION_URL;
const FALLBACK_LAMBDA_URL = 'https://j6pfsyy53ljmwbok5osjxrddwe0hfidq.lambda-url.us-east-1.on.aws/';

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
			// Production mode: Call Lambda via Function URL (HTTP)
			// Try multiple ways to get the URL, with fallback
			const functionUrl = LAMBDA_FUNCTION_URL || 
				process.env.LAMBDA_FUNCTION_URL ||
				process.env.lambda_function_url ||
				FALLBACK_LAMBDA_URL;
			
			// Log which URL source we're using
			const urlSource = LAMBDA_FUNCTION_URL ? 'env-const' : 
				process.env.LAMBDA_FUNCTION_URL ? 'process.env' :
				process.env.lambda_function_url ? 'process.env-lowercase' : 'fallback';
			console.log(`Using Lambda URL from: ${urlSource}`);

			try {
				const lambdaResponse = await fetch(functionUrl, {
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

				if (!lambdaResponse.ok) {
					const errorText = await lambdaResponse.text();
					throw new Error(
						`Lambda function error (${lambdaResponse.status}): ${errorText}`
					);
				}

				response = await lambdaResponse.json();
			} catch (fetchError: any) {
				if (fetchError instanceof TypeError && fetchError.message.includes('fetch')) {
					throw new Error(
						`Cannot connect to Lambda Function URL at ${functionUrl}. ` +
						`Please verify the URL is correct and the Lambda function is deployed.`
					);
				}
				throw fetchError;
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

