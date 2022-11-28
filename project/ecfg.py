from collections import defaultdict
from functools import reduce
from typing import NamedTuple, Dict, AbstractSet, List

from pyformlang.cfg import Variable, CFG
from pyformlang.cfg.cfg_object import CFGObject
from pyformlang.regular_expression import Regex

from project.rsm import RSM

__all__ = [
    "ECFG",
]


class ECFG(NamedTuple):
    """Class represents Extended Context Free Grammar

    Attributes:
        start_symbol(Variable): Start symbol of CFG
        variables(AbstractSet[Variable]): Set of non-terminals
        productions(Dict[Variable, Regex]): Productions represented by mapping from non-terminals to regular expressions
    """

    start_symbol: Variable
    variables: AbstractSet[Variable]
    productions: Dict[Variable, Regex]

    @classmethod
    def from_text(cls, text: str, start_symbol: Variable = Variable("S")):
        """Reads ECFG from text

        Args:
            text(str): Text that contains extended context free grammar
            start_symbol(Variable): Start symbol of ECFG
        Returns:
            Obtained context free grammar
        """
        variables = set()
        prods = dict()
        for line in text.splitlines():
            if line.strip():
                data = [str.strip(e) for e in line.split("->")]
                assert len(data) == 2
                head, body = data
                head, body = Variable(head), Regex(body)
                assert head not in variables
                variables.add(head)
                prods[head] = body
        return cls(
            start_symbol=start_symbol,
            variables=variables,
            productions=prods,
        )

    @classmethod
    def from_cfg(cls, cfg: CFG) -> "ECFG":
        """Converts CFG to ECFG

        Args:
            cfg(CFG): Context free grammar to be converted
        Returns:
            Extended context free grammar
        """
        productions = defaultdict(list)
        for p in cfg.productions:
            productions[p.head].append(p.body)
        return cls(
            cfg.start_symbol,
            cfg.variables,
            {
                h: reduce(Regex.union, map(cls.concat_body, bodies))
                for h, bodies in productions.items()
            },
        )

    def to_rsm(self) -> RSM:
        """Converts ECFG to RSM

        Returns:
            Recursive state machine
        """
        return RSM(
            self.start_symbol,
            {
                h: r.to_epsilon_nfa().to_deterministic()
                for h, r in self.productions.items()
            },
        )

    @staticmethod
    def concat_body(body: List[CFGObject]) -> Regex:
        """Utility function for converting body of CFG production to regex

        Args:
            body(List[CFGObject]): Body of CFG production
        Returns:
            Regular expression
        """
        return (
            reduce(Regex.concatenate, [Regex(o.value) for o in body])
            if body
            else Regex("$")
        )
