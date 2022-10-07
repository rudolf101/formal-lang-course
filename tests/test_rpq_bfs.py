import pytest
from networkx import MultiDiGraph
from pyformlang.regular_expression import PythonRegex

from project.rpq import *


@pytest.fixture
def graph():
    graph = MultiDiGraph()
    graph.add_edge(0, 1, label="a")
    graph.add_edge(1, 2, label="b")
    graph.add_edge(2, 3, label="c")
    graph.add_edge(2, 3, label="d")
    graph.add_edge(3, 3, label="c")
    graph.add_edge(3, 3, label="d")
    return graph


def test_empty_graph():
    result = rpq_bfs(
        MultiDiGraph(),
        PythonRegex("a b"),
        RpqMode.FIND_ALL_REACHABLE,
    )
    assert not result


def test_empty_graph_separated():
    result = rpq_bfs(
        MultiDiGraph(),
        PythonRegex("a b"),
        RpqMode.FIND_REACHABLE_FOR_EACH_START_NODE,
    )
    assert not result


def test_states(graph):
    result = rpq_bfs(
        graph,
        PythonRegex("(ab)(d*)(c|d)+"),
        RpqMode.FIND_ALL_REACHABLE,
        {0},
        {3},
    )
    assert result == {3}


def test_states_separated(
    graph,
):
    result = rpq_bfs(
        graph,
        PythonRegex("(ab)(d*)(c|d)+"),
        RpqMode.FIND_REACHABLE_FOR_EACH_START_NODE,
        {0},
        {3},
    )
    assert result == {(0, 3)}


def test_by_word_separated():
    graph_by_word = MultiDiGraph()
    for i, w in enumerate("abbabbabb"):
        graph_by_word.add_edge(i, i + 1, label=w)

    result = rpq_bfs(
        graph_by_word,
        PythonRegex("(a)(bb)"),
        RpqMode.FIND_REACHABLE_FOR_EACH_START_NODE,
    )
    assert result == {(0, 3), (6, 9), (3, 6)}
