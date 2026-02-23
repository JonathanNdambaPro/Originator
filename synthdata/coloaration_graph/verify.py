"""
Verification module for Graph Coloring Problem solutions.

This module provides the deterministic validation logic to check whether a given
color assignment for a graph satisfies all coloring constraints.
"""

from synthdata.coloaration_graph.type import Color


def verify(
    reponse_llm: dict[str, str], edges: list[tuple[str, str]], expected_nodes: list[str], allowed_colors: list[str]
) -> bool:
    """
    Verifies the correctness of a proposed graph coloring solution.

    Checks three conditions:
    1. Every node in the expected graph has been assigned a color.
    2. All assigned colors are valid choices from the allowed list.
    3. No two connected nodes share the same color.

    Args:
        reponse_llm (dict[str, str]): Dictionary mapping node IDs to their assigned color strings.
        edges (list[tuple[str, str]]): List of tuples representing the graph edges between nodes.
        expected_nodes (list[str]): List of all node IDs that must exist in the solution.
        allowed_colors (list[str]): List of valid color strings that can be used.

    Returns:
        bool: True if the graph is properly colored and valid according to constraints, False otherwise.
    """
    # 1. Verify that all nodes have been assigned a color
    if set(reponse_llm.keys()) != set(expected_nodes):
        return False

    # 2. Verify that the used colors are among the allowed colors
    # We first ensure the colors provided by the LLM match the Color Enum values
    valid_color_values = [color.value for color in Color]
    for color in reponse_llm.values():
        if color not in valid_color_values or color not in allowed_colors:
            return False

    # 3. Verify the main constraint: no edge connects two identical colors
    # get() instead of [] just in case, although step 1 handles missing keys already
    return all(reponse_llm.get(noeud_A) != reponse_llm.get(noeud_B) for noeud_A, noeud_B in edges)
