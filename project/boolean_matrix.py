from pyformlang.finite_automaton import State, EpsilonNFA
from scipy import sparse
from scipy.sparse import dok_matrix, bmat, csr_matrix, lil_array, vstack
from typing import Dict, Set, Any, List

__all__ = ["BooleanMatrix"]


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

    def _direct_sum(self, other: "BooleanMatrix") -> "BooleanMatrix":
        """Direct sum of automatons

        Args:
            other(BooleanMatrix): The matrix with which sum will be calculated

        Returns:
            Direct sum
        """
        shifted_state_to_idx = {}
        for state, idx in other.states_indices.items():
            shifted_state_to_idx[state] = len(self.states_indices) + idx

        states_indices = {**self.states_indices, **shifted_state_to_idx}
        start_states, final_states = (
            self.start_states | other.start_states,
            self.final_states | other.final_states,
        )

        bool_matrices = {}
        for label in self.bool_matrices.keys() & other.bool_matrices.keys():
            bool_matrices[label] = bmat(
                [[self.bool_matrices[label], None], [None, other.bool_matrices[label]]]
            )

        direct_sum = BooleanMatrix()
        direct_sum.states_count = len(states_indices)
        direct_sum.states_indices = states_indices
        direct_sum.start_states = start_states
        direct_sum.final_states = final_states
        direct_sum.bool_matrices = bool_matrices
        return direct_sum

    def sync_bfs(
        self,
        other: "BooleanMatrix",
        reachable_per_node: bool,
    ) -> Set[Any]:
        """Executes sync bfs on two automatons represented by boolean matrices

        Args:
            other(BooleanMatrix): BooleanMatrix with which bfs will be executed
            reachable_per_node(bool): Reachability for each node separately or not

        Returns:
            If reachable_per_node is false - set of reachable nodes, otherwise set of tuples (start_node, final_node)
        """

        if not self.states_indices or not other.states_indices:
            return set()

        other_states_num = len(other.states_indices)
        start_states_ordered = list(self.start_states)
        direct_sum = other._direct_sum(self)

        init_front = self._init_sync_bfs_front(
            other,
            reachable_per_node,
            start_states_ordered,
        )
        front = init_front

        visited = front.copy()
        while True:
            visited_nnz = visited.nnz
            new_front = front.copy()

            for _, matrix in direct_sum.bool_matrices.items():
                product: csr_matrix = front @ matrix
                new_front_step = lil_array(product.shape)
                for i, j in zip(*product.nonzero()):
                    if j >= other_states_num:
                        continue
                    row = product.getrow(i).tolil()[[0], other_states_num:]
                    if not row.nnz:
                        continue
                    row_shift = i // other_states_num * other_states_num
                    new_front_step[row_shift + j, j] = 1
                    new_front_step[[row_shift + j], other_states_num:] += row
                new_front += new_front_step.tocsr()

            for i, j in zip(*new_front.nonzero()):
                if visited[i, j]:
                    new_front[i, j] = 0

            visited += new_front
            front = new_front

            if visited_nnz == visited.nnz:
                break

        self_index_to_state = {idx: state for state, idx in self.states_indices.items()}
        other_index_to_state = {
            idx: state for state, idx in other.states_indices.items()
        }

        result = set()
        nonzero = set(zip(*visited.nonzero())).difference(
            set(zip(*init_front.nonzero()))
        )
        for i, j in nonzero:
            if (
                other_index_to_state[i % other_states_num] not in other.final_states
                or j < other_states_num
            ):
                continue
            self_state = self_index_to_state[j - other_states_num]
            if self_state not in self.final_states:
                continue
            result.add(
                self_state.value
                if not reachable_per_node
                else (
                    start_states_ordered[i // other_states_num].value,
                    self_state.value,
                )
            )
        return result

    def _init_sync_bfs_front(
        self,
        other: "BooleanMatrix",
        reachable_per_node: bool,
        ordered_start_states: List[State],
    ) -> csr_matrix:
        """Front for sync bfs

        Args:
            other(BooleanMatrix): BooleanMatrix with which bfs will be executed
            reachable_per_node(bool): Reachability for each node separately or not
            ordered_start_states(List[State]): List of start states
        Returns:
            Initial front for sync bfs
        """

        def front_with_self_start(self_start_row: lil_array):
            front = lil_array(
                (
                    len(other.states_indices),
                    len(self.states_indices) + len(other.states_indices),
                )
            )
            for state in other.start_states:
                idx = other.states_indices[state]
                front[idx, idx] = 1
                front[idx, len(other.states_indices) :] = self_start_row
            return front

        if not reachable_per_node:
            start_indices = set(
                self.states_indices[state] for state in ordered_start_states
            )
            return front_with_self_start(
                lil_array(
                    [
                        1 if index in start_indices else 0
                        for index in range(len(self.states_indices))
                    ]
                )
            ).tocsr()

        fronts = [
            front_with_self_start(
                lil_array(
                    [
                        1 if idx == self.states_indices[start] else 0
                        for idx in range(len(self.states_indices))
                    ]
                )
            )
            for start in ordered_start_states
        ]

        return (
            csr_matrix(vstack(fronts))
            if fronts
            else csr_matrix(
                (
                    len(other.states_indices),
                    len(self.states_indices) + len(other.states_indices),
                )
            )
        )
