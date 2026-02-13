from pathlib import Path
from typing import Iterable
from dataclasses import dataclass
from openai import OpenAI
from agent import Agent

@dataclass
class StepResult:
    agent: Agent
    name: str
    output: str


def save_results(task: str, results: Iterable, output_path: str | Path = "results.txt", ) -> None: 
    """ Write multi-agent workflow results to a text file. Parameters ---------- task : str
        The original task given to the workflow.
    results : Iterable
        Iterable of StepResult-like objects with attributes:
        - name (str)
        - agent.title (str)
        - output (str)
    output_path : str or Path, optional
        Path to the output file (default: "results.txt").
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        f.write("\n" + "=" * 80 + "\n")
        f.write("TASK:\n" + task + "\n")
        f.write("=" * 80 + "\n")

        for r in results:
            f.write(f"\n--- {r.name.upper()} (by {r.agent.title}) ---\n\n")
            f.write(r.output.strip() + "\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("Done.\n")
