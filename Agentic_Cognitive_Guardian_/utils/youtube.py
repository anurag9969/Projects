import requests
import urllib.parse
import re
import html as html_parser
import math
from functools import lru_cache

from sentence_transformers import SentenceTransformer, util
from agents.llm_client import call_llm


# ============================================================
# MODEL (CACHED)
# ============================================================
@lru_cache(maxsize=1)
def get_embedder():
    print("🧠 Loading semantic embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ Semantic model loaded")
    return model


EMBEDDER = get_embedder()
HEADERS = {"User-Agent": "Mozilla/5.0"}


# ============================================================
# EMBEDDING CACHE (MAJOR SPEED BOOST)
# ============================================================
@lru_cache(maxsize=4096)
def embed_text(text: str):
    return EMBEDDER.encode(text, convert_to_tensor=True)


# ============================================================
# TEXT HELPERS
# ============================================================
def clean_text(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text.lower())
    return " ".join(text.split())


# ============================================================
# FAST INTENT NORMALIZATION (NO LLM)
# ============================================================
def extract_core_intent(query: str) -> str:
    q = query.lower()

    if "not improving" in q or "stuck" in q or "plateau" in q:
        return "skill improvement plateau how to get better"

    if "interview" in q and ("fear" in q or "anxiety" in q):
        return "interview anxiety how to prepare calmly"

    if "job" in q and "gap" in q:
        return "explain career gap in interviews"

    if "burnout" in q or "burnt out" in q:
        return "burnout recovery motivation focus"

    return query


# ============================================================
# YOUTUBE SCRAPING (ROBUST)
# ============================================================
def fetch_candidates(query: str, limit=30):
    encoded = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"

    try:
        html = requests.get(url, headers=HEADERS, timeout=8).text
    except Exception as e:
        print("❌ YouTube fetch failed:", e)
        return []

    video_ids = []
    for m in re.finditer(r'"videoId":"([a-zA-Z0-9_-]{11})"', html):
        vid = m.group(1)
        if vid not in video_ids:
            video_ids.append(vid)

    raw_titles = re.findall(
        r'"title":\{"runs":\[\{"text":"(.*?)"\}\]',
        html
    )

    results = []
    for vid, title in zip(video_ids, raw_titles):
        title = title.encode("utf-8").decode("unicode_escape")
        title = html_parser.unescape(title).strip()

        if len(title) < 6:
            continue
        if any(x in title.lower() for x in ["shorts", "trailer", "edit"]):
            continue

        results.append({
            "video_id": vid,
            "title": title,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
        })

        if len(results) >= limit:
            break

    print(f"🎥 Extracted {len(results)} videos for query: {query}")
    return results


# ============================================================
# SEMANTIC RECALL (HIGH RECALL)
# ============================================================
def semantic_recall(query, candidates, top_k=15):
    if not candidates:
        return []

    intent = extract_core_intent(query)
    q_emb = embed_text(clean_text(intent))

    scored = []
    for c in candidates:
        t_clean = clean_text(c["title"])
        t_emb = embed_text(t_clean)
        sim = float(util.cos_sim(q_emb, t_emb))

        scored.append({
            **c,
            "semantic_score": sim
        })

    scored.sort(key=lambda x: x["semantic_score"], reverse=True)
    return scored[:top_k]


# ============================================================
# PRECISION RERANK (NON-LINEAR CONFIDENCE)
# ============================================================
def semantic_rerank(query, recalled):
    refined = []

    q_tokens = set(clean_text(query).split())

    for item in recalled:
        t_clean = clean_text(item["title"])
        t_tokens = set(t_clean.split())

        semantic = item["semantic_score"]
        overlap = len(q_tokens & t_tokens) / max(len(q_tokens), 1)

        combined = semantic * 0.75 + overlap * 0.25

        # 🔥 Non-linear confidence curve
        confidence = 1 - math.exp(-3 * combined)
        percent = int(min(max(confidence * 100, 30), 98))

        # Penalize clickbait
        if any(x in item["title"].lower()
               for x in ["shocking", "secret", "must watch"]):
            percent -= 10

        percent = max(25, min(percent, 98))

        refined.append({
            **item,
            "match_percent": percent
        })

    refined.sort(key=lambda x: x["match_percent"], reverse=True)
    return refined


# ============================================================
# LLM VERIFICATION (BOOST ONLY, TOP N)
# ============================================================
VIDEO_RELEVANCE_PROMPT = """
Judge if this video meaningfully helps the user's problem.

User problem:
"{problem}"

Video title:
"{title}"

Answer ONLY one:
EXACT_MATCH
STRONG_MATCH
PARTIAL_MATCH
NOT_RELEVANT
"""

def llm_verify_video(problem: str, title: str) -> int:
    result = call_llm(
        system_prompt=VIDEO_RELEVANCE_PROMPT.format(
            problem=problem,
            title=title
        ),
        user_prompt=""
    )

    if not isinstance(result, str):
        return 0

    verdict = result.strip()

    return {
        "EXACT_MATCH": 95,
        "STRONG_MATCH": 85,
        "PARTIAL_MATCH": 65,
        "NOT_RELEVANT": 0
    }.get(verdict, 0)


# ============================================================
# PUBLIC API — FAST + RELIABLE
# ============================================================
def search_youtube_semantic(query, max_results=5):
    candidates = fetch_candidates(query)

    if not candidates:
        return []

    recalled = semantic_recall(query, candidates)
    reranked = semantic_rerank(query, recalled)

    # 🔥 LLM verification only for top 4 (speed!)
    for v in reranked[:4]:
        llm_score = llm_verify_video(query, v["title"])
        if llm_score > v["match_percent"]:
            v["match_percent"] = llm_score

    reranked.sort(key=lambda x: x["match_percent"], reverse=True)

    for v in reranked[:max_results]:
        print(f"YT MATCH {v['match_percent']}% | {v['title']}")

    return reranked[:max_results]
