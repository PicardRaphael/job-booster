import { GenerateRequest, GenerateResponse } from '@/types/api';

/**
 * Client-side API functions that call Next.js API routes
 */

export async function generateContent(request: GenerateRequest): Promise<GenerateResponse> {
  const response = await fetch('/api/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to generate response');
  }

  return response.json();
}
