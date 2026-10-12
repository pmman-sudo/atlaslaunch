export function GET() {
  return Response.json(
    { status: 'ok', service: 'atlaslaunch', model_connection: 'not_checked' },
    { headers: { 'Cache-Control': 'no-store' } },
  );
}
