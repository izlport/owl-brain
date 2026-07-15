"""Debug the JSON response issue."""

import json

s = """{
        "title": "Python Async/Await Best Practices",
        "category": "Python",
        "summary": "Use asyncio with async/await for concurrency. "
                   "create_task() enables parallel task execution.",
        "content": "Python's asyncio library enables concurrent code "
                   "using async/await syntax.",
        "tags": ["python", "asyncio", "concurrency"]
    }"""

print("LENGTH:", len(s))
print("REPR FIRST 300:", repr(s[:300]))

try:
    data = json.loads(s)
    print("OK:", data["title"])
except json.JSONDecodeError as e:
    print("FAIL:", e)
    print("AROUND ERROR:", repr(s[e.pos - 20 : e.pos + 20]))
