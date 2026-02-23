"""
Data models and types for the Graph Coloring Problem.

Defines Pydantic models for structured validation of inputs, LLM outputs,
and graph representations to ensure type safety across the application.
"""

from enum import StrEnum, auto

from pydantic import BaseModel, Field


class Color(StrEnum):
    """
    Enumeration of allowed colors for the graph nodes.
    """

    RED = auto()
    BLUE = auto()
    GREEN = auto()
    YELLOW = auto()
    PURPLE = auto()


class Node(BaseModel):
    """
    Represents a single node in the graph.
    """

    node: str = Field(..., pattern=r"^N\d+$")


class GraphColoringProblem(BaseModel):
    """
    Structured definition of a complete graph coloring problem.
    """

    nodes: list[str]
    edges: list[tuple[str, str]]
    colors: list[Color]


class NodeColorMapping(BaseModel):
    """
    Represents an assignment of a specific color to a specific node.
    """

    node: str
    color: Color


class OutputExpectedGraph(BaseModel):
    """
    The strictly formatted JSON output expected from the LLM solution.
    """

    solution: list[NodeColorMapping] = Field(
        ..., description="List associating each node with its color (e.g., [{'node': 'N0', 'color': 'Red'}, ...])."
    )
