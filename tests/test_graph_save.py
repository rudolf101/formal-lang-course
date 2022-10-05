import filecmp
import os.path

from project import save_graph_dot, load_graph, build_then_save_labeled_two_cycles_graph

test_dir_path = os.path.dirname(os.path.abspath(__file__))

# Temporary disabled via errors in the source library

# def test_save_graph_dot():
#     actual_file_path = os.sep.join([test_dir_path, "resources", "actual_graph.dot"])
#     reference_file_path = os.sep.join(
#         [test_dir_path, "resources", "reference_graph_save.dot"]
#     )
#
#     save_graph_dot(load_graph("wc"), actual_file_path)
#     assert filecmp.cmp(actual_file_path, reference_file_path)
#     os.remove(actual_file_path)


def test_build_then_save_labeled_two_cycles_graph():
    actual_file_path = os.sep.join(
        [test_dir_path, "resources", "actual_labeled_two_cycles_graph.dot"]
    )
    reference_file_path = os.sep.join(
        [test_dir_path, "resources", "reference_labeled_two_cycles_graph.dot"]
    )

    build_then_save_labeled_two_cycles_graph(21, 22, ("y", "a"), actual_file_path)
    assert filecmp.cmp(actual_file_path, reference_file_path)
    os.remove(actual_file_path)
