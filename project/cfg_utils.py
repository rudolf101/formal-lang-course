from collections import defaultdict
from functools import reduce
from typing import Union, IO, List

from pyformlang.cfg import CFG, Variable
from pyformlang.cfg.cfg_object import CFGObject
from pyformlang.regular_expression import Regex
from project.rsm import RSM
from project.ecfg import ECFG

__all__ = [
    "cfg_to_weak_chomsky_normal_form",
    "get_cfg_from_file",
    "cfg_to_ecfg",
    "ecfg_from_file",
    "ecfg_to_rsm",
]


def cfg_to_weak_chomsky_normal_form(cfg: CFG) -> CFG:
    """Converts CFG to Weak Chomsky Normal Form

    Args:
        cfg(CFG): Context Free Grammar
    Returns:
        Converted CFG
    """
    cfg_fixed = (
        cfg.remove_useless_symbols()
        .eliminate_unit_productions()
        .remove_useless_symbols()
    )
    return CFG(
        start_symbol=cfg_fixed.start_symbol,
        productions=set(
            cfg_fixed._decompose_productions(
                cfg_fixed._get_productions_with_only_single_terminals()
            )
        ),
    )


def get_cfg_from_file(
    file: Union[str, IO], start_symbol: Union[str, Variable] = Variable("S")
) -> CFG:
    """Loads CFG from file

    Args:
        file(Union[str, IO]): File or filename
        start_symbol(Union[str, Variable]): CFG start symbol
    Returns:
        Loaded CFG
    """
    with open(file) as f:
        return CFG.from_text(f.read(), start_symbol=start_symbol)


def cfg_to_ecfg(cfg: CFG) -> ECFG:
    """Converts CFG to ECFG

    Args:
        cfg(CFG): CFG to be converted
    Returns:
        Extended context free grammar
    """
    productions = defaultdict(list)
    for p in cfg.productions:
        productions[p.head].append(p.body)
    return ECFG(
        start_symbol=cfg.start_symbol,
        variables=cfg.variables,
        productions={
            h: reduce(Regex.union, map(concat_body, bodies))
            for h, bodies in productions.items()
        },
    )


def ecfg_from_file(
    file: Union[str, IO], start_symbol: Union[str, Variable] = Variable("S")
) -> ECFG:
    """Loads ECFG from file

    Args:
        file(Union[str, IO]): Filename or file
        start_symbol(Union[str, Variable]): The start symbol for the ECFG to be loaded
    Returns:
        Loaded ECFG
    """
    with open(file) as f:
        return ECFG.from_text(f.read(), start_symbol=start_symbol)


def ecfg_to_rsm(ecfg: ECFG) -> RSM:
    """Converts ECFG to RSM

    Args:
        ecfg(ECFG): Extended context free grammar to be converted
    Returns:
        Recursive state machine
    """
    return RSM(
        start_symbol=ecfg.start_symbol,
        boxes={
            h: r.to_epsilon_nfa().to_deterministic()
            for h, r in ecfg.productions.items()
        },
    )


def concat_body(body: List[CFGObject]) -> Regex:
    """Utility function for converting body of CFG production to regex

    Args:
        body(List[CFGObject]): Body of CFG production
    Returns:
        Regular expression
    """
    return (
        reduce(Regex.concatenate, [Regex(o.value) for o in body]) if body else Regex("")
    )
