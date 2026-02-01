#!/usr/bin/env python3
import textwrap
import requests

HEADERS = {"User-Agent": "Terminal-Code-Assistant"}
WIKI_BASE = "https://en.wikipedia.org/api/rest_v1/page/summary/"

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
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        return r.json() if r.status_code == 200 else None
    except requests.RequestException:
        return None

# --- Wikipedia ---
def wiki_summary(query):
    url = WIKI_BASE + query.replace(" ", "_")
    data = get_json(url)
    return data.get("extract") if data else None

# --- DuckDuckGo fallback ---
def duckduckgo_search(query):
    """
    Uses DuckDuckGo Instant Answer API for general search.
    Returns a short snippet or None if nothing is found.
    """
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
    data = get_json(url)
    if not data:
        return None

    # Try to get a meaningful answer
    answer = data.get("AbstractText") or data.get("Answer")
    if answer:
        return answer.strip()
    
    # If AbstractText empty, try RelatedTopics
    topics = data.get("RelatedTopics", [])
    snippets = []
    for t in topics[:3]:
        text = t.get("Text")
        if text:
            snippets.append(text.strip())
    return "\n".join(snippets) if snippets else None

# --- Paragraph scoring ---
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

# --- Main prompt processor ---
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
            # If no helpful paragraphs, print whole summary
            print(wrap(wiki))
            print()
    else:
        print("No Wikipedia data found.")

    divider("DUCKDUCKGO RESULTS")
    ddg = duckduckgo_search(prompt)
    if ddg:
        print(wrap(ddg))
        print()
    else:
        print("No DuckDuckGo results found.")
