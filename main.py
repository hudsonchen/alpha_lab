from __future__ import annotations

from typing import Dict

from agent import Agent
from utils import *
from workflow import *

def main() -> None:
    # Define agents (you can add more, or swap models per-agent)
    agents: Dict[str, Agent] = {
        "strategist": Agent(
            title="Strategic Research Agent (战略)",
            expertise="research direction setting, problem framing, prioritization",
            goal="choose promising research directions with clear success criteria",
            role="strategist",
            model="gpt-4.1",
        ),
        "tactician": Agent(
            title="Tactical Exploration Agent (战术)",
            expertise="technical idea generation, derivations, experiment design",
            goal="generate concrete, testable ideas under the chosen direction",
            role="tactician",
            model="gpt-4.1-mini",
        ),
        "writer": Agent(
            title="Writer Agent",
            expertise="clear technical writing and synthesis",
            goal="produce a coherent draft from strategist+tactician outputs",
            role="writer",
            model="gpt-4.1",
        ),
        "critic": Agent(
            title="Critic Agent (Red Team)",
            expertise="critical review, finding flaws, improving rigor and clarity",
            goal="identify weaknesses and propose fixes; optionally provide revision",
            role="critic",
            model="gpt-4.1-mini",
        ),
    }

    task = (
        "Define a research agenda for next-generation generative models. "
        "Identify key limitations of current foundation models, propose promising "
        "directions for architectural, training, and objective-level innovations, "
        "and outline concrete steps for developing and evaluating these models."
    )

    results = run_workflow(task, agents)
    save_results(task, results, output_path="./results/workflow_results.txt")


if __name__ == "__main__":
    main()  