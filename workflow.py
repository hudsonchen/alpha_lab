from pathlib import Path
from typing import List, Dict

from openai import OpenAI
from agent import Agent
from run_meeting import run_meeting
from utils import *


def run_workflow(client: OpenAI, task: str, agents: Dict[str, Agent]) -> List[StepResult]:
    """
    4-step research workflow:
    (1) Strategy (research direction)
    (2) Tactics (concrete ideas)
    (3) Writing (synthesis)
    (4) Critique + Revision
    """
    results: List[StepResult] = []

    meetings_dir = Path("./results/meetings")

    # 1) STRATEGY — team meeting to decide research directions
    print("[1/4] Running STRATEGY step...")
    strategy = run_meeting(
        meeting_type="team",
        agenda=task,
        save_dir=meetings_dir,
        save_name="01_strategy",
        client=client,
        team_lead=agents["strategist"],
        team_members=(agents["tactician"], agents["writer"], agents["critic"]),
        agenda_questions=(
            "Propose 2-3 possible research directions.",
            "For each direction, specify core research question, key assumptions, success criteria, minimal validation plan, and main risks or failure modes.",
            "Recommend one direction and briefly justify the choice.",
        ),
        num_rounds=1,
        return_summary=True,
    )
    strategy = strategy or ""
    results.append(StepResult(agents["strategist"], "strategy", strategy))
    print("[1/4] STRATEGY step completed.")

    print("[2/4] Running TACTICS step...")
    # 2) TACTICS — team meeting to generate concrete ideas under chosen direction
    tactics = run_meeting(
        meeting_type="team",
        agenda=task,
        save_dir=meetings_dir,
        save_name="02_tactics",
        client=client,
        team_lead=agents["tactician"],
        team_members=(agents["strategist"], agents["writer"], agents["critic"]),
        summaries=(strategy,),
        agenda_questions=(
            "Focus on the recommended strategy direction only.",
            "Propose 2-4 concrete, testable idea packets.",
            "For each idea packet, include title, key technical ideas, derivation/algorithm sketch, validation plan, likely failure modes with mitigations, and prioritized next actionable steps.",
        ),
        num_rounds=1,
        return_summary=True,
    )
    tactics = tactics or ""
    results.append(StepResult(agents["tactician"], "tactics", tactics))
    print("[2/4] TACTICS step completed.")

    print("[3/4] Running WRITING step...")
    # 3) WRITING — team meeting to synthesize into a coherent draft
    draft = run_meeting(
        meeting_type="team",
        agenda=task,
        save_dir=meetings_dir,
        save_name="03_draft",
        client=client,
        team_lead=agents["writer"],
        team_members=(agents["strategist"], agents["tactician"], agents["critic"]),
        summaries=(strategy, tactics),
        agenda_questions=(
            "Synthesize strategy and tactics into a clear, structured research draft.",
            "Use this structure: Motivation; Problem Statement; Proposed Approach; Key Theoretical Ideas (if any); Experimental/Validation Plan; Timeline and Risks.",
            "Do not introduce major unsupported claims beyond the provided summaries.",
        ),
        num_rounds=1,
        return_summary=True,
    )
    draft = draft or ""
    results.append(StepResult(agents["writer"], "draft", draft))
    print("[3/4] WRITING step completed.")

    print("[4/4] Running CRITIC step...")
    # 4) CRITIC — team meeting to critique and revise
    revised = run_meeting(
        meeting_type="team",
        agenda=task,
        save_dir=meetings_dir,
        save_name="04_critic_and_revise",
        client=client,
        team_lead=agents["critic"],
        team_members=(agents["strategist"], agents["tactician"], agents["writer"]),
        summaries=(strategy, tactics, draft),
        agenda_questions=(
            "List 5-10 concrete critiques of the draft, ordered by severity.",
            "For each critique, explain why it matters and how it can be fixed.",
            "Provide a revised version of the draft that addresses the most important issues.",
        ),
        num_rounds=1,
        return_summary=True,
    )
    revised = revised or ""
    results.append(StepResult(agents["critic"], "critic_and_revise", revised))
    print("[4/4] CRITIC step completed.")

    print("Workflow completed successfully.")
    return results