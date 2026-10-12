"""Run real requests and export results. Errors are retained; no fake successes."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from atlaslaunch import AtlasClient, AtlasError
from atlaslaunch.client import LANGUAGES

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="cases.json")
    parser.add_argument("--output", default="report.json")
    parser.add_argument("--tester", default="")
    args = parser.parse_args()
    load_dotenv()
    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not 1 <= len(cases) <= 20 or any(not isinstance(c, dict) or not isinstance(c.get("id"), str) or not isinstance(c.get("prompt"), str) or not 1 <= len(c["prompt"]) <= 6000 or c.get("language") not in LANGUAGES for c in cases):
        parser.error("Provide 1–20 cases with id, prompt and a supported language.")
    try:
        client = AtlasClient.from_env()
    except AtlasError as error:
        parser.error(f"{error.code}: {error}")
    rows = []
    for case in cases:
        row = {**case, "timestamp": datetime.now(timezone.utc).isoformat(), "mode": "live", "score": None, "notes": "", "max_tokens": 192, "temperature": 0.1, "protocol": client.protocol, "configured_model": client.model}
        try:
            row.update(client.generate(case["prompt"], case["language"]))
            row["error"] = None
        except AtlasError as error:
            row.update({"error": f"{error.code}: {error}", "text": "", "latency_ms": None})
        rows.append(row)
        print(f"{case['id']}: {'error' if row['error'] else 'response received'}")
        Path(args.output).write_text(json.dumps({"schema_version": "1.0", "tester_alias": args.tester, "notice": "Transport success is not accuracy. Model identity is operator-configured. Human review and deployment provenance required.", "results": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(rows)} results to {args.output}")

if __name__ == "__main__":
    main()
