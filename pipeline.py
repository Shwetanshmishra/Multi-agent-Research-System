from agents import run_search_agent, run_reader_agent, writer_chain, critic_chain, revision_chain
from rich import print


def run_research_pipeline(topic: str, on_step=None) -> dict:
    """
    Runs Search -> Reader -> Writer -> Critic -> Revision.

    on_step(step_number, key, value) is called after each stage completes,
    so callers (CLI, Streamlit) can stream progress without duplicating
    the pipeline logic.
    """
    def emit(step, key, value):
        if on_step:
            on_step(step, key, value)
        return value

    state = {}

    state["search_results"] = emit(1, "search_results", run_search_agent(topic))
    state["scraped_content"] = emit(2, "scraped_content", run_reader_agent(state["search_results"]))

    research = f"""
SEARCH RESULTS
{state["search_results"]}

SCRAPED CONTENT
{state["scraped_content"]}
"""

    state["report"] = emit(3, "report", writer_chain.invoke({
        "topic": topic,
        "research": research,
    }))

    state["feedback"] = emit(4, "feedback", critic_chain.invoke({
        "research": research,
        "report": state["report"],
    }))

    state["final_report"] = emit(5, "final_report", revision_chain.invoke({
        "topic": topic,
        "research": research,
        "report": state["report"],
        "feedback": state["feedback"],
    }))

    return state


if __name__ == "__main__":
    labels = {
        1: "🔍 STEP 1 : SEARCH AGENT",
        2: "📖 STEP 2 : READER AGENT",
        3: "✍️  STEP 3 : WRITER AGENT",
        4: "🧐 STEP 4 : CRITIC AGENT",
        5: "🔁 STEP 5 : REVISION AGENT",
    }

    def cli_progress(step, key, value):
        print("\n" + "=" * 70)
        print(labels[step])
        print("=" * 70)
        print(value)

    topic = input("\nEnter research topic: ")
    run_research_pipeline(topic, on_step=cli_progress)