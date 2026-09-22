import base64
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


# ============================================================
# Configuration
# ============================================================

load_dotenv()

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"
LEETCODE_PROBLEMS_URL = "https://leetcode.com/api/problems/all/"
GITHUB_API_URL = "https://api.github.com"

LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
LEETCODE_CSRF_TOKEN = os.getenv("LEETCODE_CSRF_TOKEN")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "nikil3406/LeetCode")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

CACHE_FILE = Path(".submission_cache.json")


# ============================================================
# Validation
# ============================================================

def validate_environment():
    required = {
        "LEETCODE_SESSION": LEETCODE_SESSION,
        "LEETCODE_CSRF_TOKEN": LEETCODE_CSRF_TOKEN,
        "GITHUB_TOKEN": GITHUB_TOKEN,
        "GITHUB_REPO": GITHUB_REPO,
    }

    missing = [name for name, value in required.items() if not value]

    if missing:
        print("\nERROR: Missing environment variables:")
        for name in missing:
            print(f"  - {name}")
        print("\nCheck your .env file.")
        sys.exit(1)


# ============================================================
# LeetCode helpers
# ============================================================

def leetcode_headers():
    return {
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com/",
        "Origin": "https://leetcode.com",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/153.0.0.0 Safari/537.36"
        ),
        "x-csrftoken": LEETCODE_CSRF_TOKEN,
        "Cookie": (
            f"LEETCODE_SESSION={LEETCODE_SESSION}; "
            f"csrftoken={LEETCODE_CSRF_TOKEN}"
        ),
    }


def leetcode_graphql(query, variables=None):
    payload = {
        "query": query,
        "variables": variables or {},
    }

    response = requests.post(
        LEETCODE_GRAPHQL_URL,
        headers=leetcode_headers(),
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if data.get("errors"):
        print("\nLeetCode GraphQL error:")
        print(json.dumps(data["errors"], indent=2))
        raise RuntimeError("LeetCode GraphQL request failed.")

    return data


def get_problem_by_number(question_number):
    print(f"\nSearching LeetCode #{question_number}...")

    response = requests.get(
        LEETCODE_PROBLEMS_URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    for item in data.get("stat_status_pairs", []):
        stat = item.get("stat", {})

        if str(stat.get("frontend_question_id")) == str(question_number):
            difficulty_map = {
                1: "Easy",
                2: "Medium",
                3: "Hard",
            }

            return {
                "question_number": str(question_number),
                "title": stat.get("question__title", ""),
                "slug": stat.get("question__title_slug", ""),
                "difficulty": difficulty_map.get(
                    item.get("difficulty", {}).get("level"),
                    "Unknown",
                ),
            }

    raise RuntimeError(
        f"Could not find LeetCode problem #{question_number}"
    )


def get_question_details(slug):
    query = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionId
        questionFrontendId
        title
        titleSlug
        difficulty
        content
      }
    }
    """

    result = leetcode_graphql(
        query,
        {"titleSlug": slug},
    )

    return result.get("data", {}).get("question")


def get_all_submissions(question_slug):
    """
    Fetch all submissions visible in the user's LeetCode
    submission history for the specified question.
    """

    query = """
    query submissionList(
        $offset: Int!
        $limit: Int!
        $questionSlug: String
    ) {
      submissionList(
        offset: $offset
        limit: $limit
        questionSlug: $questionSlug
      ) {
        lastKey
        hasNext
        submissions {
          id
          title
          titleSlug
          statusDisplay
          lang
          runtime
          timestamp
          url
          memory
        }
      }
    }
    """

    submissions = []
    offset = 0
    limit = 20

    while True:
        result = leetcode_graphql(
            query,
            {
                "offset": offset,
                "limit": limit,
                "questionSlug": question_slug,
            },
        )

        submission_list = (
            result.get("data", {}).get("submissionList")
        )

        if not submission_list:
            break

        batch = submission_list.get("submissions", [])
        submissions.extend(batch)

        if not submission_list.get("hasNext") or not batch:
            break

        offset += limit

    return submissions


def get_submission_details(submission_id):
    """
    Fetch actual submitted source code and detailed metadata.
    This uses the current submissionDetails GraphQL query.
    """

    query = """
    query submissionDetails($submissionId: ID!) {
      submissionDetails(submissionIdV2: $submissionId) {
        runtime
        runtimeDisplay
        runtimePercentile
        runtimeDistribution
        memory
        memoryDisplay
        memoryPercentile
        memoryDistribution
        code
        timestamp
        statusCode
        aiJudgeMessage
        isCompiledLang
        aiRecheckSubmitted
        user {
          username
          profile {
            realName
            userAvatar
          }
        }
        lang {
          name
          verboseName
        }
        question {
          questionId
          titleSlug
          hasFrontendPreview
        }
        notes
        flagType
        topicTags {
          tagId
          slug
          name
        }
        runtimeError
        compileError
        lastTestcase
        codeOutput
        expectedOutput
        totalCorrect
        totalTestcases
        fullCodeOutput
        testDescriptions
        testBodies
        testInfo
        stdOutput
      }
    }
    """

    result = leetcode_graphql(
        query,
        {"submissionId": str(submission_id)},
    )

    details = (
        result.get("data", {}).get("submissionDetails")
    )

    if not details:
        raise RuntimeError(
            f"No submission details returned for {submission_id}"
        )

    return details


# ============================================================
# Cache helpers
# ============================================================

def load_cache():
    if not CACHE_FILE.exists():
        return {"submissions": {}}

    try:
        with CACHE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return {"submissions": {}}

        data.setdefault("submissions", {})
        return data

    except (json.JSONDecodeError, OSError):
        print("WARNING: Could not read cache. Starting a new cache.")
        return {"submissions": {}}


def save_cache(cache):
    with CACHE_FILE.open("w", encoding="utf-8") as file:
        json.dump(cache, file, indent=2, ensure_ascii=False)


# ============================================================
# GitHub helpers
# ============================================================

def github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "leetcode-to-github-archiver",
    }


def github_get_file(path):
    url = f"{GITHUB_API_URL}/repos/{GITHUB_REPO}/contents/{path}"

    response = requests.get(
        url,
        headers=github_headers(),
        params={"ref": GITHUB_BRANCH},
        timeout=30,
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()


def github_create_or_update_file(path, content, commit_message):
    url = f"{GITHUB_API_URL}/repos/{GITHUB_REPO}/contents/{path}"

    encoded = base64.b64encode(
        content.encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": commit_message,
        "content": encoded,
        "branch": GITHUB_BRANCH,
    }

    existing = github_get_file(path)

    if existing:
        payload["sha"] = existing["sha"]

    response = requests.put(
        url,
        headers=github_headers(),
        json=payload,
        timeout=30,
    )

    response.raise_for_status()
    return response.json()


# ============================================================
# Formatting helpers
# ============================================================

LANGUAGE_EXTENSIONS = {
    "python": ".py",
    "python3": ".py",
    "java": ".java",
    "cpp": ".cpp",
    "c": ".c",
    "csharp": ".cs",
    "javascript": ".js",
    "typescript": ".ts",
    "kotlin": ".kt",
    "swift": ".swift",
    "golang": ".go",
    "go": ".go",
    "rust": ".rs",
    "ruby": ".rb",
    "php": ".php",
    "scala": ".scala",
    "dart": ".dart",
    "mysql": ".sql",
    "mssql": ".sql",
    "oraclesql": ".sql",
    "postgresql": ".sql",
}


def get_extension(language):
    language = (language or "").lower().strip()
    return LANGUAGE_EXTENSIONS.get(language, ".txt")


def format_timestamp(timestamp):
    if timestamp is None or timestamp == "":
        return "Unknown"

    try:
        value = int(timestamp)
        return datetime.fromtimestamp(
            value,
            tz=timezone.utc,
        ).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (TypeError, ValueError, OSError):
        return str(timestamp)


def safe_folder_name(question_number, title):
    number = str(question_number).zfill(4)

    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        title.lower(),
    ).strip("-")

    return f"{number}-{slug}"


def strip_html(html):
    """
    Convert basic HTML from LeetCode's problem description
    into readable Markdown-ish text.
    """

    if not html:
        return ""

    text = html

    text = re.sub(
        r"<pre><code>(.*?)</code></pre>",
        lambda m: "\n```\n"
        + m.group(1)
        + "\n```\n",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"<code>(.*?)</code>",
        lambda m: "`" + m.group(1) + "`",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"<br\s*/?>",
        "\n",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"</p\s*>",
        "\n\n",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"<p\s*>",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"<li\s*>",
        "- ",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"</li\s*>",
        "\n",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"</?(ul|ol)\s*>",
        "\n",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"<strong>(.*?)</strong>",
        r"**\1**",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"<b>(.*?)</b>",
        r"**\1**",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"<em>(.*?)</em>",
        r"*\1*",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"<i>(.*?)</i>",
        r"*\1*",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"<h[1-6][^>]*>(.*?)</h[1-6]>",
        r"### \1\n",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"<img[^>]*alt=['\"]([^'\"]*)['\"][^>]*>",
        r"![\1]",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"<[^>]+>",
        "",
        text,
        flags=re.DOTALL,
    )

    replacements = {
        "&nbsp;": " ",
        "&lt;": "<",
        "&gt;": ">",
        "&amp;": "&",
        "&quot;": '"',
        "&#39;": "'",
        "&#x27;": "'",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\n[ \t]+\n", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)

    return text.strip()


# ============================================================
# Submission file
# ============================================================

def create_submission_file(submission, details):
    code = details.get("code") or ""

    language = (
        details.get("lang", {}).get("name")
        or submission.get("lang")
        or "unknown"
    )

    status = (
        submission.get("statusDisplay")
        or details.get("statusCode")
        or "Unknown"
    )

    runtime = (
        details.get("runtimeDisplay")
        or submission.get("runtime")
        or "N/A"
    )

    memory = (
        details.get("memoryDisplay")
        or submission.get("memory")
        or "N/A"
    )

    timestamp = (
        details.get("timestamp")
        or submission.get("timestamp")
    )

    submission_id = submission.get("id")

    header = (
        "# LeetCode Submission\n"
        f"# Submission ID: {submission_id}\n"
        f"# Status: {status}\n"
        f"# Language: {language}\n"
        f"# Runtime: {runtime}\n"
        f"# Memory: {memory}\n"
        f"# Submitted: {format_timestamp(timestamp)}\n"
        "#\n"
        "# This file contains the actual code submitted to LeetCode.\n"
        "#\n\n"
    )

    return header + code.rstrip() + "\n"


# ============================================================
# README
# ============================================================

def create_readme(problem, submissions):
    lines = []

    folder = safe_folder_name(
        problem["question_number"],
        problem["title"],
    )

    lines.append(
        f"# LeetCode #{problem['question_number']} - "
        f"{problem['title']}"
    )
    lines.append("")

    lines.append(f"**Difficulty:** {problem['difficulty']}")
    lines.append("")

    lines.append(
        f"**LeetCode:** "
        f"https://leetcode.com/problems/{problem['slug']}/"
    )
    lines.append("")

    # --------------------------------------------------------
    # Problem Description
    # --------------------------------------------------------

    lines.append("## Problem Description")
    lines.append("")

    description = strip_html(
        problem.get("content", "")
    )

    if description:
        lines.append(description)
    else:
        lines.append(
            "_Problem description could not be retrieved._"
        )

    lines.append("")

    # --------------------------------------------------------
    # Submission History
    # --------------------------------------------------------

    lines.append("## Submission History")
    lines.append("")

    lines.append(
        "| # | Submission ID | Status | Language | Runtime | Memory | Submitted | Code |"
    )
    lines.append(
        "|---:|---:|---|---|---|---|---|---|"
    )

    for index, item in enumerate(submissions, start=1):
        submission = item["submission"]
        details = item.get("details", {})

        submission_id = submission.get("id", "Unknown")

        status = (
            submission.get("statusDisplay")
            or details.get("statusCode")
            or "Unknown"
        )

        language = (
            details.get("lang", {}).get("name")
            or submission.get("lang")
            or "Unknown"
        )

        runtime = (
            details.get("runtimeDisplay")
            or submission.get("runtime")
            or "N/A"
        )

        memory = (
            details.get("memoryDisplay")
            or submission.get("memory")
            or "N/A"
        )

        timestamp = (
            details.get("timestamp")
            or submission.get("timestamp")
        )

        extension = get_extension(language)

        code_file = (
            f"submissions/submission-{index:03d}{extension}"
        )

        lines.append(
            f"| {index} | {submission_id} | "
            f"{status} | {language} | {runtime} | "
            f"{memory} | {format_timestamp(timestamp)} | "
            f"[Code]({code_file}) |"
        )

    lines.append("")

    # --------------------------------------------------------
    # Repository structure
    # --------------------------------------------------------

    lines.append("## Repository Structure")
    lines.append("")
    lines.append("```text")
    lines.append(f"{folder}/")
    lines.append("├── README.md")
    lines.append("└── submissions/")

    for index, item in enumerate(submissions, start=1):
        submission = item["submission"]
        details = item.get("details", {})

        language = (
            details.get("lang", {}).get("name")
            or submission.get("lang")
            or "unknown"
        )

        extension = get_extension(language)

        lines.append(
            f"    └── submission-{index:03d}{extension}"
        )

    lines.append("```")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# Main archiver
# ============================================================

def archive_problem(question_number):
    validate_environment()

    # --------------------------------------------------------
    # Problem
    # --------------------------------------------------------

    problem = get_problem_by_number(question_number)

    print(
        f"Found: {problem['question_number']}. "
        f"{problem['title']}"
    )
    print(f"Difficulty: {problem['difficulty']}")

    question_details = get_question_details(
        problem["slug"]
    )

    if question_details:
        problem["title"] = question_details.get(
            "title",
            problem["title"],
        )

        problem["content"] = question_details.get(
            "content",
            "",
        )

    # --------------------------------------------------------
    # Submissions
    # --------------------------------------------------------

    print("\nFetching your submissions...")

    submissions = get_all_submissions(
        problem["slug"]
    )

    print(
        f"Found {len(submissions)} submission(s)."
    )

    if not submissions:
        print("No submissions found.")
        return

    # --------------------------------------------------------
    # Cache
    # --------------------------------------------------------

    cache = load_cache()
    cached = cache.setdefault("submissions", {})

    folder = safe_folder_name(
        problem["question_number"],
        problem["title"],
    )

    print(f"\nGitHub folder: {folder}")

    # --------------------------------------------------------
    # Fetch details for every submission
    # --------------------------------------------------------

    submission_records = []

    for position, submission in enumerate(
        submissions,
        start=1,
    ):
        submission_id = str(
            submission.get("id", "")
        )

        if not submission_id:
            continue

        print(
            f"\n[{position}/{len(submissions)}] "
            f"Submission {submission_id}"
        )

        cached_entry = cached.get(submission_id)

        if cached_entry:
            print("  Already archived. Using cached details.")

            details = cached_entry.get(
                "details",
                {},
            )

            submission_records.append(
                {
                    "submission": submission,
                    "details": details,
                }
            )

            continue

        print("  Fetching submission code...")

        try:
            details = get_submission_details(
                submission_id
            )
        except Exception as error:
            print(
                f"  ERROR fetching submission "
                f"{submission_id}: {error}"
            )
            continue

        code = details.get("code")

        if code is None:
            print(
                "  WARNING: No source code returned. "
                "Skipping this submission."
            )
            continue

        language = (
            details.get("lang", {}).get("name")
            or submission.get("lang")
            or "unknown"
        )

        status = (
            submission.get("statusDisplay")
            or details.get("statusCode")
            or "Unknown"
        )

        print(f"  Language: {language}")
        print(f"  Status: {status}")

        # The filename is based on chronological order later.
        # For now store the record.
        submission_records.append(
            {
                "submission": submission,
                "details": details,
            }
        )

        cached[submission_id] = {
            "question_number": problem["question_number"],
            "question_slug": problem["slug"],
            "title": problem["title"],
            "details": details,
            "archived_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        save_cache(cache)

    if not submission_records:
        print("\nNo submission source code could be retrieved.")
        return

    # --------------------------------------------------------
    # Sort submissions oldest -> newest so numbering remains
    # stable.
    # --------------------------------------------------------

    submission_records.sort(
        key=lambda item: int(
            item["details"].get(
                "timestamp",
                item["submission"].get("timestamp", 0),
            )
            or 0
        )
    )

    # --------------------------------------------------------
    # Upload all missing submission files
    # --------------------------------------------------------

    print("\nChecking GitHub files...")

    for index, item in enumerate(
        submission_records,
        start=1,
    ):
        submission = item["submission"]
        details = item["details"]

        submission_id = str(
            submission.get("id")
        )

        language = (
            details.get("lang", {}).get("name")
            or submission.get("lang")
            or "unknown"
        )

        extension = get_extension(language)

        filename = (
            f"submission-{index:03d}{extension}"
        )

        github_path = (
            f"{folder}/submissions/{filename}"
        )

        # Record the final path in cache.
        if submission_id in cached:
            cached[submission_id][
                "github_path"
            ] = github_path

        existing = github_get_file(
            github_path
        )

        if existing:
            print(
                f"  ✓ Exists: {github_path}"
            )
            continue

        print(
            f"  Uploading: {github_path}"
        )

        file_content = create_submission_file(
            submission,
            details,
        )

        github_create_or_update_file(
            github_path,
            file_content,
            (
                f"Add LeetCode submission "
                f"{submission_id} for "
                f"#{problem['question_number']}"
            ),
        )

        print("  ✓ Uploaded.")

    save_cache(cache)

    # --------------------------------------------------------
    # README
    # --------------------------------------------------------

    print("\nUpdating README...")

    readme_content = create_readme(
        problem,
        submission_records,
    )

    github_create_or_update_file(
        f"{folder}/README.md",
        readme_content,
        (
            f"Update README for "
            f"LeetCode #{problem['question_number']}"
        ),
    )

    print("\n========================================")
    print("           ARCHIVING COMPLETE")
    print("========================================")
    print(
        f"Problem: #{problem['question_number']} "
        f"{problem['title']}"
    )
    print(
        f"Submissions found: {len(submissions)}"
    )
    print(
        f"Submissions processed: "
        f"{len(submission_records)}"
    )
    print(
        f"GitHub folder: {folder}"
    )
    print("========================================")


# ============================================================
# Entry point
# ============================================================

def main():
    if len(sys.argv) != 2:
        print("\nUsage:")
        print("  python leetcode_to_github.py <problem_number>")
        print("\nExample:")
        print("  python leetcode_to_github.py 1")
        sys.exit(1)

    question_number = sys.argv[1].strip()

    if not question_number.isdigit():
        print("ERROR: Problem number must be numeric.")
        sys.exit(1)

    try:
        archive_problem(question_number)

    except requests.HTTPError as error:
        print(f"\nHTTP ERROR: {error}")

        if error.response is not None:
            try:
                print(error.response.text[:3000])
            except Exception:
                pass

        sys.exit(1)

    except Exception as error:
        print(f"\nERROR: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
