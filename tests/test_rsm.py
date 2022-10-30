import pytest

from project.ecfg import *
from project.cfg_utils import *
from project.rsm import *
from tests.utils import check_automatons_equivalent


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
def test_minimize_rsm(text_ecfg):
    rsm = ecfg_to_rsm(ECFG.from_text(text_ecfg))
    assert all(
        check_automatons_equivalent(
            automaton,
            automaton.minimize(),
        )
        for automaton in minimize_rsm(rsm).boxes.values()
    )
