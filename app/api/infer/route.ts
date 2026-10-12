import { generate, InferenceError } from '@/lib/natlas';
export async function POST(request: Request) {
  const headers = { 'Cache-Control': 'no-store' };
  const origin = request.headers.get('origin');
  if (origin && origin !== new URL(request.url).origin) return Response.json({ error: 'Cross-origin requests are not accepted.' }, { status: 403, headers });
  try {
    const raw = await request.text();
    if (raw.length > 20000) throw new InferenceError('REQUEST_TOO_LARGE', 'Request is too large.');
    const b = JSON.parse(raw);
    if (typeof b.endpoint !== 'string' || typeof b.token !== 'string' || typeof b.model !== 'string' || !b.model.trim() || b.model.length > 200 || b.token.length > 2000 || /[\r\n]/.test(b.token) || !['openai', 'tgi'].includes(b.protocol)) throw new InferenceError('INVALID_CONFIG', 'Check your endpoint, model name and API format.');
    if (typeof b.prompt !== 'string' || !b.prompt.trim() || b.prompt.length > 6000) throw new InferenceError('INVALID_PROMPT', 'Enter a prompt between 1 and 6,000 characters.');
    if (!['English', 'Yoruba', 'Hausa', 'Igbo'].includes(b.language)) throw new InferenceError('INVALID_LANGUAGE', 'Choose a supported language.');
    if (!Number.isInteger(b.maxTokens) || b.maxTokens < 1 || b.maxTokens > 512) throw new InferenceError('INVALID_LIMIT', 'Output limit must be between 1 and 512 tokens.');
    const bindings = process.env;
    const result = await generate(b, b.prompt, b.language, b.maxTokens, bindings.NATLAS_ALLOWED_HOSTS || '');
    return Response.json(result, { headers });
  } catch (e) {
    const known = e instanceof InferenceError;
    return Response.json({ error: known ? e.message : 'Invalid request or unexpected response. Check your configuration and try again.', code: known ? e.code : 'INVALID_REQUEST' }, { status: known ? e.status : 400, headers });
  }
}
