from synthdata.coloaration_graph.type import Color
from synthdata.coloaration_graph.verify import verify

ALLOWED_COLORS = [Color.RED.value, Color.BLUE.value, Color.GREEN.value]


def test_verify_valid_coloring():
    reponse_llm = {"N0": Color.RED.value, "N1": Color.BLUE.value, "N2": Color.GREEN.value}
    edges = [("N0", "N1"), ("N1", "N2"), ("N0", "N2")]
    nodes = ["N0", "N1", "N2"]

    assert verify(reponse_llm, edges, nodes, ALLOWED_COLORS) is True


def test_verify_invalid_coloring():
    reponse_llm = {"N0": Color.RED.value, "N1": Color.RED.value, "N2": Color.GREEN.value}
    edges = [("N0", "N1"), ("N1", "N2"), ("N0", "N2")]
    nodes = ["N0", "N1", "N2"]

    assert verify(reponse_llm, edges, nodes, ALLOWED_COLORS) is False


def test_verify_empty_graph():
    reponse_llm = {}
    edges = []
    nodes = []

    assert verify(reponse_llm, edges, nodes, ALLOWED_COLORS) is True


def test_verify_no_edges():
    reponse_llm = {"N0": Color.RED.value, "N1": Color.RED.value, "N2": Color.RED.value}
    edges = []
    nodes = ["N0", "N1", "N2"]

    assert verify(reponse_llm, edges, nodes, ALLOWED_COLORS) is True


def test_verify_missing_node_in_response():
    # LLM forgets to color node N2
    reponse_llm = {"N0": Color.RED.value, "N1": Color.BLUE.value}
    edges = [("N0", "N1")]
    nodes = ["N0", "N1", "N2"]

    # Should now gracefully return False instead of crashing later
    assert verify(reponse_llm, edges, nodes, ALLOWED_COLORS) is False


def test_verify_hallucinated_node_in_response():
    # LLM hallucinates node N3
    reponse_llm = {"N0": Color.RED.value, "N1": Color.BLUE.value, "N2": Color.GREEN.value, "N3": Color.RED.value}
    edges = [("N0", "N1")]
    nodes = ["N0", "N1", "N2"]

    assert verify(reponse_llm, edges, nodes, ALLOWED_COLORS) is False


def test_verify_invalid_color_used():
    # LLM hallucinates an unauthorized color ("purple")
    # Even if "purple" is technically in the enum, we restrict it to ALLOWED_COLORS
    reponse_llm = {"N0": Color.PURPLE.value, "N1": Color.BLUE.value, "N2": Color.GREEN.value}
    edges = [("N0", "N1"), ("N1", "N2")]
    nodes = ["N0", "N1", "N2"]

    assert verify(reponse_llm, edges, nodes, ALLOWED_COLORS) is False


def test_verify_hallucinated_color():
    # LLM completely hallucinates a color that is not even in Color enum
    reponse_llm = {"N0": "magenta", "N1": Color.BLUE.value, "N2": Color.GREEN.value}
    edges = [("N0", "N1"), ("N1", "N2")]
    nodes = ["N0", "N1", "N2"]

    assert verify(reponse_llm, edges, nodes, ALLOWED_COLORS) is False
