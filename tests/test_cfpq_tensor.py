import pytest

from networkx import MultiDiGraph
from pyformlang.cfg import CFG

from project.graph_utils import *
from project.cfpq import *


@pytest.mark.parametrize(
    "text_cfg, graph, pairs",
    [
        (
            """
            """,
            MultiDiGraph(),
            set(),
        ),
        (
            """
            S -> a b
            S -> a S b
            """,
            build_labeled_two_cycles_graph(1, 1, ("a", "b")),
            {(1, 2), (0, 0)},
        ),
        (
            """
            S ->
            S -> a S b S
            S -> S S
            """,
            build_labeled_two_cycles_graph(1, 1, ("a", "b")),
            {(1, 1), (1, 2), (2, 2), (0, 0)},
        ),
        (
            """
            S -> b
            S -> b S
            """,
            build_labeled_two_cycles_graph(1, 1, ("a", "b")),
            {(0, 0), (0, 2), (2, 0), (2, 2)},
        ),
    ],
)
def test_cfpq(text_cfg, graph, pairs):
    assert cfpq(CFPQAlgorithm.TENSOR, graph, CFG.from_text(text_cfg)) == pairs
