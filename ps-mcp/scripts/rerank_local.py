# rerank_local.py - ps-mcp local re-ranker via LM Studio (OpenAI-compatible chat)
# Qwen3-Reranker served as chat model: per (query, document) pair answers yes/no;
# LM Studio (this build) has no /v1/rerank endpoint, so we drive chat completions.
# Usage:
#   py rerank_local.py --query "task profile text" --docs docs.json [--out out.json]
#                      [--model <id>] [--url http://127.0.0.1:8080] [--mode rerank|embed]
#   docs.json: {"documents": ["...", ...]}   (UTF-8; output JSON to stdout unless --out)
# exit: 0 ok | 2 server/model problem | 3 some pairs errored (scores kept, ERR marked)
import argparse
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = os.environ.get("LMSTUDIO_URL", "http://127.0.0.1:8080")
SYS = ("/no_think\n"
       "Judge whether the Document meets the requirements based on the Query and the "
       "Instruct provided. Note that the answer can only be \"yes\" or \"no\".")
INSTRUCT = ("Given the user's photo retouching / design task profile, judge whether this "
            "craft guideline is relevant and useful for executing that task.")


def api(path, payload, timeout=90):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def list_models():
    return [m.get("id", "") for m in api("/v1/models", None).get("data", [])]


def pick_model(models, keyword):
    for m in models:
        if keyword in m.lower():
            return m
    return models[0] if models else ""


def _verdict(msg):
    # this LM Studio build runs Qwen3-Reranker with thinking on: the verdict may land in
    # content (ideal) or at the head of reasoning_content (observed: "No.\n\nThe document
    # ..."). Parse both, verdict wins only if it appears in the first few words.
    for field in ("content", "reasoning_content"):
        txt = (msg.get(field) or "").strip().lower()
        if not txt:
            continue
        head = txt[:10]
        if head.startswith("yes") or head.startswith('"yes'):
            return 1.0, txt[:24]
        if head.startswith("no") or head.startswith('"no'):
            return 0.0, txt[:24]
    return -1.0, ((msg.get("content") or "") + (msg.get("reasoning_content") or ""))[:24]


def score_pair(model, query, doc):
    content = f"<Instruct>: {INSTRUCT}\n<Query>: {query}\n<Document>: {doc}"
    payload = {
        "model": model, "temperature": 0, "max_tokens": 200, "stream": False,
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": content}]}
    for attempt in (1, 2):  # observed occasional HTTP 500 under concurrency
        try:
            r = api("/v1/chat/completions", payload)
            score, raw = _verdict(r["choices"][0]["message"])
            return {"score": score, "raw": raw}
        except Exception as e:
            if attempt == 2:
                return {"score": -2.0, "raw": "ERR:" + str(e)[:80]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--docs", required=True, help="JSON file: {\"documents\": [...]}")
    ap.add_argument("--out", default="", help="optional output file (UTF-8 JSON)")
    ap.add_argument("--model", default="")
    ap.add_argument("--url", default="")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--mode", choices=["rerank", "embed"], default="rerank")
    a = ap.parse_args()
    global BASE
    if a.url:
        BASE = a.url

    try:
        models = list_models()
    except Exception as e:
        print(json.dumps({"error": f"server unreachable: {e}"}, ensure_ascii=False))
        sys.exit(2)

    docs = json.load(open(a.docs, encoding="utf-8"))["documents"]

    if a.mode == "embed":
        model = a.model or pick_model(models, "embedding")
        try:
            r = api("/v1/embeddings", {"model": model, "input": docs})
            vecs = [d["embedding"] for d in r["data"]]
            out = {"model": model, "count": len(vecs), "dims": [len(v) for v in vecs]}
            (open(a.out, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False))
             if a.out else print(json.dumps(out, ensure_ascii=False)))
            sys.exit(0)
        except Exception as e:
            print(json.dumps({"error": f"embeddings failed: {e}"}, ensure_ascii=False))
            sys.exit(2)

    model = a.model or pick_model(models, "reranker")
    if not model:
        print(json.dumps({"error": "no reranker model found"}, ensure_ascii=False))
        sys.exit(2)

    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
        results = list(ex.map(lambda d: score_pair(model, a.query, d), docs))
    errs = sum(1 for r in results if r["score"] < -1.5)
    ranked = sorted(
        ({"index": i, "doc": docs[i], **results[i]} for i in range(len(docs))),
        key=lambda x: x["score"], reverse=True)
    out = {"model": model, "query": a.query, "ranked": ranked, "errors": errs}
    if a.out:
        open(a.out, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    sys.exit(0 if errs == 0 else (0 if errs < len(docs) else 3))


if __name__ == "__main__":
    main()
