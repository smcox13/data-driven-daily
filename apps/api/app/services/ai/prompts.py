from __future__ import annotations


RELEVANCE_PROMPT = """
You are ranking article relevance for an executive newsletter about data analytics,
AI, martech, CRM, privacy, and direct marketing.

Return a short JSON object with:
- score: number from 0 to 1
- reason: short sentence
"""


SUMMARY_PROMPT = """
You write concise executive newsletter summaries.
For each article, produce:
- what happened
- why it matters
- business impact for marketing/data professionals
Keep the tone professional, concise, and non-hyped.
"""


TLDR_PROMPT = """
Turn the newsletter highlights into a crisp TL;DR for a time-pressed executive audience.
Keep it to 2-3 sentences.
"""


SUBJECT_PROMPT = """
Create 3-5 newsletter subject lines for an executive audience.
Blend data, curiosity, and strategic relevance without sounding like clickbait.
Return one subject per line.
"""


REPLACEMENT_PROMPT = """
Given the current newsletter context, choose the best replacement article and explain why it fits.
Return a short JSON object with:
- article_id
- reason
"""

