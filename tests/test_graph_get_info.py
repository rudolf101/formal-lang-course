from project import get_graph_info, load_graph, Graph


def test_get_graph_info():
    reference_graph_info = Graph(332, 269, {"D", "A"})
    graph_info = get_graph_info(load_graph("wc"))
    assert reference_graph_info == graph_info
