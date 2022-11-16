from collections import defaultdict, deque
from typing import Union, Set, Any, Tuple

from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable, Terminal

from project.cfg_utils import get_cfg_from_file, cfg_to_weak_chomsky_normal_form
from project.graph_utils import load_graph

__all__ = ["cfpq"]


def cfpq(
    graph: Union[str, MultiDiGraph],
    cfg: Union[str, CFG],
    start_nodes: Set[Any] = None,
    final_nodes: Set[Any] = None,
    start_symbol: Variable = Variable("S"),
) -> Set[Tuple[Any, Any]]:
    """Get context-free query on graph via Hellings algo

    Args:
      cfg(CFG): Context-free grammar or file with it
      graph(Union[str, MultiDiGraph]): Graph or graph name from cfpq-data
      start_nodes(Set[Any]): Set of start nodes of the graph. If none then all nodes are start nodes
      final_nodes(Set[Any]): Set of final nodes of the graph. If none then all nodes are final nodes
      start_symbol(Variable): Non-terminal as start symbol in grammar

    Returns:
        Pairs of vertices between which exists specified path
    """
    if isinstance(graph, str):
        graph = load_graph(graph)
    if isinstance(cfg, str):
        cfg = get_cfg_from_file(cfg)
    cfg._start_symbol = start_symbol

    if not start_nodes:
        start_nodes = graph.nodes
    if not final_nodes:
        final_nodes = graph.nodes
    return {
        (i, j)
        for (i, n, j) in _run_hellings_algorithm(cfg, graph)
        if start_symbol == n and i in start_nodes and j in final_nodes
    }


def _run_hellings_algorithm(
    cfg: CFG, graph: MultiDiGraph
) -> Set[Tuple[Any, Variable, Any]]:
    """Runs Hellings algorithm on given context-free grammar and graph

    Args:
      cfg(CFG): Context-free grammar
      graph(MultiDiGraph): MultiDiGraph

    Returns:
      Triples of vertices between which exists specified path with a non-terminal
    """
    n = graph.number_of_nodes()
    if not n:
        return set()

    non_term_eps = set()
    term_prods = defaultdict(set)
    non_term_two_prods = defaultdict(set)

    for p in cfg_to_weak_chomsky_normal_form(cfg).productions:
        head, body = p.head, p.body
        body_len = len(body)
        if body_len == 0:
            non_term_eps.add(head)
        elif body_len == 1:
            term_prods[head].add(body[0])
        elif body_len == 2:
            non_term_two_prods[head].add((body[0], body[1]))

    by_eps = {(i, n, i) for i in graph.nodes for n in non_term_eps}
    by_term = {
        (i, n, j)
        for i, j, label in graph.edges(data="label")
        for n, terms in term_prods.items()
        if Terminal(label) in terms
    }

    result = by_eps | by_term
    result_deque = deque(result.copy())

    while result_deque:
        i, n1, j = result_deque.popleft()
        to_add = set()
        for r, n2, l in result:
            if l == i:
                for n, non_term_two in non_term_two_prods.items():
                    new = (r, n, j)
                    if (n2, n1) in non_term_two and new not in result:
                        result_deque.append(new)
                        to_add.add(new)
            if j == r:
                for n, non_term_two in non_term_two_prods.items():
                    new = (i, n, l)
                    if (n1, n2) in non_term_two and new not in result:
                        result_deque.append(new)
                        to_add.add(new)
        result |= to_add

    return result
