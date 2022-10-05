import pytest
from itertools import product
from pyformlang.regular_expression import PythonRegex
from project import rpq_tensor
from project.graph_utils import build_labeled_two_cycles_graph


@pytest.fixture
def graph():
    return build_labeled_two_cycles_graph(3, 2, ("a", "b"))


def test_all_nodes_start_and_final(graph):
    actual_rpq = rpq_tensor(graph, PythonRegex("a*|b"))
    res = set(product(range(4), range(4)))

    assert actual_rpq == res.union({(0, 4), (4, 5), (5, 0)})


@pytest.mark.parametrize(
    "pattern,start_nodes,final_nodes,expected_rpq",
    [
        ("a*|b", {4}, {4, 5}, {(4, 5)}),
        ("aa", {0, 1, 2, 3}, {0, 1, 2, 3}, {(1, 3), (2, 0), (3, 1), (0, 2)}),
        ("b*", {0}, {5, 4}, {(0, 4), (0, 5)}),
    ],
)
def test_querying(graph, pattern, start_nodes, final_nodes, expected_rpq):
    actual_rpq = rpq_tensor(graph, pattern, start_nodes, final_nodes)

    assert actual_rpq == expected_rpq
