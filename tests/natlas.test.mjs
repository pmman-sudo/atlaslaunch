import test from 'node:test';
import assert from 'node:assert/strict';
import { validateEndpoint, buildPayload, parseGeneration, generate, endpointTimeoutMs, MODEL } from '../lib/natlas.ts';
const config = { endpoint: 'https://unit.endpoints.huggingface.cloud/v1/chat/completions', token: 'test-secret', protocol: 'openai', model: MODEL };
test('host allowlist blocks private addresses, deceptive suffixes and credential URLs', () => {
  for (const endpoint of ['http://localhost:8000', 'https://127.0.0.1', 'https://169.254.169.254', 'https://unit.endpoints.huggingface.cloud.attacker.test', 'https://a:b@unit.endpoints.huggingface.cloud', config.endpoint + '?token=secret', config.endpoint + '#test']) assert.throws(() => validateEndpoint(endpoint));
  assert.equal(validateEndpoint(config.endpoint).hostname, 'unit.endpoints.huggingface.cloud');
  assert.equal(validateEndpoint('https://inference.example/generate', 'inference.example').hostname, 'inference.example');
});
test('chat and TGI payloads preserve model-specific formatting', () => {
  const chat = buildPayload(config, 'Hello', 'Igbo', 20);
  assert.equal(chat.model, MODEL); assert.equal(chat.max_tokens, 20); assert.match(chat.messages[0].content, /Igbo/);
  const tgi = buildPayload({ ...config, protocol: 'tgi' }, 'Hello', 'Yoruba', 50);
  assert.match(tgi.inputs, /^<\|begin_of_text\|>/); assert.equal(tgi.parameters.return_full_text, false);
});
test('empty or wrong response shapes cannot be reported as success', () => {
  for (const data of [null, {}, [], { choices: [] }, { generated_text: '' }]) assert.throws(() => parseGeneration(data, 10));
  assert.equal(parseGeneration([{ generated_text: 'hello' }], 15).text, 'hello');
});
test('live adapter sends auth only upstream, disables redirects and parses output', async () => {
  const result = await generate(config, 'Hello', 'English', 10, '', async (url, init) => {
    assert.equal(url, config.endpoint); assert.equal(init.headers.Authorization, 'Bearer test-secret'); assert.equal(init.redirect, 'manual');
    return Response.json({ choices: [{ message: { content: 'hello' } }], model: MODEL });
  });
  assert.equal(result.text, 'hello'); assert.equal(result.reported_model, MODEL); assert.ok(!JSON.stringify(result).includes('test-secret'));
});
for (const [status, code] of [[401,'AUTHENTICATION_FAILED'],[403,'ACCESS_DENIED'],[404,'ENDPOINT_NOT_FOUND'],[429,'RATE_LIMITED'],[503,'MODEL_UNAVAILABLE']]) {
  test(`HTTP ${status} gives actionable error without echoing upstream body`, async () => {
    await assert.rejects(generate(config, 'Hello', 'English', 10, '', async () => new Response('test-secret', { status })), e => e.code === code && !e.message.includes('test-secret'));
  });
}
test('timeout and invalid JSON are reported intentionally', async () => {
  await assert.rejects(generate(config, 'Hello', 'English', 10, '', async () => { throw new DOMException('test', 'TimeoutError'); }), e => e.code === 'TIMEOUT');
  await assert.rejects(generate(config, 'Hello', 'English', 10, '', async () => new Response('<html>error</html>')), e => e.code === 'INVALID_RESPONSE');
});
test('oversized upstream response is rejected', async () => {
  await assert.rejects(generate(config, 'Hello', 'English', 10, '', async () => new Response('x'.repeat(513000))), e => e.code === 'RESPONSE_TOO_LARGE');
});

test('Modal hosts work, deceptive hosts fail and cold starts have a bounded timeout', async () => {
  const modal = { ...config, endpoint: 'https://paul--atlaslaunch-web.modal.run/v1/chat/completions' };
  assert.equal(validateEndpoint(modal.endpoint).hostname, 'paul--atlaslaunch-web.modal.run');
  for (const url of ['https://paul--atlaslaunch-web.modal.run.attacker.test', 'https://modal.run', 'https://paul.modal.run@attacker.test', 'https://paul.modal.run:8443']) assert.throws(() => validateEndpoint(url));
  assert.equal(endpointTimeoutMs(modal.endpoint), 120000);
  assert.equal(endpointTimeoutMs(config.endpoint), 45000);
  await assert.rejects(generate(modal, 'Hello', 'English', 10, '', async () => new Response(null, {status: 303, headers: {Location: 'https://attacker.test'}})), e => e.code === 'MODEL_STARTING');
});
