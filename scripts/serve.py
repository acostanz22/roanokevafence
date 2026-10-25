"""Preview server with the same redirects a static host will apply."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def load_rules():
    rules = []
    path = ROOT / "_redirects"
    if not path.is_file():
        return rules
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        code = int(parts[2]) if len(parts) > 2 else 301
        rules.append((parts[0], parts[1], code))
    return rules


RULES = load_rules()


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if not self._route():
            super().do_GET()

    def do_HEAD(self):
        if not self._route():
            super().do_HEAD()

    def list_directory(self, path):
        self.send_error(404, "No listing")
        return None

    def _route(self):
        parts = urlsplit(self.path)
        route = parts.path or "/"
        query = ("?" + parts.query) if parts.query else ""
        for src, dest, code in RULES:
            if route != src:
                continue
            if code == 200:
                route = dest
                break
            self.send_response(code)
            self.send_header("Location", dest + query)
            self.end_headers()
            return True

        if route == "/":
            target = ROOT / "index.html"
        else:
            rel = route.lstrip("/")
            direct = ROOT / rel
            html = ROOT / (rel + ".html")
            index = ROOT / rel / "index.html"
            if direct.is_file():
                target = direct
            elif not route.endswith("/") and html.is_file():
                target = html
            elif index.is_file():
                target = index
            else:
                target = None

        if target is None:
            body = (ROOT / "404.html").read_bytes()
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
            return True

        self.path = "/" + target.relative_to(ROOT).as_posix() + query
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(ROOT)))
    print(f"Serving {ROOT} at http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
