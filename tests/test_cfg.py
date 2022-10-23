import pytest
from pyformlang.cfg import Production, Variable, Terminal, CFG

from project.cfg_utils import *


@pytest.mark.parametrize(
    "text_cfg, expected_productions",
    [
        ("A -> a", {Production(Variable("A"), [Terminal("a")])}),
        (
            """
                S -> T
                T -> t
                """,
            {
                Production(Variable("S"), [Variable("T")]),
                Production(Variable("T"), [Terminal("t")]),
            },
        ),
        (
            """
                S -> epsilon
                S -> a S b S
                S -> S S
                """,
            {
                Production(Variable("S"), []),
                Production(
                    Variable("S"),
                    [Terminal("a"), Variable("S"), Terminal("b"), Variable("S")],
                ),
                Production(Variable("S"), [Variable("S"), Variable("S")]),
            },
        ),
    ],
)
def test_get_cfg_from_file(tmpdir, text_cfg, expected_productions):
    file = tmpdir.mkdir("test_dir").join("cfg_file")
    file.write(text_cfg)
    cfg = get_cfg_from_file(file)
    assert cfg.productions == expected_productions


@pytest.mark.parametrize(
    "text_cfg, expected_productions",
    [
        ("B -> a", set()),
        (
            """
                S -> T
                T -> t
                """,
            {Production(Variable("S"), [Terminal("t")])},
        ),
        (
            """
                S ->
                S -> a S b S
                S -> S S
                """,
            {
                Production(Variable("S"), []),
                Production(Variable("S"), [Variable("a#CNF#"), Variable("C#CNF#1")]),
                Production(Variable("a#CNF#"), [Terminal("a")]),
                Production(Variable("b#CNF#"), [Terminal("b")]),
                Production(Variable("C#CNF#1"), [Variable("S"), Variable("C#CNF#2")]),
                Production(Variable("C#CNF#2"), [Variable("b#CNF#"), Variable("S")]),
                Production(Variable("S"), [Variable("S"), Variable("S")]),
            },
        ),
    ],
)
def test_cfg_convert_to_wcnf(text_cfg, expected_productions):
    cfg_wcnf = cfg_to_weak_chomsky_normal_form(CFG.from_text(text_cfg))
    assert cfg_wcnf.productions == expected_productions
