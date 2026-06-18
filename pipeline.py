from agents import run_search_agent, run_reader_agent, writer_chain, critic_chain
from rich import print


def run_research_pipeline(topic: str) -> dict:

    state = {}

    print("\n" + "=" * 70)
    print("🔍 STEP 1 : SEARCH AGENT")
    print("=" * 70)

    state["search_results"] = run_search_agent(topic)
    print(state["search_results"])

    print("\n" + "=" * 70)
    print("📖 STEP 2 : READER AGENT")
    print("=" * 70)

    state["scraped_content"] = run_reader_agent(state["search_results"])
    print(state["scraped_content"])

    print("\n" + "=" * 70)
    print("✍️  STEP 3 : WRITER AGENT")
    print("=" * 70)

    research = f"""
SEARCH RESULTS
{state["search_results"]}

SCRAPED CONTENT
{state["scraped_content"]}
"""

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research,
    })
    print(state["report"])

    print("\n" + "=" * 70)
    print("🧐 STEP 4 : CRITIC AGENT")
    print("=" * 70)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"],
    })
    print(state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("\nEnter research topic: ")
    run_research_pipeline(topic)