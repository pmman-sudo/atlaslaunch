export const MODEL = 'NCAIR1/N-ATLaS';
export type Protocol = 'openai' | 'tgi';
export type Config = { endpoint: string; token: string; protocol: Protocol; model: string };
export type Generation = { text: string; latency_ms: number; reported_model: string | null; tokens: number | null };
export class InferenceError extends Error {
  code: string; status: number;
  constructor(code: string, message: string, status = 400) { super(message); this.code = code; this.status = status; }
}
export function endpointTimeoutMs(endpoint: string): number {
  try { return new URL(endpoint).hostname.endsWith('.modal.run') ? 120000 : 45000; } catch { return 45000; }
}
export function validateEndpoint(value: string, additionalHosts = ''): URL {
  let url: URL;
  try { url = new URL(value); } catch { throw new InferenceError('INVALID_ENDPOINT', 'Enter the complete HTTPS inference endpoint.'); }
  if (url.protocol !== 'https:' || url.username || url.password || url.search || url.hash || (url.port && url.port !== '443')) throw new InferenceError('INVALID_ENDPOINT', 'Use HTTPS on port 443, without credentials, query parameters or fragments in the URL.');
  const allowed = additionalHosts.split(',').map(v => v.trim().toLowerCase()).filter(Boolean);
  const host = url.hostname.toLowerCase();
  if (!host.endsWith('.endpoints.huggingface.cloud') && !host.endsWith('.modal.run') && !allowed.includes(host)) throw new InferenceError('HOST_NOT_ALLOWED', 'Use your Hugging Face or Modal inference endpoint. A site administrator can enable another trusted host using NATLAS_ALLOWED_HOSTS.');
  return url;
}
export function buildPayload(config: Config, prompt: string, language: string, maxTokens: number) {
  const system = `You are a helpful assistant. Respond in ${language}. Be concise and state uncertainty when appropriate.`;
  if (config.protocol === 'openai') return { model: config.model, messages: [{ role: 'system', content: system }, { role: 'user', content: prompt }], max_tokens: maxTokens, temperature: 0.1, stream: false };
  return { inputs: `<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n${system}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n${prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n`, parameters: { max_new_tokens: maxTokens, temperature: 0.1, return_full_text: false } };
}
export function parseGeneration(data: unknown, elapsed: number): Generation {
  const d = data as { choices?: { message?: { content?: unknown } }[]; generated_text?: unknown; model?: unknown; usage?: { total_tokens?: unknown } };
  const text = d?.choices?.[0]?.message?.content ?? d?.generated_text ?? (Array.isArray(data) ? data[0]?.generated_text : undefined);
  if (typeof text !== 'string' || !text.trim()) throw new InferenceError('INVALID_RESPONSE', 'The endpoint returned no usable text. Check the selected API format and full endpoint path.', 502);
  return { text, latency_ms: Math.round(elapsed), reported_model: typeof d.model === 'string' ? d.model : null, tokens: typeof d.usage?.total_tokens === 'number' ? d.usage.total_tokens : null };
}
export async function generate(config: Config, prompt: string, language: string, maxTokens: number, allowedHosts = '', fetcher: typeof fetch = fetch): Promise<Generation> {
  const url = validateEndpoint(config.endpoint, allowedHosts);
  const started = performance.now();
  const timeoutMs = endpointTimeoutMs(url.href);
  const headers: Record<string, string> = { 'Content-Type': 'application/json', Accept: 'application/json' };
  if (config.token) headers.Authorization = `Bearer ${config.token}`;
  let response: Response;
  try {
    response = await fetcher(url.href, { method: 'POST', headers, body: JSON.stringify(buildPayload(config, prompt, language, maxTokens)), redirect: 'manual', signal: AbortSignal.timeout(timeoutMs) });
  } catch (e) {
    if (e instanceof Error && (e.name === 'TimeoutError' || e.name === 'AbortError')) throw new InferenceError('TIMEOUT', `No response within ${timeoutMs / 1000} seconds. The model may be starting. For Modal, run check_endpoint.py from the deployment kit to warm it up before retrying.`, 504);
    throw new InferenceError('NETWORK_ERROR', 'Could not reach the endpoint. Check its address, deployment status and TLS configuration. Redirects are not followed.', 502);
  }
  if (!response.ok) {
    const errors: Record<number, [string, string]> = {
      303: ['MODEL_STARTING', 'The endpoint is still processing. Run check_endpoint.py from the Modal deployment kit to warm up the model, then retry.'],
      401: ['AUTHENTICATION_FAILED', 'The endpoint rejected the token. Check its value and access permissions.'],
      403: ['ACCESS_DENIED', 'Access is denied. Confirm model access conditions and endpoint permissions.'],
      404: ['ENDPOINT_NOT_FOUND', 'Endpoint not found. Chat APIs usually require /v1/chat/completions; TGI uses /generate.'],
      429: ['RATE_LIMITED', 'The endpoint is rate limited. Wait before retrying or check your provider quota.'],
      503: ['MODEL_UNAVAILABLE', 'The model is unavailable or still starting. Check your deployment and try again.'],
    };
    const [code, message] = errors[response.status] ?? ['UPSTREAM_ERROR', `The inference service returned HTTP ${response.status}. Check its API format and provider logs.`];
    await response.body?.cancel(); throw new InferenceError(code, message, 502);
  }
  const reader = response.body?.getReader();
  if (!reader) throw new InferenceError('INVALID_RESPONSE', 'The endpoint returned an empty response.', 502);
  const chunks: Uint8Array[] = []; let size = 0;
  while (true) { const { done, value } = await reader.read(); if (done) break; size += value.byteLength; if (size > 512000) { await reader.cancel(); throw new InferenceError('RESPONSE_TOO_LARGE', 'The response exceeded the 500 KB limit.', 502); } chunks.push(value); }
  const bytes = new Uint8Array(size); let offset = 0; for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  let data: unknown;
  try { data = JSON.parse(new TextDecoder().decode(bytes)); } catch { throw new InferenceError('INVALID_RESPONSE', 'The endpoint returned invalid JSON. Check the endpoint path and API format.', 502); }
  return parseGeneration(data, performance.now() - started);
}
