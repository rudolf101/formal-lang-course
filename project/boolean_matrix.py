from typing import Set, Any, Dict

from pyformlang.finite_automaton import State, EpsilonNFA
from scipy import sparse

__all__ = ["BooleanMatrix"]

from scipy.sparse import dok_matrix


class BooleanMatrix:
    """Class representing boolean adjacency matrices of NFA

    Attributes:
        states_count(int): Count of states
        states_indices(Dict[State, int]): Dictionary of states to indices in boolean matrix
        start_states(Set[State]): NFA start states
        final_states(Set[State]): NFA final states
        bool_matrices(Dict[Any, dok_matrix]): Mapping each edge label to boolean adjacency matrix
    """

    def __init__(self):
        self.states_count = 0
        self.states_indices = dict()
        self.start_states = set()
        self.final_states = set()
        self.bool_matrices = dict()

    def to_nfa(self) -> EpsilonNFA:
        """Converts boolean adjacency matrices of NFA to epsilon nfa

        Returns:
            Converted NFA
        """
        nfa = EpsilonNFA()
        for label, matrix in self.bool_matrices.items():
            for state_from, state_to in zip(*matrix.nonzero()):
                nfa.add_transition(state_from, label, state_to)

        for state in map(State, self.start_states):
            nfa.add_start_state(state)
        for state in map(State, self.final_states):
            nfa.add_final_state(state)

        return nfa

    def get_start_states(self) -> Set[State]:
        return self.start_states.copy()

    def get_final_states(self) -> Set[State]:
        return self.final_states.copy()

    def get_transitive_closure(self) -> dok_matrix:
        """Calculates transitive closure

        Returns:
            Transitive closure represented by sparse matrix
        """
        transitive_closure = sum(self.bool_matrices.values())
        cur_nnz = transitive_closure.nnz
        prev_nnz = None

        while prev_nnz != cur_nnz:
            transitive_closure += transitive_closure @ transitive_closure
            prev_nnz, cur_nnz = cur_nnz, transitive_closure.nnz

        return transitive_closure

    def intersect(self, other: "BooleanMatrix") -> "BooleanMatrix":
        """Calculates intersection of self boolean matrix with other

        Args:
            other(BooleanMatrix): The automaton with which intersection needs to calculate

        Returns:
            Intersection of two automatons as boolean matrix
        """
        boolean_matrix_result = BooleanMatrix()
        boolean_matrix_result.states_count = self.states_count * other.states_count
        inter_labels = self.bool_matrices.keys() & other.bool_matrices.keys()

        boolean_matrix_result.bool_matrices = {
            label: sparse.kron(self.bool_matrices[label], other.bool_matrices[label])
            for label in inter_labels
        }

        for self_state, self_index in self.states_indices.items():
            for other_state, other_index in other.states_indices.items():
                new_state = new_state_idx = (
                    self_index * other.states_count + other_index
                )
                boolean_matrix_result.states_indices[new_state] = new_state_idx

                if (
                    self_state in self.start_states
                    and other_state in other.start_states
                ):
                    boolean_matrix_result.start_states.add(new_state)

                if (
                    self_state in self.final_states
                    and other_state in other.final_states
                ):
                    boolean_matrix_result.final_states.add(new_state)

        return boolean_matrix_result

    @classmethod
    def from_nfa(cls, nfa: EpsilonNFA) -> "BooleanMatrix":
        """Makes boolean matrix from nfa

        Args:
            nfa(EpsilonNFA): NFA that should convert to boolean matrix

        Returns:
            Representation of automaton as boolean matrix
        """
        boolean_matrix = cls()
        boolean_matrix.states_count = len(nfa.states)
        boolean_matrix.states_indices = {
            state: idx for idx, state in enumerate(nfa.states)
        }
        boolean_matrix.start_states = nfa.start_states
        boolean_matrix.final_states = nfa.final_states
        boolean_matrix.bool_matrices = boolean_matrix._create_boolean_matrix_from_nfa(
            nfa
        )
        return boolean_matrix

    def _create_boolean_matrix_from_nfa(self, nfa: EpsilonNFA) -> Dict[Any, dok_matrix]:
        """Creating mapping from labels to adj boolean matrix

        Args:
            nfa(EpsilonNFA): NFA from which mapping creating

        Returns:
            Mapping from states to indexes in boolean matrix
        """
        boolean_matrix = {}
        for state_from, transition in nfa.to_dict().items():
            for label, states_to in transition.items():
                if not isinstance(states_to, set):
                    states_to = {states_to}
                for state_to in states_to:
                    index_from = self.states_indices[state_from]
                    index_to = self.states_indices[state_to]
                    if label not in boolean_matrix:
                        boolean_matrix[label] = sparse.dok_matrix(
                            (self.states_count, self.states_count), dtype=bool
                        )
                    boolean_matrix[label][index_from, index_to] = True

        return boolean_matrix
