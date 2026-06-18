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
    temperature=0,
)


# ── Content extractor ─────────────────────────────────────────────────────────
def extract_text(result: dict) -> str:
    """
    Safely pull clean text out of any agent .invoke() result.

    Handles every shape create_agent / create_react_agent can return:
      • content is already a plain str          → return as-is
      • content is a list of typed blocks       → join only type=="text" entries
      • content has a .text attribute           → return that
      • anything else                           → str() fallback
    """
    # grab the last message from the result
    messages = result.get("messages", [])
    if not messages:
        return ""

    content = messages[-1].content

    # ── Case 1: plain string ──────────────────────────────────────────────────
    if isinstance(content, str):
        return content.strip()

    # ── Case 2: list of blocks  e.g. [{'type':'text','text':'...'}, ...] ──────
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
            elif hasattr(block, "text"):        # LangChain TextBlock / AIMessageChunk
                parts.append(block.text)
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts).strip()

    # ── Case 3: object with .text  ────────────────────────────────────────────
    if hasattr(content, "text"):
        return content.text.strip()

    # ── Fallback ──────────────────────────────────────────────────────────────
    return str(content).strip()


# ── Agent 1: Search ───────────────────────────────────────────────────────────
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
    )

def run_search_agent(topic: str) -> str:
    agent = build_search_agent()
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
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
    )

def run_reader_agent(search_results: str) -> str:
    agent = build_reader_agent()
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
1. Read ALL collected information carefully.
2. Merge information from every source into one coherent narrative.
3. Remove duplicate information completely.
4. Verify consistency between different sources.
5. Mention conflicting viewpoints whenever sources disagree.
6. Explain WHY something happened instead of only WHAT happened.
7. Add logical transitions between sections.
8. Expand short facts into detailed explanations.
9. Write like a professional analyst, not like an AI summary.
10. Never invent information that is absent from the research.

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
Do not write sections shorter than 300 words.
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
At least 10 insights, each 3–5 sentences explaining significance.
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
- Factual accuracy          - Completeness
- Logical organization      - Depth of analysis
- Clarity and readability   - Use of evidence and sources
- Objectivity               - Coverage of important aspects
- Unsupported claims        - Overall researcher usefulness

Be constructive, specific, and unbiased.
""",
    ),
    (
        "human",
        """
Review the following research report.

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