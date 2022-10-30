import pytest
from pyformlang.cfg import Variable

from project import ecfg_to_rsm, generate_min_dfa_by_regex
from project.ecfg import *
from tests.utils import check_automatons_equivalent


@pytest.mark.parametrize(
    "text_cfg, prods_expected",
    [
        (
            "",
            {},
        ),
        (
            "S -> ",
            {Variable("S"): "Empty"},
        ),
        (
            "S -> a",
            {Variable("S"): "a"},
        ),
        (
            "S -> c | d | e",
            {Variable("S"): "(c|(d|e))"},
        ),
    ],
)
def test_ecfg_from_text(text_cfg, prods_expected):
    ecfg = ECFG.from_text(text_cfg)
    productions = {v: str(r) for v, r in ecfg.productions.items()}
    assert productions == prods_expected


@pytest.mark.parametrize(
    "text_ecfg",
    [
        """
        """,
        """
        S -> (a | b*)
        """,
        """
        S -> (a | (b | c)) | (d* | e)
        """,
    ],
)
def test_ecfg_to_rsm(text_ecfg):
    ecfg = ECFG.from_text(text_ecfg)
    rsm = ecfg_to_rsm(ecfg)
    assert len(ecfg.productions) == len(rsm.boxes)
    assert all(
        check_automatons_equivalent(
            generate_min_dfa_by_regex(ecfg.productions[v]),
            rsm.boxes[v].minimize(),
        )
        for v in ecfg.productions
    )
