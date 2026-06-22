import re
from collections import Counter

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "with",
    "is", "are", "was", "were", "be", "been", "as", "at", "by", "it", "its",
    "this", "that", "these", "those", "from", "which", "who", "whom", "into",
}


def summarize_text(text: str, max_sentences: int = 2) -> str:
    text = " ".join(text.split())
    if not text:
        return "No content to summarize."

    sentences = re.split(r"(?<=[.!?])\s+", text)
    lead = " ".join(sentences[:max_sentences]).strip()

    words = [w.lower() for w in re.findall(r"[A-Za-z']+", text)]
    keywords = [w for w, _ in Counter(
        w for w in words if w not in _STOPWORDS and len(w) > 3
    ).most_common(5)]

    summary = lead
    if keywords:
        summary += f"\n\nKey terms: {', '.join(keywords)}."
    summary += f"\n\n(Simulated summary · {len(words)} words, {len(sentences)} sentences.)"
    return summary
