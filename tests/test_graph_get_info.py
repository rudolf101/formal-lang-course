from project import get_graph_info, load_graph, Graph, get_graph_info_by_name


def test_get_graph_info():
    reference_graph_info = Graph(332, 269, {"d", "a"})
    graph_info = get_graph_info(load_graph("wc"))
    assert reference_graph_info == graph_info


def test_get_graph_info_by_name():
    reference_graph_info = Graph(332, 269, {"d", "a"})
    graph_info = get_graph_info_by_name("wc")
    assert reference_graph_info == graph_info
