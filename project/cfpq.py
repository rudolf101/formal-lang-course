from collections import defaultdict, deque
from enum import Enum, auto
from typing import Union, Set, Any, Tuple, Collection, Dict

from networkx import MultiDiGraph
from pyformlang.cfg import CFG, Variable, Terminal, Production
from scipy.sparse import dok_matrix

from project.cfg_utils import get_cfg_from_file, cfg_to_weak_chomsky_normal_form
from project.graph_utils import load_graph

__all__ = ["cfpq", "CFPQAlgorithm"]


class CFPQAlgorithm(Enum):
    """Class represents algorithm of CFPQ

    Attributes:
        HELLINGS: Hellings algorithm
        MATRIX: Matrix algorithm
    """

    HELLINGS = auto()
    MATRIX = auto()


def cfpq(
    algorithm: CFPQAlgorithm,
    graph: Union[str, MultiDiGraph],
    cfg: Union[str, CFG],
    start_nodes: Set[Any] = None,
    final_nodes: Set[Any] = None,
    start_symbol: Variable = Variable("S"),
) -> Set[Tuple[Any, Any]]:
    """Get context-free query on graph via Hellings algo

    Args:
      algorithm(CFPQAlgorithm): Algorithm for CFPQ
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
        for (i, n, j) in {
            CFPQAlgorithm.HELLINGS: _run_hellings_algorithm,
            CFPQAlgorithm.MATRIX: _run_matrix_algorithm,
        }[algorithm](cfg, graph)
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

    wcnf = cfg_to_weak_chomsky_normal_form(cfg)
    non_term_eps, term_prods, non_term_two_prods = _convert_wcnf_prods(wcnf.productions)

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


def _run_matrix_algorithm(
    cfg: CFG, graph: MultiDiGraph
) -> Set[Tuple[Any, Variable, Any]]:
    """Runs Matrix algorithm on given CFG and graph

    Args:
      cfg(CFG): Context-free grammar
      graph(MultiDiGraph): Graph
    Returns:
      Triples of vertices with specified constraints and a non-terminal from path is derived
    """
    n = graph.number_of_nodes()
    if not n:
        return set()

    nodes = list(graph.nodes)
    node_to_idx = {node: idx for idx, node in enumerate(nodes)}

    wcnf = cfg_to_weak_chomsky_normal_form(cfg)
    eps_nonterm, term_prods, two_nonterm_prods = _convert_wcnf_prods(wcnf.productions)

    nonterm_to_mtx = {
        nonterm: dok_matrix((n, n), dtype=bool) for nonterm in wcnf.variables
    }

    for i in range(n):
        for nonterm in eps_nonterm:
            nonterm_to_mtx[nonterm][i, i] = True

    for i_node, j_node, label in graph.edges(data="label"):
        i, j = node_to_idx[i_node], node_to_idx[j_node]
        for nonterm in {
            n for n, terms in term_prods.items() if Terminal(label) in terms
        }:
            nonterm_to_mtx[nonterm][i, j] = True

    while True:
        changed = False
        for nonterm, two_nonterms in two_nonterm_prods.items():
            old_nnz = nonterm_to_mtx[nonterm].nnz
            nonterm_to_mtx[nonterm] += sum(
                nonterm_to_mtx[n1] @ nonterm_to_mtx[n2] for n1, n2 in two_nonterms
            )
            changed |= old_nnz != nonterm_to_mtx[nonterm].nnz
        if not changed:
            break

    return set(
        (nodes[i], nonterm, nodes[j])
        for nonterm, mtx in nonterm_to_mtx.items()
        for i, j in zip(*mtx.nonzero())
    )


def _convert_wcnf_prods(
    prods: Collection[Production],
) -> Tuple[
    Set[Variable],
    Dict[Variable, Set[Terminal]],
    Dict[Variable, Set[Tuple[Variable, Variable]]],
]:
    """Utility function for converting productions of context-free grammar in Weak Chomsky Normal Form

    Args:
        prods(Collection[Production]): Productions
    Returns:
        Triple of set of non-terminals that produces epsilon, mapping from non-terminal to (non)terminal that it produces
    """
    eps_nonterm = set()
    term_prods = defaultdict(set)
    two_nonterm_prods = defaultdict(set)

    for p in prods:
        head, body = p.head, p.body
        body_len = len(body)
        if body_len == 0:
            eps_nonterm.add(head)
        elif body_len == 1:
            term_prods[head].add(body[0])
        elif body_len == 2:
            two_nonterm_prods[head].add((body[0], body[1]))

    return (
        eps_nonterm,
        term_prods,
        two_nonterm_prods,
    )
