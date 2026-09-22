import base64
import html
import os
import re
from datetime import datetime, timezone
from typing import Any

import requests
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai

GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "nikil3406/LeetCode")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
ARCHIVE_WEBHOOK_TOKEN = os.getenv("ARCHIVE_WEBHOOK_TOKEN")

app = FastAPI(title="LeetCode Auto Archive API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

def authenticate(token: str | None):
    required = {
        "GITHUB_TOKEN": GITHUB_TOKEN,
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "ARCHIVE_WEBHOOK_TOKEN": ARCHIVE_WEBHOOK_TOKEN,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise HTTPException(500, f"Missing server configuration: {', '.join(missing)}")
    if token != ARCHIVE_WEBHOOK_TOKEN:
        raise HTTPException(401, "Invalid archive token.")

def strip_html(value: str) -> str:
    if not value:
        return ""
    text = value
    text = re.sub(r"<pre><code>(.*?)</code></pre>",
                  lambda m: "\n```\n" + html.unescape(m.group(1)) + "\n```\n",
                  text, flags=re.S | re.I)
    text = re.sub(r"<code>(.*?)</code>",
                  lambda m: "`" + html.unescape(m.group(1)) + "`",
                  text, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.I)
    text = re.sub(r"<p\s*>", "", text, flags=re.I)
    text = re.sub(r"<li\s*>", "- ", text, flags=re.I)
    text = re.sub(r"</li\s*>", "\n", text, flags=re.I)
    text = re.sub(r"</?(ul|ol)\s*>", "\n", text, flags=re.I)
    text = re.sub(r"<strong>(.*?)</strong>", r"**\1**", text, flags=re.S | re.I)
    text = re.sub(r"<b>(.*?)</b>", r"**\1**", text, flags=re.S | re.I)
    text = re.sub(r"<em>(.*?)</em>", r"*\1*", text, flags=re.S | re.I)
    text = re.sub(r"<i>(.*?)</i>", r"*\1*", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "", text, flags=re.S)
    for old, new in {
        "&nbsp;": " ", "&lt;": "<", "&gt;": ">", "&amp;": "&",
        "&quot;": '"', "&#39;": "'", "&#x27;": "'"
    }.items():
        text = text.replace(old, new)
    return re.sub(r"\n[ \t]+\n", "\n\n", text).strip()

def generate_explanation(problem: dict, submission: dict, details: dict) -> str:
    code = details.get("code") or ""
    language = details.get("lang", {}).get("name") or submission.get("lang") or "unknown"
    prompt = f"""You are explaining a student's actual LeetCode submission.

Analyze the submitted code exactly as written.
- Do NOT rewrite or replace the code.
- Do NOT invent an algorithm the code does not use.
- Explain the actual algorithm and data structures.
- If inefficient, explain what it actually does.
- Keep it concise and technically accurate.
- Do not use Markdown code fences.

Return exactly:
INTUITION
2-5 sentences about this exact solution.

APPROACH
Numbered steps describing the submitted code.

WHY IT WORKS
Why the algorithm produces the required result.

COMPLEXITY
Time and space complexity with a brief explanation.

Problem:
{problem.get("title", "")}

Problem description:
{strip_html(problem.get("content", ""))}

Language:
{language}

Actual submitted code:
{code}
"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    text = (getattr(response, "text", None) or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty explanation.")
    return text

EXTENSIONS = {
    "python": ".py", "python3": ".py", "java": ".java", "cpp": ".cpp",
    "c": ".c", "csharp": ".cs", "javascript": ".js", "typescript": ".ts",
    "kotlin": ".kt", "swift": ".swift", "golang": ".go", "go": ".go",
    "rust": ".rs", "ruby": ".rb", "php": ".php", "scala": ".scala",
    "dart": ".dart", "mysql": ".sql", "mssql": ".sql",
    "oraclesql": ".sql", "postgresql": ".sql", "sql": ".sql"
}

def extension(language):
    return EXTENSIONS.get((language or "").lower().strip(), ".txt")

def comment(text: str, language: str) -> str:
    lang = (language or "").lower()
    if lang in {"python", "python3", "ruby", "bash", "shell", "perl"}:
        return "\n".join("# " + x if x else "#" for x in text.splitlines())
    if lang in {"mysql", "mssql", "oraclesql", "postgresql", "sql"}:
        return "\n".join("-- " + x if x else "--" for x in text.splitlines())
    return "/*\n" + "\n".join(" * " + x if x else " *" for x in text.splitlines()) + "\n */"

def timestamp(value: Any) -> str:
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (TypeError, ValueError, OSError):
        return str(value) if value not in (None, "") else "Unknown"

def submission_file(sub: dict, details: dict, explanation: str) -> str:
    code = details.get("code") or ""
    language = details.get("lang", {}).get("name") or sub.get("lang") or "unknown"
    meta = "\n".join([
        "LeetCode Submission",
        f"Submission ID: {sub.get('id')}",
        f"Status: {sub.get('statusDisplay') or details.get('statusCode') or 'Unknown'}",
        f"Language: {language}",
        f"Runtime: {details.get('runtimeDisplay') or sub.get('runtime') or 'N/A'}",
        f"Memory: {details.get('memoryDisplay') or sub.get('memory') or 'N/A'}",
        f"Submitted: {timestamp(details.get('timestamp') or sub.get('timestamp'))}",
    ])
    if (language or "").lower() in {"python", "python3", "ruby", "bash", "shell", "perl"}:
        meta_block = "\n".join("# " + x for x in meta.splitlines())
    elif (language or "").lower() in {"mysql", "mssql", "oraclesql", "postgresql", "sql"}:
        meta_block = "\n".join("-- " + x for x in meta.splitlines())
    else:
        meta_block = "/*\n" + "\n".join(" * " + x for x in meta.splitlines()) + "\n */"
    return meta_block + "\n" + comment(explanation, language) + "\n\n" + code.rstrip() + "\n"

def folder(number: str, title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"{str(number).zfill(4)}-{slug}"

def gh_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "leetcode-auto-archive-api",
    }

def gh_get(path: str):
    r = requests.get(
        f"{GITHUB_API_URL}/repos/{GITHUB_REPO}/contents/{path}",
        headers=gh_headers(), params={"ref": GITHUB_BRANCH}, timeout=30
    )
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()

def gh_text(path: str):
    item = gh_get(path)
    if not item or not item.get("content"):
        return None
    return base64.b64decode(item["content"].replace("\n", "")).decode("utf-8")

def gh_put(path: str, content: str, message: str):
    existing = gh_get(path)
    if existing and gh_text(path) == content:
        return "unchanged"
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": GITHUB_BRANCH,
    }
    if existing:
        payload["sha"] = existing["sha"]
    r = requests.put(
        f"{GITHUB_API_URL}/repos/{GITHUB_REPO}/contents/{path}",
        headers=gh_headers(), json=payload, timeout=30
    )
    r.raise_for_status()
    return "updated" if existing else "created"

def readme(problem: dict, submissions: list[dict]) -> str:
    number, title = str(problem["question_number"]), problem["title"]
    lines = [
        f"# LeetCode #{number} - {title}", "",
        f"**Difficulty:** {problem.get('difficulty', 'Unknown')}", "",
        f"**LeetCode:** https://leetcode.com/problems/{problem['slug']}/", "",
        "## Problem Description", "",
        strip_html(problem.get("content", "")) or "_Problem description could not be retrieved._", "",
        "## Submission History", "",
        "| # | Submission ID | Status | Language | Runtime | Memory | Submitted | Code |",
        "|---:|---:|---|---|---|---|---|---|"
    ]
    for i, s in enumerate(submissions, 1):
        ext = extension(s.get("lang"))
        lines.append(
            f"| {i} | {s.get('id', 'Unknown')} | {s.get('statusDisplay', 'Unknown')} | "
            f"{s.get('lang', 'Unknown')} | {s.get('runtime', 'N/A')} | {s.get('memory', 'N/A')} | "
            f"{timestamp(s.get('timestamp'))} | [Code](submissions/submission-{i:03d}{ext}) |"
        )
    lines += ["", "## Repository Structure", "", "```text",
              f"{folder(number, title)}/", "├── README.md", "└── submissions/"]
    for i, s in enumerate(submissions, 1):
        lines.append(f"    └── submission-{i:03d}{extension(s.get('lang'))}")
    lines += ["```", ""]
    return "\n".join(lines)

@app.get("/")
def root():
    return {"service": "leetcode-auto-archive", "status": "ok", "model": GEMINI_MODEL}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/archive-submission")
def archive(payload: dict, x_archive_token: str | None = Header(default=None)):
    authenticate(x_archive_token)

    problem = payload.get("problem")
    current = payload.get("submission")
    details = payload.get("details")
    all_submissions = payload.get("all_submissions")

    if not all(isinstance(x, dict) for x in [problem, current, details]) or not isinstance(all_submissions, list):
        raise HTTPException(400, "problem, submission, details and all_submissions are required.")

    number = str(problem.get("question_number") or "")
    title = str(problem.get("title") or "")
    slug = str(problem.get("slug") or "")
    if not number or not title or not slug:
        raise HTTPException(400, "Incomplete problem metadata.")

    ordered = sorted(all_submissions, key=lambda x: int(x.get("timestamp") or 0))
    sid = str(current.get("id"))
    matching = next((x for x in ordered if str(x.get("id")) == sid), current)
    index = next((i for i, x in enumerate(ordered, 1) if str(x.get("id")) == sid), len(ordered))

    explanation = generate_explanation(problem, matching, details)
    lang = details.get("lang", {}).get("name") or matching.get("lang") or "unknown"
    path = f"{folder(number, title)}/submissions/submission-{index:03d}{extension(lang)}"

    file_result = gh_put(
        path,
        submission_file(matching, details, explanation),
        f"Archive LeetCode submission {sid} for #{number}"
    )
    readme_result = gh_put(
        f"{folder(number, title)}/README.md",
        readme(problem, ordered),
        f"Update README for LeetCode #{number}"
    )

    return {
        "ok": True,
        "submission_id": sid,
        "problem": f"#{number} {title}",
        "github_path": path,
        "file_result": file_result,
        "readme_result": readme_result,
        "gemini_model": GEMINI_MODEL,
    }
