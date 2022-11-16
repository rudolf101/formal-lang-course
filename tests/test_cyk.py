import pytest
from pyformlang.cfg import CFG

from project.cyk import *


@pytest.mark.parametrize(
    "text_cfg, words_included, words_excluded",
    [
        (
            """
                S ->
                """,
            [""],
            ["a", "ab", "aba", "b", "ba", "bab"],
        ),
        (
            """
                S ->
                S -> a S b S
                S -> S S
                """,
            ["", "ab", "aabb", "abab"],
            ["a", "b", "aa", "bb", "abba", "baab"],
        ),
    ],
)
def test_cyk(text_cfg, words_included, words_excluded):
    cfg = CFG.from_text(text_cfg)
    assert all(cyk(s, cfg) for s in words_included)
    assert all(not cyk(s, cfg) for s in words_excluded)
