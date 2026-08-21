from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
import os

load_dotenv()

# ── Model ─────────────────────────────────────────────────────────────────────
llm = ChatMistralAI(
    model="mistral-small-latest",
    api_key=os.getenv("MISTRAL_API_KEY"),
    temperature=0.2,
)


# ── Content extractor ─────────────────────────────────────────────────────────
def extract_text(result: dict) -> str:
    """Pull clean text out of an agent .invoke() result's last message."""
    messages = result.get("messages", [])
    if not messages:
        return ""

    content = messages[-1].content
    if isinstance(content, str):
        return content.strip()

    # list of blocks e.g. [{'type': 'text', 'text': '...'}, ...]
    parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    return "".join(parts).strip()


# ── Agent 1: Search ───────────────────────────────────────────────────────────
def run_search_agent(topic: str) -> str:
    agent = create_agent(model=llm, tools=[web_search])
    result = agent.invoke({
        "messages": [("user", f"""
Search the internet for the topic: {topic}

Find at least 5 high-quality sources.
Return for each source:
- Title
- URL
- Short Summary

Use markdown formatting.
""")]
    })
    return extract_text(result)


# ── Agent 2: Reader ───────────────────────────────────────────────────────────
def run_reader_agent(search_results: str) -> str:
    agent = create_agent(model=llm, tools=[scrape_url])
    result = agent.invoke({
        "messages": [("user", f"""
Read ALL URLs from the following search results.

Extract:
- important facts
- statistics
- examples
- expert opinions
- chronology
- technical details

Remove duplicate information.

Search Results:
{search_results}
""")]
    })
    return extract_text(result)


# ── Writer chain ──────────────────────────────────────────────────────────────
writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are the Final Research Writer Agent in an advanced Multi-Agent Research System.

Other agents have already:
- searched the internet,
- collected information from multiple websites,
- extracted webpage content,
- gathered facts and references.

Your responsibility is to transform this raw research into a publication-quality research report.

Your responsibilities:
1. Read ALL collected information carefully and write like a professional
   analyst, not an AI summary.
2. Explain WHY something happened, not just WHAT happened, and add logical
   transitions between sections.
3. Mention conflicting viewpoints whenever sources disagree.
4. Never invent information that is absent from the research. Depth should
   come from what the sources actually contain, not from padding to a length.

Your report must feel like an original research paper rather than copied notes.
""",
    ),
    (
        "human",
        """
Topic: {topic}

Collected Research: {research}

Generate a comprehensive report using the following structure.

# Background
Explain the historical context and why this topic matters.
---
# Core Analysis
Divide into multiple sections. Each section must:
- explain the concept deeply
- discuss causes and consequences
- include examples and statistics
- include expert opinions if present
- explain implications
Depth should match what the research supports — don't pad a thin section to
hit a length.
---
# Comparative Analysis
Compare viewpoints, governments, organizations or experts using Markdown tables.
---
# Timeline
Chronological timeline if the topic involves events.
---
# Geopolitical / Economic / Technical Impact
Broader implications depending on the topic.
---
# Challenges and Risks
Current limitations, risks, controversies and criticisms.
---
# Key Insights
The most significant insights from the research, each 3–5 sentences
explaining why it matters. Only as many as the research genuinely supports.
---
# Conclusion
Balanced, evidence-based conclusion.
---
# References
Every unique source listed exactly once.

Rules: proper Markdown, bullet lists, tables where helpful, no repetition,
professional language. If research is insufficient, say so — never hallucinate.
""",
    ),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# ── Critic chain ──────────────────────────────────────────────────────────────
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a senior research reviewer and quality assurance expert.

Evaluate reports with strict academic and professional standards across:
- Factual accuracy
- Completeness and coverage of important aspects
- Logical organization and depth of analysis
- Clarity and readability
- Use of evidence and sources
- Objectivity and unsupported claims

You are given the original collected research alongside the draft — use it as
the evidence boundary. A claim is "unsupported" if it isn't backed by that
research, regardless of how plausible it sounds.

Be constructive, specific, and unbiased.
""",
    ),
    (
        "human",
        """
Collected Research:
{research}

Review the following research report against the research above.

# Research Report
{report}

Evaluate using this format:

# Overall Score
Score: X/10

# Summary
Brief evaluation of overall quality.

# Strengths
- Strength 1
- Strength 2
- Strength 3

# Weaknesses
- Weakness 1
- Weakness 2
- Weakness 3

# Missing Information
Important topics, perspectives, or details that should have been included.

# Logical or Factual Issues
Inconsistencies, unsupported claims, or reasoning problems.

# Suggestions for Improvement
- Suggestion 1
- Suggestion 2
- Suggestion 3

# Final Verdict
Is the report publication-ready or does it require significant revision?
""",
    ),
])

critic_chain = critic_prompt | llm | StrOutputParser()


# ── Revision chain ────────────────────────────────────────────────────────────
revision_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are the Revision Writer Agent in a Multi-Agent Research System.

You receive a draft report, the original research it was based on, and a
critic's review of the draft. Your job is to produce the final, improved
report.

Rules:
1. Address every weakness, missing item, and suggestion the critic raised.
2. Only use facts present in the original research — never invent new
   statistics, examples, or sources to satisfy the critic.
3. If the critic flagged missing information the research doesn't contain,
   note the gap explicitly instead of fabricating a fix.
4. Preserve the report's overall section structure unless the critic
   specifically flagged the structure itself.
5. Output only the final revised report — no commentary about what changed.
""",
    ),
    (
        "human",
        """
Topic: {topic}

Original Research:
{research}

Draft Report:
{report}

Critic Feedback:
{feedback}

Produce the final, revised report.
""",
    ),
])

revision_chain = revision_prompt | llm | StrOutputParser()