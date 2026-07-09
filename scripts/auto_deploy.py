#!/usr/bin/env python3
"""
Auto-deploy listener for Iztack-Finance.
Listens for GitHub webhooks and auto-deploys when develop is pushed.
"""
import os
import sys
import subprocess
import json
import hashlib
import hmac
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

DEPLOY_DIR = Path("/opt/iztack-finance")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

class DeployHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        # Verify signature
        sig = self.headers.get("X-Hub-Signature-256", "")
        if WEBHOOK_SECRET and sig:
            expected = "sha256=" + hmac.new(
                WEBHOOK_SECRET.encode(), body, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(expected, sig):
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Bad signature")
                return
        
        event = self.headers.get("X-GitHub-Event", "")
        if event != "push":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Ignored non-push event")
            return
        
        payload = json.loads(body)
        ref = payload.get("ref", "")
        
        if ref != "refs/heads/develop" and ref != "refs/heads/main":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"Ignored push to {ref}".encode())
            return
        
        print(f"\n=== Auto-deploy triggered by push to {ref} ===")
        result = subprocess.run(
            ["bash", "-c", """
                cd /opt/iztack-finance
                git fetch origin
                git reset --hard origin/develop
                docker compose up -d --build
                echo "Deploy complete"
            """],
            capture_output=True, text=True, timeout=300
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr[:500])
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deploy OK")

    def log_message(self, format, *args):
        print(f"[AutoDeploy] {args[0]} {args[1]} {args[2]}")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
    server = HTTPServer(("0.0.0.0", port), DeployHandler)
    print(f"Auto-deploy webhook listening on :{port}")
    print(f"Configure GitHub repo: Settings > Webhooks > Add webhook")
    print(f"  Payload URL: http://YOUR_IP:{port}")
    print(f"  Content type: application/json")
    print(f"  Secret: (set WEBHOOK_SECRET env var)")
    print(f"  Events: Just the push event")
    server.serve_forever()