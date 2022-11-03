from typing import NamedTuple, Dict, AbstractSet

from pyformlang.cfg import Variable
from pyformlang.regular_expression import Regex

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
