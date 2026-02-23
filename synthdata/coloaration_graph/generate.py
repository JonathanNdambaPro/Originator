"""
Generates synthetic data for Graph Coloring Problems.

This module provides a CLI to generate random, solvable graph coloring problems
using a "planted solution" approach, ensuring that all generated problems
have at least one valid solution.
"""

import json
import random
from pathlib import Path
from typing import Annotated

import typer

from synthdata.coloaration_graph.type import Color, GraphColoringProblem

# Ensure the import matches your directory structure

DATA_FOLDER = Path(__file__).parent

app = typer.Typer(help="CLI to generate graph coloring problems.")


def create_single_problem(num_nodes: int, num_colors: int, edge_probability: float) -> GraphColoringProblem:
    """
    Generates a single solvable graph coloring problem.

    Uses the 'planted solution' method by first assigning valid colors and then
    only creating edges between nodes with different colors.

    Args:
        num_nodes (int): The total number of nodes in the generated graph.
        num_colors (int): The number of allowed colors.
        edge_probability (float): The probability of creating an edge between two valid nodes.

    Returns:
        GraphColoringProblem: A Pydantic model containing nodes, edges, and valid colors.
    """
    colors = [Color.RED, Color.BLUE, Color.GREEN, Color.YELLOW, Color.PURPLE][:num_colors]
    nodes = [f"N{i}" for i in range(num_nodes)]

    # 1. Start with a valid hidden assignment (planted solution)
    golden_solution = {node: random.choice(colors) for node in nodes}  # noqa: S311

    # 2. Iteratively build up edges (constraints)
    edges = []
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            node_u = nodes[i]
            node_v = nodes[j]

            # GOLDEN RULE: We ONLY connect nodes if their secret colors are different
            if golden_solution[node_u] != golden_solution[node_v] and random.random() < edge_probability:  # noqa: S311
                edges.append((node_u, node_v))

    # We shuffle the edges so the LLM cannot guess the pattern
    random.shuffle(edges)

    return GraphColoringProblem(nodes=nodes, edges=edges, colors=colors)


@app.command()
def generate(
    num_samples: Annotated[int, typer.Option("--num-samples", help="Number of problems to generate", min=1)] = 30,
    num_nodes: Annotated[int, typer.Option("--num-nodes", help="Number of nodes in the graph", min=3)] = 12,
    num_colors: Annotated[int, typer.Option("--num-colors", help="Number of allowed colors", min=1, max=5)] = 3,
    edge_probability: Annotated[
        float, typer.Option("--edge-probability", help="Probability of an edge existing", min=0.0, max=1.0)
    ] = 0.4,
    output: Annotated[Path, typer.Option("--output", help="Output file path (default: print to stdout)")] = DATA_FOLDER,
):
    """
    Generates a synthetic dataset of graph coloring problems and exports it to JSON.

    Args:
        num_samples (int): Number of separate constraint-satisfaction problems to make.
        num_nodes (int): The total number of nodes in the generated graphs.
        num_colors (int): Allowed amount of colors to use per graph.
        edge_probability (float): Probabilistic density for edges to appear between nodes.
        output (Path): Path to output directory containing `problems.json`.
    """
    examples = []

    # We loop here (at the CLI level) to generate the requested number of problems
    for _ in range(num_samples):
        problem = create_single_problem(num_nodes=num_nodes, num_colors=num_colors, edge_probability=edge_probability)
        # We convert the Pydantic model to a dict for JSON
        examples.append(problem.model_dump())

    # JSON Formatting
    output_json = json.dumps(examples, indent=2)

    # Typer and pathlib magically handle directory creation
    output.mkdir(parents=True, exist_ok=True)
    path_json_data = output / "problems.json"
    # Write directly to the file
    path_json_data.write_text(output_json, encoding="utf-8")

    # typer.secho allows writing in color to the terminal
    typer.secho(f"✅ Generated {num_samples} problems and saved to {output}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
