import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

// Determine mode from environment variable
// Use local debug server only if explicitly enabled
const USE_DEBUG_SERVER = env.USE_DEBUG_SERVER === 'true' || env.DEBUG_MODE === 'true';
const DEBUG_SERVER_URL = env.DEBUG_SERVER_URL || 'http://localhost:8000';

// Lambda Function URL - this is the primary way to call Lambda from Amplify
// Set this in Amplify Console environment variables after deploying infrastructure
const LAMBDA_FUNCTION_URL = env.LAMBDA_FUNCTION_URL;

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
			if (!LAMBDA_FUNCTION_URL) {
				throw new Error(
					'LAMBDA_FUNCTION_URL environment variable is not set. ' +
					'Please set it in Amplify Console → App Settings → Environment Variables. ' +
					'Get the URL from: cd twenty-one-questions/infra && cdktf output'
				);
			}

			try {
				const lambdaResponse = await fetch(LAMBDA_FUNCTION_URL, {
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
						`Cannot connect to Lambda Function URL at ${LAMBDA_FUNCTION_URL}. ` +
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

