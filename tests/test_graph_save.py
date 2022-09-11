import filecmp
import os.path

from project import save_graph_dot, load_graph

test_resources_path = os.path.abspath("./resources/")
actual_file_path = os.sep.join([test_resources_path, "actual_graph_save.dot"])
reference_file_path = os.sep.join([test_resources_path, "reference_graph_save.dot"])


def test_graph_save_dot():
    save_graph_dot(load_graph("wc"), actual_file_path)
    assert filecmp.cmp(actual_file_path, reference_file_path)
    os.remove(actual_file_path)
