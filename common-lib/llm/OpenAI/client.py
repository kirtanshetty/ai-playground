"""
Simple OpenAI client for API calls.
"""

import os
from typing import Optional
from openai import OpenAI


class OpenAIClient:
    """
    Simple client for OpenAI API calls.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY env var or pass api_key.")
        
        self.client = OpenAI(api_key=api_key)
    
    def call(self, prompt: str, model: str = "gpt-4", **kwargs):
        """
        Call the OpenAI API with a given prompt.
        
        Args:
            prompt: The prompt to send to the API.
            model: The model to use. Defaults to "gpt-4".
            **kwargs: Additional arguments to pass to the API (e.g., temperature, max_tokens).
        
        Returns:
            The chat completion response.
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response
