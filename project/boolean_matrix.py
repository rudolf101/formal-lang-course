from typing import Dict, Set, Any, List

from pyformlang.finite_automaton import State, EpsilonNFA
from scipy.sparse import dok_matrix, bmat, csr_matrix, lil_array, vstack, kron

__all__ = ["BooleanMatrix"]


class BooleanMatrix:
    """Class representing boolean adjacency matrices of NFA

    Attributes:
        state_to_index(Dict[State, int]): Dictionary of states to indices in boolean matrix
        start_states(Set[State]): NFA start states
        final_states(Set[State]): NFA final states
        bool_matrices(Dict[Any, dok_matrix]): Mapping each edge label to boolean adjacency matrix
    """

    def __init__(
        self,
        state_to_index: Dict[State, int],
        start_states: Set[State],
        final_states: Set[State],
        bool_matrices: Dict[Any, dok_matrix],
    ):
        self.state_to_index = state_to_index
        self.start_states = start_states
        self.final_states = final_states
        self.bool_matrices = bool_matrices

    def __and__(self, other: "BooleanMatrix") -> "BooleanMatrix":
        """Calculates intersection of two automatons represented by bool matrices
        Parameters
        ----------
        other : BoolMatrixAutomaton
            The automaton with which intersection will be calculated
        Returns
        -------
        intersection : BoolMatrixAutomaton
            Intersection of two automatons represented by bool matrix
        """
        inter_labels = self.bool_matrices.keys() & other.bool_matrices.keys()
        inter_bool_matrices = {
            label: kron(self.bool_matrices[label], other.bool_matrices[label])
            for label in inter_labels
        }
        inter_states_indices = dict()
        inter_start_states = set()
        inter_final_states = set()
        for self_state, self_idx in self.state_to_index.items():
            for other_state, other_idx in other.state_to_index.items():
                state = State((self_state.value, other_state.value))
                idx = self_idx * len(other.state_to_index) + other_idx
                inter_states_indices[state] = idx
                if (
                    self_state in self.start_states
                    and other_state in other.start_states
                ):
                    inter_start_states.add(state)
                if (
                    self_state in self.final_states
                    and other_state in other.final_states
                ):
                    inter_final_states.add(state)
        return BooleanMatrix(
            inter_states_indices,
            inter_start_states,
            inter_final_states,
            inter_bool_matrices,
        )

    def to_nfa(self) -> EpsilonNFA:
        """Converts boolean adjacency matrices of NFA to epsilon nfa

        Returns:
            Converted NFA
        """
        nfa = EpsilonNFA()
        for label, matrix in self.bool_matrices.items():
            matrix_as_array = dok_matrix.toarray()
            for state_from, i in self.state_to_index.items():
                for state_to, j in self.state_to_index.items():
                    if matrix_as_array[i][j]:
                        nfa.add_transitions([(state_from, label, state_to)])

        for state in self.start_states:
            nfa.add_start_state(state)
        for state in self.final_states:
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
        transitive_closure = sum(
            self.bool_matrices.values(),
            start=dok_matrix((len(self.state_to_index), len(self.state_to_index))),
        )
        cur_nnz = transitive_closure.nnz
        prev_nnz = None

        if not cur_nnz:
            return transitive_closure

        while prev_nnz != cur_nnz:
            transitive_closure += transitive_closure @ transitive_closure
            prev_nnz, cur_nnz = cur_nnz, transitive_closure.nnz

        return transitive_closure

    @classmethod
    def from_nfa(cls, nfa: EpsilonNFA) -> "BooleanMatrix":
        """Makes boolean matrix from nfa

        Args:
            nfa(EpsilonNFA): NFA that should convert to boolean matrix

        Returns:
            Representation of automaton as boolean matrix
        """
        state_to_index = {state: index for index, state in enumerate(nfa.states)}
        return cls(
            state_to_index=state_to_index,
            start_states=nfa.start_states.copy(),
            final_states=nfa.final_states.copy(),
            bool_matrices=cls._create_boolean_matrix_from_nfa(
                nfa=nfa, state_to_index=state_to_index
            ),
        )

    @staticmethod
    def _create_boolean_matrix_from_nfa(
        nfa: EpsilonNFA, state_to_index: Dict[State, int]
    ) -> Dict[Any, dok_matrix]:
        """Creating mapping from labels to adj boolean matrix

        Args:
            nfa(EpsilonNFA): NFA from which mapping creating

        Returns:
            Mapping from states to indexes in boolean matrix
        """
        boolean_matrices = dict()
        state_from_to_transition = nfa.to_dict()
        for label in nfa.symbols:
            dok_mtx = dok_matrix((len(nfa.states), len(nfa.states)), dtype=bool)
            for state_from, transitions in state_from_to_transition.items():
                states_to = transitions.get(label, set())
                if not isinstance(states_to, set):
                    states_to = {states_to}
                for state_to in states_to:
                    dok_mtx[state_to_index[state_from], state_to_index[state_to]] = True
            boolean_matrices[label] = dok_mtx
        return boolean_matrices

    def _direct_sum(self, other: "BooleanMatrix") -> "BooleanMatrix":
        """Direct sum of automatons

        Args:
            other(BooleanMatrix): The matrix with which sum will be calculated

        Returns:
            Direct sum
        """
        shifted_states_indices = {}
        for state, idx in other.state_to_index.items():
            shifted_states_indices[state] = len(self.state_to_index) + idx

        states_indices = {**self.state_to_index, **shifted_states_indices}
        start_states, final_states = (
            self.start_states | other.start_states,
            self.final_states | other.final_states,
        )

        bool_matrices = {}
        for label in self.bool_matrices.keys() & other.bool_matrices.keys():
            bool_matrices[label] = bmat(
                [[self.bool_matrices[label], None], [None, other.bool_matrices[label]]]
            )

        return BooleanMatrix(
            states_indices,
            start_states,
            final_states,
            bool_matrices,
        )

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

        if not self.state_to_index or not other.state_to_index:
            return set()

        other_states_num = len(other.state_to_index)
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

        self_index_to_state = {idx: state for state, idx in self.state_to_index.items()}
        other_index_to_state = {
            idx: state for state, idx in other.state_to_index.items()
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
                    len(other.state_to_index),
                    len(self.state_to_index) + len(other.state_to_index),
                )
            )
            for state in other.start_states:
                idx = other.state_to_index[state]
                front[idx, idx] = 1
                front[idx, len(other.state_to_index) :] = self_start_row
            return front

        if not reachable_per_node:
            start_indices = set(
                self.state_to_index[state] for state in ordered_start_states
            )
            return front_with_self_start(
                lil_array(
                    [
                        1 if index in start_indices else 0
                        for index in range(len(self.state_to_index))
                    ]
                )
            ).tocsr()

        fronts = [
            front_with_self_start(
                lil_array(
                    [
                        1 if idx == self.state_to_index[start] else 0
                        for idx in range(len(self.state_to_index))
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
                    len(other.state_to_index),
                    len(self.state_to_index) + len(other.state_to_index),
                )
            )
        )
