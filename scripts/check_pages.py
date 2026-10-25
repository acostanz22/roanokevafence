import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
htmls = [
    p for p in root.rglob("*.html")
    if ".audit" not in p.parts and "scripts" not in p.parts
]
print("pages", len(htmls))
missing = []
bad_json = []
multi_h1 = []
for p in htmls:
    text = p.read_text(encoding="utf-8")
    urls = re.findall(r'(?:src|href)="([^"]+)"', text)
    for u in urls:
        if u.startswith(("http", "tel:", "mailto:", "#", "data:")):
            continue
        path = u.split("#")[0].split("?")[0]
        if path in ("", "/"):
            continue
        rel = path.lstrip("/")
        target = root / rel
        ok = target.exists() or (root / rel / "index.html").exists()
        if not ok:
            missing.append((str(p.relative_to(root)), u))
    h1 = len(re.findall(r"<h1[\s>]", text))
    if h1 != 1:
        multi_h1.append((str(p.relative_to(root)), h1))
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
    if not m:
        bad_json.append((str(p.relative_to(root)), "no json"))
    else:
        try:
            json.loads(m.group(1))
        except Exception as e:
            bad_json.append((str(p.relative_to(root)), str(e)[:160]))
    if "<html" not in text or "</html>" not in text:
        print("incomplete", p.relative_to(root))

print("MISSING", len(missing))
for item in missing:
    print(" ", item)
print("H1", multi_h1)
print("JSON", bad_json)
