#!/usr/bin/env python3
import textwrap
import requests

MAX_SNIPPET_LINES = 20
HEADERS = {"User-Agent": "Pi-Terminal-Assistant"}

def print_panel(title):
    line = "=" * (len(title) + 8)
    print("\n" + line)
    print(f"=== {title} ===")
    print(line + "\n")

def divider(title):
    print_panel(title)

def wrap(text, width=80):
    return "\n".join(textwrap.wrap(text, width))

def get_json(url):
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else None

def get_text(url):
    r = requests.get(url, headers=HEADERS)
    return r.text if r.status_code == 200 else None

# Wikipedia summary works for any topic
def wiki_summary(query):
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")
    data = get_json(url)
    return data.get("extract") if data else None

# Score paragraphs based on query relevance
def score_paragraph(text, prompt):
    score = 0
    for term in prompt.lower().split():
        if term in text.lower():
            score += 2
    if 20 <= len(text.split()) <= 120:
        score += 1
    return score

def extract_help(text, prompt, limit=3):
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]
    scored = []
    for p in paragraphs:
        s = score_paragraph(p, prompt)
        if s > 0:
            scored.append((s, p))
    scored.sort(reverse=True)
    return [p for _, p in scored[:limit]]

# GitHub search for code (optional)
def github_search(query, results=3):
    url = f"https://api.github.com/search/code?q={query}"
    data = get_json(url)
    return (data or {}).get("items", [])[:results]

def fetch_raw(item):
    raw_url = (
        item["html_url"]
        .replace("github.com", "raw.githubusercontent.com")
        .replace("/blob/", "/")
    )
    return get_text(raw_url)

def extract_snippet(code):
    lines = []
    for line in code.splitlines():
        if line.strip() and not line.strip().startswith("#"):
            lines.append(line)
        if len(lines) >= MAX_SNIPPET_LINES:
            break
    return "\n".join(lines)

def process_prompt(prompt):
    divider("HELPFUL CONTEXT (WIKIPEDIA)")
    wiki = wiki_summary(prompt)
    if wiki:
        sections = extract_help(wiki, prompt)
        if sections:
            for s in sections:
                print(wrap(s))
                print()
        else:
            print("No clearly helpful sections found.")
    else:
        print("No Wikipedia data found. Try a more specific query.")

    divider("REAL CODE (GITHUB - optional)")
    results = github_search(prompt)
    if not results:
        print("No GitHub code found.")
        return

    for item in results:
        print(f"\n{item['repository']['full_name']}")
        raw = fetch_raw(item)
        snippet = extract_snippet(raw) if raw else None
        print("\n" + (snippet or "No usable code found") + "\n")
