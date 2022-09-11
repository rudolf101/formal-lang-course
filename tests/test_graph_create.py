import cfpq_data
import networkx

from project import build_labeled_two_cycles_graph


def test_build_labeled_two_cycles_graph():
    expected_graph = cfpq_data.labeled_two_cycles_graph(21, 22, labels=("a", "y"))
    actual_graph = build_labeled_two_cycles_graph(21, 22, ("y", "a"))
    assert networkx.isomorphism.is_isomorphic(actual_graph, expected_graph)
