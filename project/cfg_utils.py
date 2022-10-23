from typing import Union, IO

from pyformlang.cfg import CFG, Variable

__all__ = [
    "cfg_to_weak_chomsky_normal_form",
    "get_cfg_from_file",
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
