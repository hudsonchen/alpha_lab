from dataclasses import dataclass
from typing import List, Dict, Any

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from agent import Agent
from utils import *

def call_agent(
    client: OpenAI,
    agent: Agent,
    user_content: str,
    context_messages: List[ChatCompletionMessageParam] | None = None,
    temperature: float = 0.2,
) -> str:
    """
    Calls a single agent with:
      - agent.system message
      - optional context messages (e.g. outputs from previous steps)
      - the new user instruction

    Returns assistant text.
    """
    messages: List[ChatCompletionMessageParam] = [agent.message]
    if context_messages:
        messages.extend(context_messages)
    messages.append({"role": "user", "content": user_content})

    resp = client.chat.completions.create(
        model=agent.model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


def run_workflow(client: OpenAI, task: str, agents: Dict[str, Agent]) -> List[StepResult]:
    """
    4-step research workflow:
    (1) Strategy (research direction)
    (2) Tactics (concrete ideas)
    (3) Writing (synthesis)
    (4) Critique + Revision
    """
    results: List[StepResult] = []

    # 1) STRATEGY — decide research directions
    print("[1/4] Running STRATEGY step...")
    strategy = call_agent(
        client,
        agents["strategist"],
        user_content=(
            "You are a STRATEGIC research agent.\n\n"
            "Given the TASK below, propose 2–3 possible research directions.\n\n"
            "For each direction, include:\n"
            "- Core research question\n"
            "- Key assumptions\n"
            "- Success criteria\n"
            "- Minimal validation (proof sketch or experiment)\n"
            "- Main risks or failure modes\n\n"
            "Finally, recommend ONE direction and briefly justify the choice.\n\n"
            f"TASK:\n{task}"
        ),
        temperature=0.2,
    )
    results.append(StepResult(agents["strategist"], "strategy", strategy))
    print("[1/4] STRATEGY step completed.")

    print("[2/4] Running TACTICS step...")
    # 2) TACTICS — generate concrete ideas under the chosen direction
    tactics = call_agent(
        client,
        agents["tactician"],
        user_content=(
            "You are a TACTICAL research agent.\n\n"
            "Based on the STRATEGY output, focus on the RECOMMENDED direction only.\n"
            "Propose 2–4 concrete, testable idea packets.\n\n"
            "Each idea packet must include:\n"
            "- Title (one sentence)\n"
            "- Key technical ideas (2–5 bullets)\n"
            "- Sketch of derivation / algorithm / construction\n"
            "- Validation plan (theoretical or experimental)\n"
            "- Likely failure modes and mitigations\n"
            "- Next actionable steps (prioritized)\n\n"
            f"TASK:\n{task}\n\nSTRATEGY:\n{strategy}"
        ),
        temperature=0.3,
    )
    results.append(StepResult(agents["tactician"], "tactics", tactics))
    print("[2/4] TACTICS step completed.")

    print("[3/4] Running WRITING step...")
    # 3) WRITING — synthesize into a coherent draft
    draft = call_agent(
        client,
        agents["writer"],
        user_content=(
            "You are the WRITER.\n\n"
            "Synthesize the STRATEGY and TACTICS into a clear, structured research draft.\n\n"
            "Suggested structure:\n"
            "1. Motivation\n"
            "2. Problem Statement\n"
            "3. Proposed Approach\n"
            "4. Key Theoretical Ideas (if any)\n"
            "5. Experimental / Validation Plan\n"
            "6. Timeline and Risks\n\n"
            "Do NOT introduce major new claims that are unsupported by STRATEGY or TACTICS.\n"
            "Use precise technical language and clear sectioning.\n\n"
            f"TASK:\n{task}\n\nSTRATEGY:\n{strategy}\n\nTACTICS:\n{tactics}"
        ),
        temperature=0.4,
    )
    results.append(StepResult(agents["writer"], "draft", draft))
    print("[3/4] WRITING step completed.")

    print("[4/4] Running CRITIC step...")
    # 4) CRITIC — critique and revise
    revised = call_agent(
        client,
        agents["critic"],
        user_content=(
            "You are a CRITICAL reviewer (red team).\n\n"
            "First, list 5–10 concrete critiques of the DRAFT, ordered by severity.\n"
            "Each critique should explain why it matters and how it could be fixed.\n\n"
            "Then, provide a revised version of the draft that addresses the most important issues.\n\n"
            f"TASK:\n{task}\n\nDRAFT:\n{draft}"
        ),
        temperature=0.2,
    )
    results.append(StepResult(agents["critic"], "critic_and_revise", revised))
    print("[4/4] CRITIC step completed.")

    print("Workflow completed successfully.")
    return results